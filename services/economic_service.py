from __future__ import annotations

from typing import Any


# ============================================================
# CHIPPER - ECONOMIC ENGINE
# ============================================================
#
# Responsável por transformar as massas estimadas pelo
# analysis_service.py em uma estimativa econômica.
#
# Os preços abaixo são valores de referência internos.
# Futuramente poderão ser substituídos por uma API de
# cotações de metais e materiais.
# ============================================================


# ============================================================
# PREÇOS DE REFERÊNCIA
# Unidade: R$ por grama
# ============================================================

PRECOS_REFERENCIA: dict[str, float] = {
    # Metais preciosos
    "Ouro": 450.00,
    "Prata": 5.00,
    "Paládio": 180.00,

    # Metais industriais
    "Cobre": 0.05,
    "Alumínio": 0.01,
    "Estanho": 0.15,
    "Níquel": 0.10,

    # Materiais relacionados a baterias
    "Cobalto": 0.20,
    "Lítio": 0.08,

    # Outros materiais
    "Ferro e aço": 0.002,
    "Silício": 0.01,
    "Vidro": 0.001,
    "Plásticos": 0.002,

    # Material não classificado
    "Outros materiais": 0.0,
}


# ============================================================
# ALIASES
# ============================================================

ALIASES_MATERIAIS: dict[str, str] = {
    # Ouro
    "ouro": "Ouro",
    "gold": "Ouro",

    # Prata
    "prata": "Prata",
    "silver": "Prata",

    # Paládio
    "paladio": "Paládio",
    "paládio": "Paládio",
    "palladium": "Paládio",

    # Cobre
    "cobre": "Cobre",
    "copper": "Cobre",

    # Alumínio
    "aluminio": "Alumínio",
    "alumínio": "Alumínio",
    "aluminum": "Alumínio",
    "aluminium": "Alumínio",

    # Estanho
    "estanho": "Estanho",
    "tin": "Estanho",

    # Níquel
    "niquel": "Níquel",
    "níquel": "Níquel",
    "nickel": "Níquel",

    # Cobalto
    "cobalto": "Cobalto",
    "cobalt": "Cobalto",

    # Lítio
    "litio": "Lítio",
    "lítio": "Lítio",
    "lithium": "Lítio",

    # Ferro / aço
    "ferro": "Ferro e aço",
    "aco": "Ferro e aço",
    "aço": "Ferro e aço",
    "ferro e aço": "Ferro e aço",
    "iron": "Ferro e aço",
    "steel": "Ferro e aço",

    # Silício
    "silicio": "Silício",
    "silício": "Silício",
    "silicon": "Silício",

    # Vidro
    "vidro": "Vidro",
    "glass": "Vidro",

    # Plásticos
    "plastico": "Plásticos",
    "plástico": "Plásticos",
    "plasticos": "Plásticos",
    "plásticos": "Plásticos",
    "plastic": "Plásticos",

    # Outros
    "outros materiais": "Outros materiais",
}


# ============================================================
# NORMALIZAÇÃO DO MATERIAL
# ============================================================

def normalizar_material(material: str) -> str:
    """
    Normaliza o nome recebido para o padrão utilizado
    internamente pelo CHIPPER.
    """

    if not material:
        return "Material desconhecido"

    material_limpo = str(material).strip()

    if not material_limpo:
        return "Material desconhecido"

    chave = material_limpo.lower()

    return ALIASES_MATERIAIS.get(
        chave,
        material_limpo,
    )


# ============================================================
# PREÇO POR GRAMA
# ============================================================

def obter_preco_por_grama(material: str) -> float:
    """
    Retorna o preço de referência em R$/g.

    Caso não exista preço cadastrado para o material,
    retorna 0.0.
    """

    material_normalizado = normalizar_material(
        material
    )

    return float(
        PRECOS_REFERENCIA.get(
            material_normalizado,
            0.0,
        )
    )


# ============================================================
# CÁLCULO INDIVIDUAL
# ============================================================

def calcular_valor_material(
    material: str,
    massa_g: float,
) -> dict[str, Any]:
    """
    Calcula o valor econômico estimado de um material.
    """

    massa = float(massa_g)

    if massa < 0:
        raise ValueError(
            "A massa do material não pode ser negativa."
        )

    material_normalizado = normalizar_material(
        material
    )

    preco_por_grama = obter_preco_por_grama(
        material_normalizado
    )

    valor_estimado = (
        massa * preco_por_grama
    )

    return {
        "material": material_normalizado,

        "massa_estimada_g": round(
            massa,
            6,
        ),

        "preco_por_grama": round(
            preco_por_grama,
            6,
        ),

        "valor_estimado": round(
            valor_estimado,
            2,
        ),

        "possui_preco": (
            preco_por_grama > 0
        ),
    }


# ============================================================
# CÁLCULO ECONÔMICO COMPLETO
# ============================================================

