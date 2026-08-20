from __future__ import annotations

from typing import Any


PERFIS: dict[str, dict[str, Any]] = {
    "phone": {
        "nome": "Smartphone",
        "componentes": [
            "Tela",
            "Bateria de íons de lítio",
            "Placa lógica",
            "Processador",
            "Memória RAM",
            "Armazenamento",
            "Módulo de câmeras",
            "Antenas",
            "Conector USB",
            "Alto-falantes",
            "Microfones",
            "Motor vibratório",
            "Carcaça",
        ],
        "percentuais": {
            "Vidro": 0.30,
            "Plásticos": 0.20,
            "Alumínio": 0.14,
            "Cobre": 0.08,
            "Lítio": 0.015,
            "Cobalto": 0.010,
            "Níquel": 0.015,
            "Ferro e aço": 0.05,
            "Silício": 0.030,
            "Ouro": 0.0003,
            "Prata": 0.0010,
            "Paládio": 0.0002,
            "Estanho": 0.008,
            "Outros materiais": 0.1505,
        },
    },
    "tablet": {
        "nome": "Tablet",
        "componentes": [
            "Tela sensível ao toque",
            "Bateria de íons de lítio",
            "Placa lógica",
            "Processador",
            "Memória RAM",
            "Armazenamento",
            "Módulo de câmeras",
            "Alto-falantes",
            "Microfones",
            "Conector USB",
            "Carcaça",
        ],
        "percentuais": {
            "Vidro": 0.34,
            "Plásticos": 0.16,
            "Alumínio": 0.20,
            "Cobre": 0.07,
            "Lítio": 0.012,
            "Cobalto": 0.010,
            "Níquel": 0.012,
            "Ferro e aço": 0.03,
            "Silício": 0.030,
            "Ouro": 0.0002,
            "Prata": 0.0008,
            "Paládio": 0.0002,
            "Estanho": 0.008,
            "Outros materiais": 0.1268,
        },
    },
    "notebook": {
        "nome": "Notebook",
        "componentes": [
            "Tela LCD ou OLED",
            "Bateria",
            "Placa-mãe",
            "Processador",
            "Memória RAM",
            "SSD ou HD",
            "Sistema de refrigeração",
            "Cooler",
            "Teclado",
            "Touchpad",
            "Módulo Wi-Fi e Bluetooth",
            "Fonte de alimentação",
            "Carcaça",
        ],
        "percentuais": {
            "Plásticos": 0.25,
            "Alumínio": 0.18,
            "Ferro e aço": 0.18,
            "Cobre": 0.10,
            "Vidro": 0.08,
            "Lítio": 0.015,
            "Cobalto": 0.012,
            "Níquel": 0.015,
            "Silício": 0.050,
            "Ouro": 0.0005,
            "Prata": 0.002,
            "Paládio": 0.0005,
            "Estanho": 0.012,
            "Outros materiais": 0.103,
        },
    },
    "desktop": {
        "nome": "Computador desktop",
        "componentes": [
            "Gabinete",
            "Fonte de alimentação",
            "Placa-mãe",
            "Processador",
            "Memória RAM",
            "SSD ou HD",
            "Sistema de refrigeração",
            "Cabos",
            "Conectores",
            "Placa de vídeo, quando presente",
        ],
        "percentuais": {
            "Ferro e aço": 0.40,
            "Plásticos": 0.15,
            "Alumínio": 0.12,
            "Cobre": 0.12,
            "Silício": 0.07,
            "Vidro": 0.01,
            "Ouro": 0.0006,
            "Prata": 0.002,
            "Paládio": 0.0005,
            "Estanho": 0.015,
            "Outros materiais": 0.1119,
        },
    },
    "console": {
        "nome": "Console de videogame",
        "componentes": [
            "Placa principal",
            "Processador",
            "Memória",
            "Armazenamento",
            "Fonte de alimentação",
            "Sistema de refrigeração",
            "Cooler",
            "Unidade óptica, quando presente",
            "Antenas",
            "Portas USB e HDMI",
            "Carcaça",
        ],
        "percentuais": {
            "Plásticos": 0.32,
            "Ferro e aço": 0.20,
            "Alumínio": 0.16,
            "Cobre": 0.10,
            "Silício": 0.08,
            "Vidro": 0.01,
            "Ouro": 0.0005,
            "Prata": 0.0015,
            "Paládio": 0.0003,
            "Estanho": 0.012,
            "Outros materiais": 0.1157,
        },
    },
    "monitor": {
        "nome": "Monitor",
        "componentes": [
            "Painel LCD ou OLED",
            "Placa controladora",
            "Fonte de alimentação",
            "Cabos internos",
            "Iluminação de fundo",
            "Estrutura metálica",
            "Carcaça",
            "Base e suporte",
        ],
        "percentuais": {
            "Vidro": 0.35,
            "Plásticos": 0.27,
            "Ferro e aço": 0.16,
            "Alumínio": 0.07,
            "Cobre": 0.05,
            "Silício": 0.03,
            "Ouro": 0.0002,
            "Prata": 0.0008,
            "Estanho": 0.01,
            "Outros materiais": 0.059,
        },
    },
}


ALIASES_CATEGORIA: dict[str, str] = {
    "phone": "phone",
    "smartphone": "phone",
    "mobile": "phone",
    "mobile phone": "phone",
    "cellphone": "phone",
    "tablet": "tablet",
    "laptop": "notebook",
    "notebook": "notebook",
    "desktop": "desktop",
    "computer": "desktop",
    "pc": "desktop",
    "console": "console",
    "videogame": "console",
    "game console": "console",
    "gaming console": "console",
    "monitor": "monitor",
    "display": "monitor",
}


