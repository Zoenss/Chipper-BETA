from __future__ import annotations

from typing import Any

import requests
import streamlit as st


UPC_SEARCH_URL = "https://api.upcitemdb.com/prod/trial/search"
UPC_LOOKUP_URL = "https://api.upcitemdb.com/prod/trial/lookup"


class UPCItemDBError(Exception):
    """Erro específico da integração com UPCitemdb."""

    pass


def _normalizar_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "encontrado": True,
        "fonte": "UPCitemdb",
        "titulo": item.get("title"),
        "fabricante": item.get("brand"),
        "modelo": item.get("model"),
        "gtin": item.get("gtin") or item.get("ean") or item.get("upc"),
        "ean": item.get("ean"),
        "upc": item.get("upc"),
        "categoria": item.get("category"),
        "peso": item.get("weight"),
        "dimensoes": item.get("dimension"),
        "descricao": item.get("description"),
        "imagens": item.get("images") if isinstance(item.get("images"), list) else [],
        "dados_brutos": item,
    }


def _tratar_resposta(resposta: requests.Response, contexto: str) -> dict[str, Any]:
    if resposta.status_code == 404:
        return {
            "encontrado": False,
            "fonte": "UPCitemdb",
            "erro": "Produto não localizado no UPCitemdb.",
        }
    if resposta.status_code == 429:
        raise UPCItemDBError(
            "O limite gratuito do UPCitemdb foi atingido ou as consultas estão rápidas demais."
        )
    if resposta.status_code == 400:
        raise UPCItemDBError(
            f"O UPCitemdb rejeitou os parâmetros da consulta ({contexto})."
        )
    if resposta.status_code != 200:
        raise UPCItemDBError(
            f"UPCitemdb retornou HTTP {resposta.status_code} durante {contexto}."
        )

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise UPCItemDBError("UPCitemdb retornou uma resposta inválida.") from erro

    if not isinstance(dados, dict):
        raise UPCItemDBError("UPCitemdb retornou um formato inesperado.")

    itens = dados.get("items", [])
    if not isinstance(itens, list) or not itens:
        return {
            "encontrado": False,
            "fonte": "UPCitemdb",
            "erro": "Produto não localizado no UPCitemdb.",
        }

    primeiro = itens[0]
    if not isinstance(primeiro, dict):
        return {
            "encontrado": False,
            "fonte": "UPCitemdb",
            "erro": "Produto não localizado no UPCitemdb.",
        }

    resultado = _normalizar_item(primeiro)
    resultado["total_resultados"] = dados.get("total", len(itens))
    return resultado


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_produto_por_nome(nome: str) -> dict[str, Any]:
    """Busca um produto por texto no plano trial do UPCitemdb."""

    consulta = str(nome).strip()
    if not consulta:
        raise ValueError("Informe o nome do produto.")

    try:
        resposta = requests.get(
            UPC_SEARCH_URL,
            params={
                "s": consulta,
                "type": "product",
                "match_mode": 0,
            },
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
            },
            timeout=20,
        )
    except requests.Timeout as erro:
        raise UPCItemDBError("A consulta ao UPCitemdb demorou demais para responder.") from erro
    except requests.RequestException as erro:
        raise UPCItemDBError(f"Erro de comunicação com UPCitemdb: {erro}") from erro

    return _tratar_resposta(resposta, "busca por nome")


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_produto_por_gtin(gtin: str) -> dict[str, Any]:
    """Consulta UPC/EAN/GTIN exato no UPCitemdb."""

    codigo = str(gtin).strip()
    if not codigo:
        raise ValueError("Informe um GTIN/EAN/UPC válido.")

    try:
        resposta = requests.get(
            UPC_LOOKUP_URL,
            params={"upc": codigo},
            headers={
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
            },
            timeout=20,
        )
    except requests.Timeout as erro:
        raise UPCItemDBError("A consulta ao UPCitemdb demorou demais para responder.") from erro
    except requests.RequestException as erro:
        raise UPCItemDBError(f"Erro de comunicação com UPCitemdb: {erro}") from erro

    return _tratar_resposta(resposta, "consulta por GTIN")
