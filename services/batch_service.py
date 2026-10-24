"""Análise em lote a partir de uma planilha; sem alterar o cadastro individual."""
from __future__ import annotations
import math
from typing import Any

from services.analysis_service import identificar_categoria_por_nome, estimar_analise
from services.catalog_service import buscar_produto_local
from services.validation_service import validar_lote
from services.economic_service import calcular_valor_economico


def analisar_linha(nome: Any, quantidade: Any, massa_total_g: Any) -> dict[str, Any]:
    produto = str(nome or "").strip()
    if not produto or produto.lower() in {"nan", "none"}:
        raise ValueError("Equipamento não informado")
    try:
        q = float(quantidade)
        if not math.isfinite(q) or not q.is_integer() or q < 1:
            raise ValueError()
        qtd = int(q)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("Quantidade deve ser um inteiro positivo") from None
    try:
        massa = float(massa_total_g)
    except (TypeError, ValueError):
        raise ValueError("Massa total (g) deve ser numérica") from None
    if not math.isfinite(massa) or massa <= 0:
        raise ValueError("Massa total (g) deve ser positiva e finita")

    local = buscar_produto_local(produto)
    categoria = str(local.get("categoria") or "") if local else identificar_categoria_por_nome(produto)
    if not categoria:
        categoria = "desconhecido"
    validacao = validar_lote(qtd, massa, categoria)
    analise = estimar_analise(categoria, massa)
    materiais = analise["materiais"]
    confiavel = bool(validacao["confiavel_para_valoracao"])
    economico = calcular_valor_economico(materiais) if confiavel and materiais else None
    return {
        "equipamento": produto,
        "modelo_catalogo": str(local.get("nome") or "") if local else "",
        "categoria": categoria,
        "quantidade": qtd,
        "massa_total_g": massa,
        "massa_media_g": round(massa / qtd, 4),
        "fonte": "Catálogo local" if local else "Perfil de categoria (sem confirmação de modelo)",
        "status": "REVISAR" if validacao["alertas"] else ("ESTIMADO" if materiais else "SEM PERFIL"),
        "alertas": " | ".join(validacao["alertas"]),
        "valor_bruto_teorico_rs": economico["valor_bruto_estimado"] if economico else None,
        "massa_recuperavel_g": None,
        "retorno_liquido_rs": None,
    }
