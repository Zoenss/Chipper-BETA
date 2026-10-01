from __future__ import annotations

from typing import Any

import requests
import streamlit as st


ICECAT_API_URL = "https://live.icecat.biz/api"


class ProductAPIError(Exception):
    """Erro específico da integração com o Icecat."""

    pass


def _get_icecat_credentials() -> tuple[str, str]:
    try:
        token = st.secrets["ICECAT_API_KEY"]
        username = st.secrets["ICECAT_USERNAME"]
    except KeyError as erro:
        raise ProductAPIError(
            f"Credencial Icecat não encontrada: {erro}"
        ) from erro

    token_texto = str(token).strip()
    username_texto = str(username).strip()

    if not token_texto or not username_texto:
        raise ProductAPIError(
            "As credenciais do Icecat estão vazias."
        )

    return token_texto, username_texto


def _extrair_features(dados: dict[str, Any]) -> dict[str, Any]:
    """Converte os grupos de especificações do Icecat em dicionário simples."""

    resultado: dict[str, Any] = {}
    grupos = dados.get("FeaturesGroups", [])

    if not isinstance(grupos, list):
        return resultado

    for grupo in grupos:
        if not isinstance(grupo, dict):
            continue

        features = grupo.get("Features", [])
        if not isinstance(features, list):
            continue

        for feature in features:
            if not isinstance(feature, dict):
                continue

            info_feature = feature.get("Feature", {})
            if not isinstance(info_feature, dict):
                continue

            nome_info = info_feature.get("Name", {})
            nome = (
                nome_info.get("Value")
                if isinstance(nome_info, dict)
                else nome_info
            )

            valor = (
                feature.get("PresentationValue")
                or feature.get("LocalValue")
                or feature.get("RawValue")
                or feature.get("Value")
            )

            if nome and valor is not None:
                resultado[str(nome)] = valor

    return resultado


def _extrair_peso(especificacoes: dict[str, Any]) -> str | None:
    candidatos = [
        "Weight",
        "Package weight",
        "Product weight",
        "Net weight",
    ]

    for chave in candidatos:
        valor = especificacoes.get(chave)
        if valor:
            return str(valor)

    return None


def _normalizar_categoria(
    categoria_icecat: str | None,
    nome_produto: str | None,
) -> str:
    texto = " ".join(
        [
            str(categoria_icecat or ""),
            str(nome_produto or ""),
        ]
    ).lower()

    regras = {
        "notebook": [
            "notebook",
            "laptop",
            "mobile workstation",
            "chromebook",
        ],
        "desktop": [
            "desktop",
            "pc/workstation",
            "workstation",
            "personal computer",
            "mini pc",
        ],
        "monitor": [
            "monitor",
            "computer monitor",
            "display",
        ],
        "console": [
            "game console",
            "gaming console",
            "playstation",
            "xbox",
            "nintendo",
        ],
        "tablet": ["tablet"],
        "phone": ["smartphone", "mobile phone"],
    }

    for categoria, termos in regras.items():
        if any(termo in texto for termo in termos):
            return categoria

    return "desconhecido"


