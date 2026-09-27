from __future__ import annotations

import csv
from io import StringIO
from typing import Any


def gerar_csv_analise(
    *,
    equipamento: str,
    quantidade: int,
    massa_total_g: float,
    massa_media_g: float,
    categoria: str,
    fonte_principal: str,
    fontes_utilizadas: list[str],
    materiais: list[dict[str, Any]],
    materiais_economicos: list[dict[str, Any]],
    massa_recuperavel_g: float,
    percentual_recuperavel: float,
    valor_total_estimado: float,
    recomendacoes: list[str],
) -> bytes:
    """Gera o CSV da análise atual do CHIPPER em formato amigável ao Excel."""

    saida = StringIO()

    campos = [
        "equipamento",
        "quantidade",
        "massa_total_g",
        "massa_media_g",
        "categoria",
        "fonte_principal",
        "fontes_utilizadas",
        "material",
        "massa_estimada_g",
        "participacao_estimada_pct",
        "preco_referencia_rs_g",
        "valor_estimado_rs",
        "massa_recuperavel_g",
        "percentual_recuperavel",
        "valor_total_estimado_rs",
        "recomendacoes_logistica_reversa",
    ]

    escritor = csv.DictWriter(
        saida,
        fieldnames=campos,
        delimiter=";",
        lineterminator="\n",
    )
    escritor.writeheader()

    percentuais_por_material = {
        str(item.get("material", "Não informado")): float(
            item.get("percentual_estimado", 0.0)
        )
        for item in materiais
    }

    fontes_texto = " | ".join(str(fonte) for fonte in fontes_utilizadas)
    recomendacoes_texto = " | ".join(str(item) for item in recomendacoes)

    linhas_economicas = materiais_economicos or [
        {
            "material": item.get("material", "Não informado"),
            "massa_estimada_g": item.get("massa_estimada_g", 0.0),
            "preco_por_grama": 0.0,
            "valor_estimado": 0.0,
        }
        for item in materiais
    ]

    if not linhas_economicas:
        linhas_economicas = [
            {
                "material": "Não informado",
                "massa_estimada_g": 0.0,
                "preco_por_grama": 0.0,
                "valor_estimado": 0.0,
            }
        ]

    for item in linhas_economicas:
        material = str(item.get("material", "Não informado"))

        escritor.writerow(
            {
                "equipamento": equipamento,
                "quantidade": int(quantidade),
                "massa_total_g": round(float(massa_total_g), 4),
                "massa_media_g": round(float(massa_media_g), 4),
                "categoria": categoria,
                "fonte_principal": fonte_principal,
                "fontes_utilizadas": fontes_texto,
                "material": material,
                "massa_estimada_g": round(
                    float(item.get("massa_estimada_g", 0.0)),
                    6,
                ),
                "participacao_estimada_pct": round(
                    percentuais_por_material.get(material, 0.0),
                    4,
                ),
                "preco_referencia_rs_g": round(
                    float(item.get("preco_por_grama", 0.0)),
                    6,
                ),
                "valor_estimado_rs": round(
                    float(item.get("valor_estimado", 0.0)),
                    2,
                ),
                "massa_recuperavel_g": round(float(massa_recuperavel_g), 4),
                "percentual_recuperavel": round(
                    float(percentual_recuperavel),
                    4,
                ),
                "valor_total_estimado_rs": round(
                    float(valor_total_estimado),
                    2,
                ),
                "recomendacoes_logistica_reversa": recomendacoes_texto,
            }
        )

    return saida.getvalue().encode("utf-8-sig")
