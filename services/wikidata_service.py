"""Consulta complementar ao Wikidata por nome/modelo, sem chave de API."""
from __future__ import annotations

import re
import unicodedata
from typing import Any

import requests
import streamlit as st

URL = "https://www.wikidata.org/w/api.php"
HEADERS = {
    "User-Agent": "CYPHER-TCC/1.0 (https://github.com/Zoenss/Chipper-BETA)",
    "Accept": "application/json",
}


class WikidataError(Exception):
    """Falha de rede, limite ou formato inesperado."""


def _normalizar(texto: str) -> list[str]:
    texto = unicodedata.normalize("NFKD", str(texto).lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.findall(r"[a-z]+\d+[a-z\d]*|\d+|[a-z]+", texto)


def modelo_compativel(consulta: str, nome_candidato: str) -> bool:
    """Aceita modelos com código exato; recusa M55 quando resultado é M55s."""
    a = _normalizar(consulta)
    b = _normalizar(nome_candidato)
    codigos_a = [v for v in a if any(c.isdigit() for c in v)]
    codigos_b = [v for v in b if any(c.isdigit() for c in v)]
    if not codigos_a or codigos_a != codigos_b:
        return False
    # Não aceitar correspondência de um produto de outra marca.
    marcas = {"samsung", "apple", "xiaomi", "motorola", "lenovo", "dell", "acer",
              "asus", "sony", "nintendo", "microsoft", "lg", "hp"}
    marcas_a = marcas.intersection(a)
    marcas_b = marcas.intersection(b)
    if marcas_a and marcas_b and not marcas_a.intersection(marcas_b):
        return False
    # Tokens não numéricos úteis da consulta devem aparecer no nome encontrado.
    ignorar = marcas | {"galaxy", "smartphone", "celular", "tablet", "modelo"}
    importantes = {v for v in a if v not in ignorar and not any(c.isdigit() for c in v)}
    if importantes and not importantes.issubset(set(b)):
        return False
    return True


def selecionar_resultado(consulta: str, resultados: list[dict[str, Any]]) -> dict[str, Any]:
    """Não escolhe o primeiro resultado por similaridade aproximada."""
    for item in resultados:
        if not isinstance(item, dict):
            continue
        titulo = str(item.get("label") or "")
        aliases = [str(x) for x in item.get("aliases", []) if isinstance(x, str)]
        if any(modelo_compativel(consulta, v) for v in [titulo, *aliases]):
            qid = str(item.get("id") or "")
            if re.fullmatch(r"Q\d+", qid):
                return {
                    "encontrado": True,
                    "fonte": "Wikidata",
                    "nome": titulo,
                    "id": qid,
                    "descricao": str(item.get("description") or ""),
                    "url": f"https://www.wikidata.org/wiki/{qid}",
                    "aviso": "Identificação complementar; ficha técnica não verificada.",
                }
    return {"encontrado": False, "fonte": "Wikidata"}


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_modelo_wikidata(consulta: str) -> dict[str, Any]:
    nome = " ".join(str(consulta).split())
    if len(nome) < 3 or len(nome) > 120:
        raise ValueError("Informe nome/modelo entre 3 e 120 caracteres.")
    try:
        r = requests.get(
            URL,
            params={"action": "wbsearchentities", "search": nome, "language": "en",
                    "uselang": "pt", "type": "item", "limit": 10, "format": "json"},
            headers=HEADERS, timeout=(3, 7),
        )
    except requests.RequestException as exc:
        raise WikidataError("Wikidata indisponível ou sem conexão.") from exc
    if r.status_code == 429:
        raise WikidataError("Wikidata limitou as consultas; tente novamente mais tarde.")
    if r.status_code != 200:
        raise WikidataError(f"Wikidata respondeu HTTP {r.status_code}.")
    try:
        data = r.json()
    except ValueError as exc:
        raise WikidataError("Wikidata retornou JSON inválido.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("search"), list):
        raise WikidataError("Formato inesperado de resposta do Wikidata.")
    return selecionar_resultado(nome, data["search"])