def _normalizar_resposta(resposta: dict[str, Any]) -> dict[str, Any]:
    """Transforma o JSON bruto do Icecat em formato simples para o CHIPPER."""

    dados = resposta.get("data")

    if not isinstance(dados, dict):
        return {
            "encontrado": False,
            "fonte": "Icecat",
            "erro": "Resposta sem dados de produto.",
        }

    geral = dados.get("GeneralInfo", {})
    if not isinstance(geral, dict):
        geral = {}

    especificacoes = _extrair_features(dados)

    nome_produto = (
        geral.get("ProductName")
        or geral.get("Title")
        or "Produto não identificado"
    )

    brand_info = geral.get("BrandInfo", {})
    fabricante = geral.get("Brand")
    if not fabricante and isinstance(brand_info, dict):
        fabricante = brand_info.get("BrandName")
    fabricante = fabricante or "Não informado"

    categoria_info = geral.get("Category", {})
    categoria_original = None

    if isinstance(categoria_info, dict):
        nome_categoria = categoria_info.get("Name", {})
        if isinstance(nome_categoria, dict):
            categoria_original = nome_categoria.get("Value")
        elif nome_categoria:
            categoria_original = str(nome_categoria)

    categoria_chipper = _normalizar_categoria(
        categoria_original,
        nome_produto,
    )

    gtins = geral.get("GTIN", [])
    if isinstance(gtins, str):
        gtins = [gtins]
    elif not isinstance(gtins, list):
        gtins = []

    imagem = dados.get("Image", {})
    imagem_url = None
    if isinstance(imagem, dict):
        imagem_url = (
            imagem.get("HighPic")
            or imagem.get("Pic500x500")
            or imagem.get("LowPic")
        )

    descricao = geral.get("Description", {})
    descricao_longa = None
    if isinstance(descricao, dict):
        descricao_longa = descricao.get("LongDesc")

    return {
        "encontrado": True,
        "fonte": "Icecat",
        "icecat_id": geral.get("IcecatId"),
        "fabricante": fabricante,
        "modelo": nome_produto,
        "codigo_fabricante": geral.get("BrandPartCode"),
        "categoria_original": categoria_original,
        "categoria_chipper": categoria_chipper,
        "gtin": gtins,
        "peso": _extrair_peso(especificacoes),
        "imagem_url": imagem_url,
        "descricao": descricao_longa,
        "especificacoes": especificacoes,
        "dados_brutos": dados,
    }


def _consultar_icecat(
    identificadores: dict[str, str],
    idioma: str,
) -> dict[str, Any]:
    token, username = _get_icecat_credentials()

    headers = {
        "api-token": token,
    }

    params = {
        "lang": idioma,
        "shopname": username,
        "content": "",
        **identificadores,
    }

    try:
        resposta = requests.get(
            ICECAT_API_URL,
            headers=headers,
            params=params,
            timeout=20,
        )
    except requests.Timeout as erro:
        raise ProductAPIError(
            "A consulta ao Icecat demorou demais para responder."
        ) from erro
    except requests.RequestException as erro:
        raise ProductAPIError(
            f"Erro de conexão com Icecat: {erro}"
        ) from erro

    if resposta.status_code == 401:
        raise ProductAPIError(
            "As credenciais do Icecat não foram autorizadas."
        )
    if resposta.status_code == 429:
        raise ProductAPIError(
            "O limite de consultas do Icecat foi atingido."
        )
    if resposta.status_code != 200:
        raise ProductAPIError(
            "Icecat retornou HTTP "
            f"{resposta.status_code}: "
            f"{resposta.text[:300]}"
        )

    try:
        dados = resposta.json()
    except ValueError as erro:
        raise ProductAPIError(
            "Icecat retornou uma resposta inválida."
        ) from erro

    if not isinstance(dados, dict):
        raise ProductAPIError(
            "Icecat retornou um formato inesperado."
        )

    if dados.get("msg") != "OK":
        return {
            "encontrado": False,
            "fonte": "Icecat",
            "erro": dados.get("msg", "Produto não localizado."),
        }

    return _normalizar_resposta(dados)


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_produto_por_gtin(
    gtin: str,
    idioma: str = "EN",
) -> dict[str, Any]:
    """Busca um produto no Icecat pelo GTIN/EAN/UPC."""

    gtin_limpo = str(gtin).strip()
    if not gtin_limpo:
        raise ValueError("Informe um GTIN/EAN/UPC válido.")

    return _consultar_icecat(
        {"GTIN": gtin_limpo},
        idioma,
    )


@st.cache_data(ttl=3600, show_spinner=False)
def buscar_produto_por_marca_codigo(
    marca: str,
    codigo_fabricante: str,
    idioma: str = "EN",
) -> dict[str, Any]:
    """Busca no Icecat por fabricante + código/MPN do produto."""

    marca_limpa = str(marca).strip()
    codigo_limpo = str(codigo_fabricante).strip()

    if not marca_limpa or not codigo_limpo:
        raise ValueError(
            "Informe fabricante e código do produto para consultar o Icecat."
        )

    return _consultar_icecat(
        {
            "Brand": marca_limpa,
            "ProductCode": codigo_limpo,
        },
        idioma,
    )
