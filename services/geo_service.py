from __future__ import annotations

from typing import Any

import requests
import streamlit as st


GEOAPIFY_GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"


class GeoServiceError(Exception):
    """Erro específico do provedor de geocodificação."""

    pass


def geoapify_disponivel() -> bool:
    """Informa se uma chave Geoapify foi configurada nos Secrets."""

    try:
        valor = st.secrets.get("GEOAPIFY_API_KEY")
    except Exception:
        return False
    return bool(str(valor or "").strip())


def _obter_chave() -> str:
    try:
        valor = st.secrets.get("GEOAPIFY_API_KEY")
    except Exception as erro:
        raise GeoServiceError("Geoapify não está configurado.") from erro

    chave = str(valor or "").strip()
    if not chave:
        raise GeoServiceError("Geoapify não está configurado.")
    return chave


@st.cache_data(ttl=3600, show_spinner=False)
def geocodificar_geoapify(local: str) -> dict[str, Any]:
    """Geocodifica endereço, cidade ou CEP brasileiro usando Geoapify."""

    consulta = str(local).strip()
    if not consulta:
        raise ValueError("Informe uma cidade, endereço ou CEP.")

    chave = _obter_chave()

    try:
        resposta = requests.get(
            GEOAPIFY_GEOCODING_URL,
            params={
                "text": f"{consulta}, Brasil",
                "filter": "countrycode:br",
                "limit": 1,
                "format": "json",
                "lang": "pt",
                "apiKey": chave,
            },
            timeout=15,
        )
    except requests.Timeout as erro:
        raise GeoServiceError("A consulta ao Geoapify demorou demais para responder.") from erro
    except requests.RequestException as erro:
        raise GeoServiceError(f"Erro de comunicação com Geoapify: {erro}") from erro

    if resposta.status_code == 401:
        raise GeoServiceError("A chave do Geoapify não foi autorizada.")
    if resposta.status_code == 429:
        raise GeoServiceError("O limite de consultas do Geoapify foi atingido.")
    if resposta.status_code != 200:
        raise GeoServiceError(
            f"Geoapify retornou HTTP {resposta.status_code}."
        )

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise GeoServiceError("Geoapify retornou uma resposta inválida.") from erro

    resultados = dados.get("results", []) if isinstance(dados, dict) else []
    if not isinstance(resultados, list) or not resultados:
        raise GeoServiceError("Localidade não encontrada pelo Geoapify.")

    primeiro = resultados[0]
    if not isinstance(primeiro, dict):
        raise GeoServiceError("Geoapify retornou um formato inesperado.")

    try:
        latitude = float(primeiro["lat"])
        longitude = float(primeiro["lon"])
    except (KeyError, TypeError, ValueError) as erro:
        raise GeoServiceError("Geoapify não retornou coordenadas válidas.") from erro

    return {
        "latitude": latitude,
        "longitude": longitude,
        "nome": str(
            primeiro.get("formatted")
            or primeiro.get("address_line1")
            or consulta
        ),
        "fonte_geocodificacao": "Geoapify",
    }
