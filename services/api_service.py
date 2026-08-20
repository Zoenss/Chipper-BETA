from __future__ import annotations

from typing import Any

import requests
import streamlit as st


MOBILE_API_URL = "https://api.mobileapi.dev/devices/search/"


class MobileAPIError(Exception):
    """
    Erro específico da integração com a MobileAPI.
    """

    pass


def _obter_api_key() -> str:
    """
    Obtém a chave da MobileAPI configurada no Streamlit Secrets.
    """

    try:
        chave = st.secrets["MOBILE_API_KEY"]

    except KeyError as erro:
        raise MobileAPIError(
            "A credencial MOBILE_API_KEY não foi encontrada "
            "no arquivo .streamlit/secrets.toml."
        ) from erro

    chave = str(chave).strip()

    if not chave:
        raise MobileAPIError(
            "A credencial MOBILE_API_KEY está vazia."
        )

    return chave


def _normalizar_resposta(
    dados: dict[str, Any],
) -> dict[str, Any]:
    """
    Normaliza a resposta para o formato já utilizado
    pelo restante do CHIPPER.
    """

    dispositivos = dados.get(
        "devices",
        [],
    )

    if not isinstance(dispositivos, list):
        dispositivos = []

    return {
        "encontrado": bool(dispositivos),

        "resultados": {
            "total": dados.get(
                "total",
                len(dispositivos),
            ),

            "page": dados.get(
                "page",
                1,
            ),

            "page_size": dados.get(
                "page_size",
                len(dispositivos),
            ),

            "total_pages": dados.get(
                "total_pages",
                1,
            ),

            "devices": dispositivos,
        },

        "fonte": "MobileAPI",
    }


def buscar_dispositivo(
    nome_aparelho: str,
) -> dict[str, Any]:
    """
    Pesquisa um smartphone ou tablet pelo nome
    utilizando a MobileAPI.dev.

    Retorno esperado pelo CHIPPER:

    {
        "encontrado": True,
        "resultados": {
            "devices": [...]
        },
        "fonte": "MobileAPI"
    }
    """

    nome = str(
        nome_aparelho
    ).strip()

    if not nome:
        raise ValueError(
            "Informe o nome do equipamento."
        )

    chave = _obter_api_key()

    params = {
        "name": nome,
        "page": 1,
        "key": chave,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    try:
        resposta = requests.get(
            MOBILE_API_URL,
            params=params,
            headers=headers,
            timeout=20,
        )

    except requests.Timeout as erro:
        raise MobileAPIError(
            "A MobileAPI demorou demais para responder."
        ) from erro

    except requests.ConnectionError as erro:
        raise MobileAPIError(
            "Não foi possível conectar à MobileAPI."
        ) from erro

    except requests.RequestException as erro:
        raise MobileAPIError(
            f"Erro de comunicação com a MobileAPI: {erro}"
        ) from erro

    # --------------------------------------------------------
    # TRATAMENTO DOS STATUS HTTP
    # --------------------------------------------------------

    if resposta.status_code == 204:
        return {
            "encontrado": False,
            "resultados": {
                "devices": [],
            },
            "fonte": "MobileAPI",
        }

    if resposta.status_code == 400:
        raise MobileAPIError(
            "A MobileAPI rejeitou os parâmetros da consulta."
        )

    if resposta.status_code == 401:
        raise MobileAPIError(
            "A chave da MobileAPI é inválida ou não foi autorizada."
        )

    if resposta.status_code == 429:
        raise MobileAPIError(
            "O limite de consultas da MobileAPI foi atingido."
        )

    if resposta.status_code != 200:
        raise MobileAPIError(
            "A MobileAPI retornou HTTP "
            f"{resposta.status_code}."
        )

    try:
        dados = resposta.json()

    except ValueError as erro:
        raise MobileAPIError(
            "A MobileAPI retornou uma resposta inválida."
        ) from erro

    if not isinstance(dados, dict):
        raise MobileAPIError(
            "A MobileAPI retornou um formato inesperado."
        )

    return _normalizar_resposta(
        dados
    )


def buscar_dispositivo_por_modelo(
    modelo: str,
) -> dict[str, Any]:
    """
    Busca opcionalmente pelo número exato do modelo.

    Exemplo:
        SM-S928B
        A3520
    """

    modelo_limpo = str(
        modelo
    ).strip()

    if not modelo_limpo:
        raise ValueError(
            "Informe o número do modelo."
        )

    chave = _obter_api_key()

    params = {
        "model_number": modelo_limpo,
        "key": chave,
    }

    try:
        resposta = requests.get(
            MOBILE_API_URL,
            params=params,
            timeout=20,
        )

    except requests.RequestException as erro:
        raise MobileAPIError(
            f"Erro de conexão com a MobileAPI: {erro}"
        ) from erro

    if resposta.status_code == 204:
        return {
            "encontrado": False,
            "resultados": {
                "devices": [],
            },
            "fonte": "MobileAPI",
        }

    if resposta.status_code != 200:
        raise MobileAPIError(
            "A MobileAPI retornou HTTP "
            f"{resposta.status_code}."
        )

    try:
        dados = resposta.json()

    except ValueError as erro:
        raise MobileAPIError(
            "A MobileAPI retornou uma resposta inválida."
        ) from erro

    return _normalizar_resposta(
        dados
    )


if __name__ == "__main__":
    testes = [
        "Samsung Galaxy M55 5G",
        "iPhone 15",
    ]

    for produto in testes:
        print("=" * 60)
        print("CONSULTA:", produto)

        try:
            resultado = buscar_dispositivo(
                produto
            )

            print(
                "ENCONTRADO:",
                resultado["encontrado"],
            )

            dispositivos = resultado[
                "resultados"
            ].get(
                "devices",
                [],
            )

            for dispositivo in dispositivos[:3]:
                print()
                print(
                    "Modelo:",
                    dispositivo.get("name"),
                )
                print(
                    "Fabricante:",
                    dispositivo.get(
                        "manufacturer_name"
                    ),
                )
                print(
                    "Categoria:",
                    dispositivo.get(
                        "device_type"
                    ),
                )
                print(
                    "Confiança:",
                    dispositivo.get(
                        "match_certainty"
                    ),
                )

        except MobileAPIError as erro:
            print(
                "ERRO:",
                erro,
            )