PALAVRAS_CATEGORIA: dict[str, list[str]] = {
    "console": [
        "playstation",
        "playstation 5",
        "playstation 4",
        "ps5",
        "ps4",
        "xbox",
        "nintendo switch",
        "console",
    ],
    "notebook": [
        "notebook",
        "laptop",
        "inspiron",
        "ideapad",
        "macbook",
        "latitude",
        "aspire",
        "vivobook",
        "thinkpad",
    ],
    "desktop": [
        "desktop",
        "computador",
        "pc gamer",
        "pc gaming",
        "gabinete",
        "workstation",
    ],
    "monitor": ["monitor", "display"],
    "tablet": ["tablet", "ipad", "galaxy tab"],
    "phone": [
        "galaxy",
        "iphone",
        "motorola",
        "moto g",
        "redmi",
        "poco",
        "smartphone",
        "celular",
    ],
}


def identificar_categoria_por_nome(nome: str) -> str:
    nome_normalizado = nome.strip().lower()

    for categoria, palavras in PALAVRAS_CATEGORIA.items():
        if any(palavra in nome_normalizado for palavra in palavras):
            return categoria

    return "desconhecido"


def normalizar_categoria(categoria: str | None) -> str:
    if not categoria:
        return "desconhecido"

    categoria_normalizada = categoria.strip().lower()

    return ALIASES_CATEGORIA.get(
        categoria_normalizada,
        categoria_normalizada,
    )


def gerar_recomendacoes(categoria: str) -> list[str]:
    recomendacoes_gerais = [
        "Priorizar o reaproveitamento de peças funcionais.",
        "Separar placas eletrônicas para recuperação especializada.",
        "Reciclar metais, vidro e plásticos separadamente.",
        "Evitar descarte em lixo comum.",
    ]

    recomendacoes_especificas = {
        "phone": [
            "Separar a bateria para tratamento especializado.",
            "Testar tela, câmeras, alto-falantes e conector de carga.",
        ],
        "tablet": [
            "Separar a bateria antes do processamento.",
            "Avaliar a reutilização da tela e da placa lógica.",
        ],
        "notebook": [
            "Testar memória RAM, armazenamento e fonte.",
            "Separar bateria, tela e sistema de refrigeração.",
        ],
        "desktop": [
            "Testar processador, memória, armazenamento e placa de vídeo.",
            "Separar fonte, cabos, placas eletrônicas e gabinete metálico.",
        ],
        "console": [
            "Testar armazenamento, unidade óptica e fonte.",
            "Separar placa principal e sistema de refrigeração.",
        ],
        "monitor": [
            "Avaliar o reaproveitamento do painel e da fonte.",
            "Separar estrutura metálica, placas e cabos.",
        ],
    }

    return recomendacoes_especificas.get(categoria, []) + recomendacoes_gerais


def validar_percentuais(perfil: dict[str, Any]) -> None:
    total = sum(float(valor) for valor in perfil["percentuais"].values())

    if abs(total - 1.0) > 0.0001:
        raise ValueError(
            f"Os percentuais do perfil somam {total:.6f}, e deveriam somar 1.0."
        )


def estimar_analise(
    categoria: str | None,
    massa_g: float,
) -> dict[str, Any]:
    if massa_g <= 0:
        raise ValueError("A massa deve ser maior que zero.")

    categoria_normalizada = normalizar_categoria(categoria)
    perfil = PERFIS.get(categoria_normalizada)

    if perfil is None:
        return {
            "categoria": categoria_normalizada,
            "categoria_exibicao": "Equipamento eletrônico",
            "componentes": [],
            "materiais": [],
            "massa_recuperavel_g": 0.0,
            "percentual_recuperavel": 0.0,
            "recomendacoes": [
                "Realizar inspeção técnica manual do equipamento.",
                "Separar componentes funcionais.",
                "Encaminhar placas eletrônicas para reciclagem especializada.",
                "Evitar descarte em lixo comum.",
            ],
            "observacao": (
                "Não existe um perfil específico para esta categoria."
            ),
        }

    validar_percentuais(perfil)

    materiais: list[dict[str, Any]] = []

    for material, percentual in perfil["percentuais"].items():
        massa_estimada = massa_g * float(percentual)

        materiais.append(
            {
                "material": material,
                "percentual_estimado": round(float(percentual) * 100, 4),
                "massa_estimada_g": round(massa_estimada, 6),
            }
        )

    percentual_outros = float(
        perfil["percentuais"].get("Outros materiais", 0.0)
    )

    percentual_recuperavel = max(0.0, 1.0 - percentual_outros)
    massa_recuperavel = massa_g * percentual_recuperavel

    return {
        "categoria": categoria_normalizada,
        "categoria_exibicao": perfil["nome"],
        "componentes": list(perfil["componentes"]),
        "materiais": materiais,
        "massa_recuperavel_g": round(massa_recuperavel, 2),
        "percentual_recuperavel": round(percentual_recuperavel * 100, 2),
        "recomendacoes": gerar_recomendacoes(categoria_normalizada),
        "observacao": (
            "Os resultados apresentados são estimativas calculadas "
            "pelo CHIPPER com base na categoria e na massa informada. "
            "Eles não representam desmontagem física, medição "
            "individual dos componentes ou análise laboratorial."
        ),
    }


if __name__ == "__main__":
    exemplos = [
        ("Samsung Galaxy M55 5G", 180.0),
        ("Dell Inspiron 15", 1650.0),
        ("PlayStation 5", 4500.0),
    ]

    for nome, massa in exemplos:
        categoria = identificar_categoria_por_nome(nome)
        resultado = estimar_analise(categoria, massa)

        print("=" * 60)
        print(f"Equipamento: {nome}")
        print(f"Categoria: {resultado['categoria_exibicao']}")
        print(f"Massa recuperável: {resultado['massa_recuperavel_g']} g")