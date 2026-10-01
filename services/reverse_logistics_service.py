from __future__ import annotations

import math
from typing import Any

import requests
import streamlit as st

from services.geo_service import (
    GeoServiceError,
    geoapify_disponivel,
    geocodificar_geoapify,
)


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URLS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.nchc.org.tw/api/interpreter",
)
USER_AGENT = "CHIPPER-Reverse-Logistics/alpha"


class ReverseLogisticsError(RuntimeError):
    pass


def _distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    raio = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * raio * math.asin(math.sqrt(a))


def _geocodificar_nominatim(consulta: str) -> dict[str, Any]:
    try:
        resposta = requests.get(
            NOMINATIM_URL,
            params={
                "q": f"{consulta}, Brasil",
                "format": "jsonv2",
                "limit": 1,
                "countrycodes": "br",
            },
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.Timeout as erro:
        raise ReverseLogisticsError("A busca da localidade demorou demais para responder.") from erro
    except requests.RequestException as erro:
        raise ReverseLogisticsError("Não foi possível consultar a localização informada.") from erro
    except ValueError as erro:
        raise ReverseLogisticsError("A resposta de localização veio em formato inválido.") from erro

    if not isinstance(dados, list) or not dados:
        raise ReverseLogisticsError("Cidade ou CEP não localizado.")

    primeiro = dados[0]
    try:
        latitude = float(primeiro["lat"])
        longitude = float(primeiro["lon"])
    except (KeyError, TypeError, ValueError) as erro:
        raise ReverseLogisticsError("Não foi possível obter as coordenadas da localidade.") from erro

    return {
        "latitude": latitude,
        "longitude": longitude,
        "nome": str(primeiro.get("display_name") or consulta),
        "fonte_geocodificacao": "OpenStreetMap / Nominatim",
    }


@st.cache_data(ttl=3600, show_spinner=False)
def geocodificar_local(local: str) -> dict[str, Any]:
    consulta = str(local).strip()
    if not consulta:
        raise ReverseLogisticsError("Informe uma cidade ou CEP.")

    # Geoapify é o provedor principal quando a chave estiver configurada.
    # Em qualquer falha, o fluxo permanece resiliente pelo Nominatim.
    if geoapify_disponivel():
        try:
            return geocodificar_geoapify(consulta)
        except GeoServiceError:
            pass

    return _geocodificar_nominatim(consulta)


def _endereco(tags: dict[str, Any]) -> str:
    rua = tags.get("addr:street") or tags.get("addr:place")
    numero = tags.get("addr:housenumber")
    bairro = tags.get("addr:suburb") or tags.get("addr:neighbourhood")
    cidade = tags.get("addr:city") or tags.get("addr:municipality")

    partes: list[str] = []
    if rua:
        texto_rua = str(rua)
        if numero:
            texto_rua += f", {numero}"
        partes.append(texto_rua)
    if bairro:
        partes.append(str(bairro))
    if cidade:
        partes.append(str(cidade))

    return " - ".join(partes) if partes else "Endereço não informado no OpenStreetMap"


def _consultar_overpass(query: str) -> dict[str, Any]:
    ultimo_erro: Exception | None = None

    for url in OVERPASS_URLS:
        try:
            resposta = requests.post(
                url,
                data={"data": query},
                headers={"User-Agent": USER_AGENT},
                timeout=20,
            )
            resposta.raise_for_status()
            dados = resposta.json()

            if not isinstance(dados, dict):
                raise ValueError("Resposta Overpass fora do formato esperado.")

            return dados
        except (requests.RequestException, ValueError) as erro:
            ultimo_erro = erro
            continue

    raise ReverseLogisticsError(
        "Não foi possível consultar os pontos de descarte agora. "
        "Os servidores públicos de consulta estão indisponíveis ou sobrecarregados."
    ) from ultimo_erro


@st.cache_data(ttl=1800, show_spinner=False)
def buscar_pontos_eletroeletronicos(
    latitude: float,
    longitude: float,
    raio_m: int = 20000,
) -> list[dict[str, Any]]:
    query = f"""
    [out:json][timeout:25];
    (
      nwr(around:{raio_m},{latitude},{longitude})["amenity"="recycling"]["recycling:electrical_appliances"="yes"];
      nwr(around:{raio_m},{latitude},{longitude})["amenity"="recycling"]["recycling:electronics"="yes"];
      nwr(around:{raio_m},{latitude},{longitude})["recycling:electrical_appliances"="yes"];
      nwr(around:{raio_m},{latitude},{longitude})["recycling:electronics"="yes"];
      nwr(around:{raio_m},{latitude},{longitude})["waste"="electrical_appliances"];
    );
    out center tags;
    """

    dados = _consultar_overpass(query)

    elementos = dados.get("elements", []) if isinstance(dados, dict) else []
    resultados: list[dict[str, Any]] = []
    vistos: set[tuple[str, str]] = set()

    for elemento in elementos:
        if not isinstance(elemento, dict):
            continue

        tags = elemento.get("tags", {})
        if not isinstance(tags, dict):
            tags = {}

        lat = elemento.get("lat")
        lon = elemento.get("lon")
        centro = elemento.get("center")
        if (lat is None or lon is None) and isinstance(centro, dict):
            lat = centro.get("lat")
            lon = centro.get("lon")

        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except (TypeError, ValueError):
            continue

        nome = str(
            tags.get("name")
            or tags.get("operator")
            or tags.get("brand")
            or "Ponto de reciclagem de eletroeletrônicos"
        )
        endereco = _endereco(tags)
        chave = (nome.lower(), endereco.lower())
        if chave in vistos:
            continue
        vistos.add(chave)

        resultados.append(
            {
                "nome": nome,
                "endereco": endereco,
                "latitude": lat_f,
                "longitude": lon_f,
                "distancia_km": _distancia_km(latitude, longitude, lat_f, lon_f),
                "operador": str(tags.get("operator") or "Não informado"),
                "telefone": str(tags.get("phone") or tags.get("contact:phone") or "Não informado"),
                "fonte": "OpenStreetMap / Overpass",
            }
        )

    resultados.sort(key=lambda item: float(item["distancia_km"]))
    return resultados[:20]
