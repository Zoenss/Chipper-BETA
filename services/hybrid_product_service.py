from __future__ import annotations

from typing import Any

from services.api_service import (
    MobileAPIError,
    buscar_detalhes_dispositivo,
    buscar_dispositivo,
)

from services.analysis_service import (
    identificar_categoria_por_nome,
)

from services.catalog_service import (
    buscar_produto_local,
)

from services.product_api_service import (
    ProductAPIError,
    buscar_produto_por_gtin,
)


def _categoria_mobile(categoria: str) -> bool:
    return categoria in {
        "phone",
        "tablet",
    }


def _pontuacao_match(valor: Any) -> float:
    if valor is None:
        return -1.0
    texto = str(valor).strip().replace("%", "")
    try:
        return float(texto)
    except (TypeError, ValueError):
        return -1.0


def _normalizar_dados_mobile(dados: dict[str, Any]) -> dict[str, Any]:
    normalizados = dict(dados)

    if not normalizados.get("manufacturer_name"):
        marca = normalizados.get("brand") or normalizados.get("manufacturer")
        if isinstance(marca, dict):
            nome_marca = marca.get("name")
            if nome_marca:
                normalizados["manufacturer_name"] = str(nome_marca)
        elif marca:
            normalizados["manufacturer_name"] = str(marca)

    return normalizados


def _resumo_mobile(
    consulta: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Converte a resposta da MobileAPI para um formato
    mais simples para o orquestrador híbrido.
    """

    if not consulta:
        return None

    if not consulta.get("encontrado"):
        return None

    resultados = consulta.get(
        "resultados",
        {},
    )

    if not isinstance(resultados, dict):
        return None

    dispositivos = resultados.get(
        "devices",
        [],
    )

    if not isinstance(dispositivos, list):
        return None

    if not dispositivos:
        return None

    melhor = max(
        dispositivos,
        key=lambda item: _pontuacao_match(
            item.get("match_certainty")
            if isinstance(item, dict)
            else None
        ),
    )

    if not isinstance(melhor, dict):
        return None

    return {
        "encontrado": True,
        "fonte": "MobileAPI",
        "dados": _normalizar_dados_mobile(melhor),
    }


def resolver_produto_hibrido(
    nome_produto: str,
) -> dict[str, Any]:
    """
    Orquestra as fontes de identificação do CHIPPER.

    Fluxo:

    1. Identifica categoria pelo motor interno.
    2. Consulta catálogo local.
    3. Se for smartphone/tablet, tenta MobileAPI.
    4. Quando a MobileAPI retorna um ID, busca a ficha detalhada.
    5. Se o catálogo tiver GTIN, tenta Icecat.
    6. Se nenhuma API localizar, mantém os dados
       do catálogo local e do motor interno.

    A função não impede a análise caso uma API falhe.
    """

    nome = str(
        nome_produto
    ).strip()

    if not nome:
        raise ValueError(
            "Informe o nome do equipamento."
        )

    categoria_interna = (
        identificar_categoria_por_nome(
            nome
        )
    )

    produto_local = buscar_produto_local(
        nome
    )

    resultado: dict[str, Any] = {
        "encontrado": False,
        "nome_informado": nome,
        "categoria_interna": categoria_interna,
        "categoria_final": categoria_interna,
        "fonte_principal": "Motor interno do CHIPPER",
        "catalogo_local": produto_local,
        "mobileapi": None,
        "icecat": None,
        "fontes_utilizadas": [],
        "erros": [],
    }

    # ========================================================
    # CATÁLOGO LOCAL
    # ========================================================

    if produto_local:
        resultado["fontes_utilizadas"].append("Catálogo local")

        categoria_catalogo = produto_local.get("categoria")
        if categoria_catalogo:
            resultado["categoria_final"] = str(categoria_catalogo)

        resultado["fonte_principal"] = "Catálogo local"
        resultado["encontrado"] = True

    # ========================================================
    # MOBILE API
    # ========================================================

    categoria_para_mobile = resultado.get(
        "categoria_final",
        categoria_interna,
    )

    deve_tentar_mobile = (
        _categoria_mobile(str(categoria_para_mobile))
        or str(categoria_para_mobile) == "desconhecido"
    )

    if deve_tentar_mobile:
        try:
            consulta_mobile = buscar_dispositivo(nome)
            resumo_mobile = _resumo_mobile(consulta_mobile)

            if resumo_mobile:
                dados_mobile = resumo_mobile.get("dados", {})

                if isinstance(dados_mobile, dict):
                    dispositivo_id = dados_mobile.get("id")
                    if dispositivo_id:
                        try:
                            detalhes = buscar_detalhes_dispositivo(dispositivo_id)
                            if isinstance(detalhes, dict):
                                dados_enriquecidos = dict(dados_mobile)
                                dados_enriquecidos.update(detalhes)
                                resumo_mobile["dados"] = _normalizar_dados_mobile(
                                    dados_enriquecidos
                                )
                        except MobileAPIError as erro:
                            resultado["erros"].append(
                                f"MobileAPI detalhes: {erro}"
                            )

                resultado["mobileapi"] = resumo_mobile
                resultado["fontes_utilizadas"].append("MobileAPI")
                resultado["fonte_principal"] = "MobileAPI"
                resultado["encontrado"] = True

                dados_mobile_final = resumo_mobile.get("dados", {})
                categoria_mobile = (
                    dados_mobile_final.get("device_type")
                    if isinstance(dados_mobile_final, dict)
                    else None
                )

                if categoria_mobile:
                    resultado["categoria_final"] = str(categoria_mobile)

        except MobileAPIError as erro:
            resultado["erros"].append(
                f"MobileAPI: {erro}"
            )

        except Exception as erro:
            resultado["erros"].append(
                "MobileAPI: "
                f"{type(erro).__name__}"
            )

    # ========================================================
    # ICECAT
    # ========================================================

    if produto_local:
        gtin = produto_local.get("gtin")

        if gtin:
            try:
                resultado_icecat = buscar_produto_por_gtin(str(gtin))
                resultado["icecat"] = resultado_icecat

                if resultado_icecat.get("encontrado"):
                    resultado["fontes_utilizadas"].append("Icecat")
                    resultado["fonte_principal"] = "Icecat"
                    resultado["encontrado"] = True

                    categoria_icecat = resultado_icecat.get("categoria_chipper")
                    if categoria_icecat and categoria_icecat != "desconhecido":
                        resultado["categoria_final"] = str(categoria_icecat)

            except ProductAPIError as erro:
                resultado["erros"].append(
                    f"Icecat: {erro}"
                )

            except Exception as erro:
                resultado["erros"].append(
                    "Icecat: "
                    f"{type(erro).__name__}"
                )

    # ========================================================
    # FALLBACK FINAL
    # ========================================================

    if not resultado["fontes_utilizadas"]:
        resultado["fontes_utilizadas"].append(
            "Motor interno do CHIPPER"
        )

    if resultado.get("categoria_final") in {None, ""}:
        resultado["categoria_final"] = "desconhecido"

    return resultado
