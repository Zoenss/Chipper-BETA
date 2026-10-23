"""Validação conservadora dos dados de entrada do CYPHER."""
from __future__ import annotations
import math
import re

# Faixas amplas de plausibilidade, NÃO fichas técnicas de modelos específicos.
FAIXAS_G = {
    "phone": (70, 600), "tablet": (150, 2000),
    "notebook": (500, 6500), "desktop": (1000, 35000),
    "console": (150, 10000), "monitor": (500, 30000),
}

def validar_lote(quantidade: int, massa_total_g: float, categoria: str,
                 massa_referencia_g: float | None = None) -> dict:
    if isinstance(quantidade, bool) or not isinstance(quantidade, int) or quantidade < 1:
        raise ValueError("A quantidade deve ser um inteiro positivo.")
    try:
        massa = float(massa_total_g)
    except (TypeError, ValueError):
        raise ValueError("Informe uma massa total numérica.") from None
    if not math.isfinite(massa) or massa <= 0:
        raise ValueError("A massa total deve ser positiva e finita.")
    media = massa / quantidade
    alertas = []
    faixa = FAIXAS_G.get(categoria)
    if faixa and not (faixa[0] <= media <= faixa[1]):
        alertas.append(
            f"Massa média de {media:.2f} g fora da faixa orientativa "
            f"({faixa[0]}–{faixa[1]} g) da categoria. "
            "Confira se informou a massa TOTAL em gramas e a quantidade correta."
        )
    if massa_referencia_g is not None:
        try:
            referencia = float(massa_referencia_g)
        except (ValueError, TypeError):
            referencia = 0
        if math.isfinite(referencia) and referencia > 0:
            desvio = abs(media - referencia) / referencia
            if desvio > 0.30:
                alertas.append(
                    f"Massa por unidade diverge {desvio:.0%} da referência de "
                    f"{referencia:.2f} g. Confirme a variante do modelo e a pesagem."
                )
    return {
        "quantidade": quantidade, "massa_total_g": massa,
        "massa_media_g": media, "alertas": alertas,
        "confiavel_para_valoracao": len(alertas) == 0,
    }

def extrair_massa_referencia_g(valor: object) -> float | None:
    """Interpreta apenas valores inequívocos em g ou kg; não adivinha unidades."""
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        numero = float(valor)
        return numero if math.isfinite(numero) and numero > 0 else None
    s = str(valor or "").strip().lower().replace(",", ".")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(kg|g|gramas?)", s)
    if not m:
        return None
    n = float(m.group(1)) * (1000 if m.group(2) == "kg" else 1)
    return n if math.isfinite(n) and n > 0 else None