def calcular_valor_economico(
    materiais: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Recebe diretamente a lista 'materiais' gerada pelo
    analysis_service.py.

    Exemplo:

    [
        {
            "material": "Cobre",
            "percentual_estimado": 8.0,
            "massa_estimada_g": 14.8
        }
    ]
    """

    resultados: list[dict[str, Any]] = []

    valor_total = 0.0
    massa_total = 0.0
    massa_precificada = 0.0
    massa_sem_preco = 0.0

    quantidade_precificados = 0
    quantidade_sem_preco = 0

    for item in materiais:
        material = str(
            item.get(
                "material",
                "Material desconhecido",
            )
        )

        massa_g = float(
            item.get(
                "massa_estimada_g",
                0.0,
            )
        )

        percentual_estimado = float(
            item.get(
                "percentual_estimado",
                0.0,
            )
        )

        resultado = calcular_valor_material(
            material=material,
            massa_g=massa_g,
        )

        resultado["percentual_estimado"] = round(
            percentual_estimado,
            6,
        )

        resultados.append(
            resultado
        )

        massa_total += massa_g

        valor_total += float(
            resultado["valor_estimado"]
        )

        if resultado["possui_preco"]:
            massa_precificada += massa_g
            quantidade_precificados += 1

        else:
            massa_sem_preco += massa_g
            quantidade_sem_preco += 1

    # Ordena do maior valor econômico para o menor.
    resultados.sort(
        key=lambda item: float(
            item.get(
                "valor_estimado",
                0.0,
            )
        ),
        reverse=True,
    )

    return {
        "materiais": resultados,

        "valor_total_estimado": round(
            valor_total,
            2,
        ),

        "massa_total_analisada_g": round(
            massa_total,
            4,
        ),

        "massa_precificada_g": round(
            massa_precificada,
            4,
        ),

        "massa_sem_preco_g": round(
            massa_sem_preco,
            4,
        ),

        "quantidade_materiais_precificados": (
            quantidade_precificados
        ),

        "quantidade_materiais_sem_preco": (
            quantidade_sem_preco
        ),

        "moeda": "BRL",

        "simbolo_moeda": "R$",

        "fonte_precos": (
            "Tabela interna de preços de referência "
            "do CHIPPER"
        ),

        "observacao": (
            "O valor econômico apresentado é uma estimativa. "
            "O cálculo utiliza a massa estimada de cada material "
            "e preços internos de referência por grama. "
            "O valor real de recuperação pode variar conforme "
            "pureza do material, eficiência da recuperação, "
            "condição do equipamento, custos de processamento "
            "e preços de mercado."
        ),
    }


# ============================================================
# FORMATAÇÃO DE MOEDA
# ============================================================

def formatar_real(valor: float) -> str:
    """
    Formata um valor para o padrão monetário brasileiro.

    Exemplo:

    1234.56
        ↓
    R$ 1.234,56
    """

    valor_formatado = f"{float(valor):,.2f}"

    valor_formatado = (
        valor_formatado
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"R$ {valor_formatado}"


# ============================================================
# RESUMO ECONÔMICO
# ============================================================

def gerar_resumo_economico(
    analise_economica: dict[str, Any],
) -> dict[str, Any]:
    """
    Gera informações resumidas para serem exibidas
    no 02_analisar.py.
    """

    materiais = analise_economica.get(
        "materiais",
        [],
    )

    materiais_com_valor = [
        item
        for item in materiais
        if float(
            item.get(
                "valor_estimado",
                0.0,
            )
        ) > 0
    ]

    material_mais_valioso = None

    if materiais_com_valor:
        material_mais_valioso = (
            materiais_com_valor[0]
        )

    valor_total = float(
        analise_economica.get(
            "valor_total_estimado",
            0.0,
        )
    )

    return {
        "valor_total": valor_total,

        "valor_total_formatado": formatar_real(
            valor_total
        ),

        "quantidade_materiais_precificados": (
            len(materiais_com_valor)
        ),

        "material_mais_valioso": (
            material_mais_valioso
        ),
    }


# ============================================================
# TESTE LOCAL
# ============================================================

if __name__ == "__main__":
    materiais_teste = [
        {
            "material": "Cobre",
            "percentual_estimado": 8.0,
            "massa_estimada_g": 14.4,
        },
        {
            "material": "Ouro",
            "percentual_estimado": 0.03,
            "massa_estimada_g": 0.054,
        },
        {
            "material": "Prata",
            "percentual_estimado": 0.10,
            "massa_estimada_g": 0.18,
        },
        {
            "material": "Alumínio",
            "percentual_estimado": 14.0,
            "massa_estimada_g": 25.2,
        },
    ]

    resultado = calcular_valor_economico(
        materiais_teste
    )

    print("=" * 60)
    print("CHIPPER - ECONOMIC ENGINE")
    print("=" * 60)

    for item in resultado["materiais"]:
        print()
        print(
            f"Material: "
            f"{item['material']}"
        )

        print(
            f"Massa: "
            f"{item['massa_estimada_g']:.6f} g"
        )

        print(
            f"Preço/g: "
            f"{formatar_real(item['preco_por_grama'])}"
        )

        print(
            f"Valor: "
            f"{formatar_real(item['valor_estimado'])}"
        )

    print()
    print("=" * 60)

    print(
        "VALOR TOTAL:",
        formatar_real(
            resultado[
                "valor_total_estimado"
            ]
        ),
    )

    print("=" * 60)