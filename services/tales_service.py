"""Mensagens determinísticas do Tales baseadas somente nos resultados do CYPHER."""

from __future__ import annotations
from typing import Any


def gerar_resumo_tales(
    *,
    equipamento_informado: str,
    modelo_identificado: str | None,
    quantidade: int,
    massa_total_g: float,
    massa_media_g: float,
    fontes: list[str],
    alertas: list[str],
    materiais: list[dict[str, Any]],
    valor_bruto: float | None,
    massa_sem_preco_g: float | None,
    massa_recuperavel_g: float | None,
    percentual_recuperavel: float | None,
    componentes_nao_confirmados: list[str] | None = None,
) -> list[str]:
    """Cria frases rastreáveis; nunca inventa confirmação, recuperação ou lucro."""
    if quantidade <= 0 or massa_total_g <= 0 or massa_media_g <= 0:
        raise ValueError("Quantidade e massas devem ser positivas.")

    nome = (modelo_identificado or "").strip()
    linhas = []
    if nome:
        fontes_validas = [str(f).strip() for f in fontes if str(f).strip()]
        origem = ", ".join(fontes_validas) if fontes_validas else "fonte não especificada"
        linhas.append(
            f"Encontrei uma identificação compatível: {nome}. "
            f"Fontes informadas: {origem}. Confira o código exato do modelo, se necessário."
        )
    else:
        linhas.append(
            f"Não consegui confirmar o modelo exato de {equipamento_informado}. "
            "A análise pode utilizar somente o perfil estimado da categoria."
        )
    linhas.append(
        f"O lote tem {quantidade} unidade(s), massa total de {massa_total_g:.2f} g "
        f"e massa média de {massa_media_g:.2f} g por unidade."
    )
    if alertas:
        linhas.append("Atenção: " + " ".join(str(x) for x in alertas) +
                      " Revise os dados antes de usar uma estimativa econômica.")
    if materiais:
        linhas.append(
            "A composição de materiais foi estimada com base no perfil da categoria, "
            "não em pesagem individual nem em análise laboratorial."
        )
    else:
        linhas.append("Não há composição material suficiente para estimar os materiais deste equipamento.")
    if componentes_nao_confirmados:
        linhas.append("Os componentes listados são prováveis para a categoria, mas não foram "
                     "confirmados individualmente neste equipamento. Peças e variantes podem "
                     "diferir; a ausência de confirmação não significa ausência física.")
    if valor_bruto is None:
        linhas.append("O valor bruto teórico não foi calculado para esta análise.")
    else:
        linhas.append(
            f"O valor bruto teórico é R$ {valor_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            + ". É uma simulação com preços internos, não receita de venda ou lucro."
        )
        if massa_sem_preco_g is not None and massa_sem_preco_g > 0:
            linhas.append(f"Há {massa_sem_preco_g:.2f} g de materiais sem preço positivo de referência.")
    if massa_recuperavel_g is None or percentual_recuperavel is None:
        linhas.append("Massa e percentual efetivamente recuperáveis: não determinados; faltam taxas verificadas.")
    else:
        linhas.append(
            f"Recuperação informada: {massa_recuperavel_g:.2f} g "
            f"({percentual_recuperavel * 100:.2f}%). Verifique a origem desse rendimento."
        )
    linhas.append(
        "Próximo passo: avalie o reaproveitamento de componentes e encaminhe os resíduos "
        "a operadores especializados em logística reversa."
    )
    return linhas
