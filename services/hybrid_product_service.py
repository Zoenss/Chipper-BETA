from __future__ import annotations

import re
from typing import Any

from services.api_service import (
    MobileAPIError,
    buscar_detalhes_dispositivo,
    buscar_dispositivo,
)
from services.analysis_service import identificar_categoria_por_nome
from services.catalog_service import buscar_produto_local
from services.product_api_service import (
    ProductAPIError,
    buscar_produto_por_gtin,
    buscar_produto_por_marca_codigo,
)
from services.upc_service import UPCItemDBError, buscar_produto_por_nome as buscar_upc_por_nome


def _categoria_mobile(categoria: str) -> bool:
    return categoria in {"phone", "tablet"}


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


def _mobile_precisa_detalhes(dados: dict[str, Any]) -> bool:
    """Evita uma segunda chamada quando a busca já trouxe ficha útil."""

    campos_tecnicos = (
        "weight",
        "battery_capacity",
        "release_date",
        "storage",
        "screen_resolution",
        "hardware",
    )
    preenchidos = sum(
        1
        for campo in campos_tecnicos
        if dados.get(campo) not in {None, "", [], {}}
    )

    # Se ao menos quatro campos já vieram na busca, preservamos créditos.
    return preenchidos < 4


def _resumo_mobile(
    consulta: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not consulta or not consulta.get("encontrado"):
        return None

    resultados = consulta.get("resultados", {})
    if not isinstance(resultados, dict):
        return None

    dispositivos = resultados.get("devices", [])
    if not isinstance(dispositivos, list) or not dispositivos:
        return None

    melhor = max(
        dispositivos,
        key=lambda item: _pontuacao_match(
            item.get("match_certainty") if isinstance(item, dict) else None
        ),
    )

    if not isinstance(melhor, dict):
        return None

    return {
        "encontrado": True,
        "fonte": "MobileAPI",
        "dados": _normalizar_dados_mobile(melhor),
    }


def _inferir_marca_codigo(nome: str) -> tuple[str | None, str | None]:
    texto = " ".join(str(nome).strip().split())
    if not texto:
        return None, None

    palavras = texto.split()
    primeiro = palavras[0]
    primeiro_lower = primeiro.lower()

    aliases = {
        "asus": "ASUS",
        "acer": "Acer",
        "dell": "Dell",
        "lenovo": "Lenovo",
        "hp": "HP",
        "samsung": "Samsung",
        "lg": "LG",
        "sony": "Sony",
        "playstation": "Sony",
        "xbox": "Microsoft",
        "microsoft": "Microsoft",
        "nintendo": "Nintendo",
        "aoc": "AOC",
        "philips": "Philips",
        "msi": "MSI",
        "gigabyte": "Gigabyte",
        "apple": "Apple",
        "motorola": "Motorola",
        "xiaomi": "Xiaomi",
    }

    marca = aliases.get(primeiro_lower, primeiro)

    candidatos: list[str] = []
    for token in reversed(palavras[1:]):
        limpo = token.strip("(),;:/\"")
        if not limpo:
            continue
        if re.search(r"[A-Za-z]", limpo) and re.search(r"\d", limpo):
            candidatos.append(limpo)

    codigo = candidatos[0] if candidatos else None
    return marca, codigo


def _aplicar_icecat(
    resultado: dict[str, Any],
    resultado_icecat: dict[str, Any],
) -> None:
    resultado["icecat"] = resultado_icecat

    if not resultado_icecat.get("encontrado"):
        erro = resultado_icecat.get("erro")
        if erro:
            resultado["erros"].append(f"Icecat: {erro}")
        return

    if "Icecat" not in resultado["fontes_utilizadas"]:
        resultado["fontes_utilizadas"].append("Icecat")

    resultado["fonte_principal"] = "Icecat"
    resultado["encontrado"] = True

    categoria_icecat = resultado_icecat.get("categoria_chipper")
    if categoria_icecat and categoria_icecat != "desconhecido":
        resultado["categoria_final"] = str(categoria_icecat)


def _aplicar_upc(
    resultado: dict[str, Any],
    resultado_upc: dict[str, Any],
) -> None:
    resultado["upcitemdb"] = resultado_upc

    if not resultado_upc.get("encontrado"):
        erro = resultado_upc.get("erro")
        if erro:
            resultado["erros"].append(f"UPCitemdb: {erro}")
        return

    if "UPCitemdb" not in resultado["fontes_utilizadas"]:
        resultado["fontes_utilizadas"].append("UPCitemdb")

    resultado["encontrado"] = True


def resolver_produto_hibrido(nome_produto: str) -> dict[str, Any]:
    """Orquestra catálogo local, MobileAPI, Icecat, UPCitemdb e motor interno."""

    nome = str(nome_produto).strip()
    if not nome:
        raise ValueError("Informe o nome do equipamento.")

    categoria_interna = identificar_categoria_por_nome(nome)
    produto_local = buscar_produto_local(nome)

    resultado: dict[str, Any] = {
        "encontrado": False,
        "nome_informado": nome,
        "categoria_interna": categoria_interna,
        "categoria_final": categoria_interna,
        "fonte_principal": "Motor interno do CHIPPER",
        "catalogo_local": produto_local,
        "mobileapi": None,
        "icecat": None,
        "upcitemdb": None,
        "consulta_icecat": None,
        "fontes_utilizadas": [],
        "erros": [],
    }

    if produto_local:
        resultado["fontes_utilizadas"].append("Catálogo local")
        categoria_catalogo = produto_local.get("categoria")
        if categoria_catalogo:
            resultado["categoria_final"] = str(categoria_catalogo)
        resultado["fonte_principal"] = "Catálogo local"
        resultado["encontrado"] = True

    categoria_para_mobile = resultado.get("categoria_final", categoria_interna)
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
                    if dispositivo_id and _mobile_precisa_detalhes(dados_mobile):
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
            resultado["erros"].append(f"MobileAPI: {erro}")
        except Exception as erro:
            resultado["erros"].append(
                "MobileAPI: " f"{type(erro).__name__}"
            )

    icecat_consultado = False
    if produto_local:
        gtin = produto_local.get("gtin")
        if gtin:
            icecat_consultado = True
            resultado["consulta_icecat"] = {
                "estrategia": "GTIN / EAN / UPC",
                "gtin": str(gtin),
            }
            try:
                _aplicar_icecat(
                    resultado,
                    buscar_produto_por_gtin(str(gtin)),
                )
            except ProductAPIError as erro:
                resultado["erros"].append(f"Icecat: {erro}")
            except Exception as erro:
                resultado["erros"].append(
                    "Icecat: " f"{type(erro).__name__}"
                )

    categoria_atual = str(resultado.get("categoria_final") or categoria_interna)
    deve_tentar_icecat_mpn = (
        not icecat_consultado
        and categoria_atual in {"notebook", "desktop", "monitor", "console"}
    )

    if deve_tentar_icecat_mpn:
        marca = None
        codigo = None
        origem_codigo = "inferido do nome informado"

        if produto_local:
            marca_local = produto_local.get("fabricante")
            codigo_local = (
                produto_local.get("mpn")
                or produto_local.get("product_code")
                or produto_local.get("codigo_fabricante")
            )
            if marca_local and codigo_local:
                marca = str(marca_local).strip()
                codigo = str(codigo_local).strip()
                origem_codigo = "catálogo local"

        if not (marca and codigo):
            marca, codigo = _inferir_marca_codigo(nome)

        if marca and codigo:
            icecat_consultado = True
            resultado["consulta_icecat"] = {
                "estrategia": "Fabricante + MPN / código do fabricante",
                "fabricante": marca,
                "codigo_fabricante": codigo,
                "origem_codigo": origem_codigo,
            }
            try:
                _aplicar_icecat(
                    resultado,
                    buscar_produto_por_marca_codigo(marca, codigo),
                )
            except ProductAPIError as erro:
                mensagem = str(erro)
                if "404" in mensagem or "not present" in mensagem.lower():
                    mensagem = "Produto não localizado na base Icecat com o identificador consultado."
                resultado["erros"].append(f"Icecat: {mensagem}")
            except Exception as erro:
                resultado["erros"].append(
                    "Icecat: " f"{type(erro).__name__}"
                )

    # UPCitemdb entra como fallback de identificação para produtos que o
    # Icecat não conseguiu localizar ou para equipamentos sem identificador.
    icecat_encontrou = bool(
        isinstance(resultado.get("icecat"), dict)
        and resultado["icecat"].get("encontrado")
    )
    deve_tentar_upc = (
        not icecat_encontrou
        and categoria_atual in {"notebook", "desktop", "monitor", "console", "desconhecido"}
    )

    if deve_tentar_upc:
        try:
            resultado_upc = buscar_upc_por_nome(nome)
            _aplicar_upc(resultado, resultado_upc)

            if resultado_upc.get("encontrado"):
                gtin_upc = resultado_upc.get("gtin")
                if gtin_upc:
                    resultado["consulta_icecat"] = {
                        "estrategia": "GTIN obtido via UPCitemdb",
                        "gtin": str(gtin_upc),
                        "origem_codigo": "UPCitemdb",
                    }
                    try:
                        resultado_icecat_upc = buscar_produto_por_gtin(str(gtin_upc))
                        if resultado_icecat_upc.get("encontrado"):
                            _aplicar_icecat(resultado, resultado_icecat_upc)
                    except ProductAPIError as erro:
                        resultado["erros"].append(f"Icecat via UPCitemdb: {erro}")
        except UPCItemDBError as erro:
            resultado["erros"].append(f"UPCitemdb: {erro}")
        except Exception as erro:
            resultado["erros"].append(
                "UPCitemdb: " f"{type(erro).__name__}"
            )

    if not resultado["fontes_utilizadas"]:
        resultado["fontes_utilizadas"].append("Motor interno do CHIPPER")

    if resultado.get("categoria_final") in {None, ""}:
        resultado["categoria_final"] = "desconhecido"

    return resultado
