"""Consulta complementar de GTIN ao upc.dev. Não confirma correspondência apenas por nome."""
from __future__ import annotations
import re
from typing import Any
import requests
import streamlit as st


class UPCDevError(Exception):
    pass


@st.cache_data(ttl=86400, show_spinner=False)
def buscar_gtin_upcdev(gtin: str) -> dict[str, Any]:
    codigo = str(gtin).strip()
    if not re.fullmatch(r"\d{8}|\d{12,14}", codigo):
        raise ValueError("GTIN deve ter 8, 12, 13 ou 14 dígitos.")
    try:
        resposta = requests.get(
            f"https://upc.dev/v1/product/{codigo}",
            headers={"Accept": "application/json", "User-Agent": "CYPHER-TCC/1.0 (academic project)"},
            timeout=(3, 7),
        )
    except requests.RequestException as erro:
        raise UPCDevError("Não foi possível consultar a API secundária.") from erro
    if resposta.status_code in (404, 204):
        return {"encontrado": False, "fonte": "upc.dev"}
    if resposta.status_code == 429:
        raise UPCDevError("Limite gratuito diário do upc.dev atingido.")
    if resposta.status_code != 200:
        raise UPCDevError(f"upc.dev retornou HTTP {resposta.status_code}.")
    try:
        corpo = resposta.json()
    except ValueError as erro:
        raise UPCDevError("Resposta inválida do upc.dev.") from erro
    if not isinstance(corpo, dict):
        raise UPCDevError("Formato inesperado do upc.dev.")
    item = corpo.get("data", corpo)
    if not isinstance(item, dict):
        return {"encontrado": False, "fonte": "upc.dev"}
    retornado = str(item.get("upc") or item.get("gtin") or item.get("ean") or "")
    # Comprovação por identificador: não aceitar outro código como resultado.
    if retornado != codigo:
        return {"encontrado": False, "fonte": "upc.dev", "aviso": "GTIN não confirmado"}
    return {
        "encontrado": True, "fonte": "upc.dev", "gtin": codigo,
        "titulo": item.get("name") or item.get("title"),
        "fabricante": item.get("brand"), "modelo": item.get("model"),
    }
