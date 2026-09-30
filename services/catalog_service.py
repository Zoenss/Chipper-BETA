from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


# ============================================================
# CATÁLOGO LOCAL DE PRODUTOS
# ============================================================

CATALOGO_CSV = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "catalogo_equipamentos.csv"
)


PRODUTOS_FALLBACK: list[dict[str, Any]] = [
    {
        "nome": "PlayStation 5",
        "aliases": ["PS5", "Sony PlayStation 5"],
        "fabricante": "Sony",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "PlayStation 4",
        "aliases": ["PS4", "Sony PlayStation 4"],
        "fabricante": "Sony",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "Xbox Series X",
        "aliases": ["Xbox X", "Microsoft Xbox Series X"],
        "fabricante": "Microsoft",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "Xbox Series S",
        "aliases": ["Xbox S", "Microsoft Xbox Series S"],
        "fabricante": "Microsoft",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "Nintendo Switch",
        "aliases": ["Switch", "Nintendo Switch Console"],
        "fabricante": "Nintendo",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "Dell Inspiron 15",
        "aliases": ["Inspiron 15", "Dell Inspiron"],
        "fabricante": "Dell",
        "categoria": "notebook",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "Lenovo IdeaPad 3",
        "aliases": ["IdeaPad 3", "Lenovo Ideapad"],
        "fabricante": "Lenovo",
        "categoria": "notebook",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "Acer Aspire 5",
        "aliases": ["Aspire 5", "Acer Aspire"],
        "fabricante": "Acer",
        "categoria": "notebook",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "Samsung Galaxy M55 5G",
        "aliases": [
            "Samsung M55 5G",
            "Samsung Galaxy M55",
            "Galaxy M55 5G",
            "Galaxy M55",
            "M55 5G",
            "M55",
        ],
        "fabricante": "Samsung",
        "categoria": "phone",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
    {
        "nome": "Samsung Odyssey G5",
        "aliases": [
            "Odyssey G5",
            "Samsung Odyssey G5",
            "Samsung G5",
        ],
        "fabricante": "Samsung",
        "categoria": "monitor",
        "product_code": None,
        "gtin": None,
        "peso_referencia_g": None,
        "fonte": "fallback_codigo",
    },
]


def _valor_ou_none(valor: Any) -> str | None:
    texto = str(valor or "").strip()
    return texto or None


def _peso_ou_none(valor: Any) -> float | None:
    texto = str(valor or "").strip().replace(",", ".")
    if not texto:
        return None
    try:
        return float(texto)
    except ValueError:
        return None


def _carregar_catalogo_csv() -> list[dict[str, Any]]:
    """Carrega o catálogo local a partir do CSV.

    Se o arquivo estiver ausente, vazio ou inválido, retorna uma lista
    vazia para permitir o uso do fallback em código.
    """

    if not CATALOGO_CSV.exists():
        return []

    try:
        with CATALOGO_CSV.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as arquivo:
            leitor = csv.DictReader(
                arquivo,
                delimiter=";",
            )

            produtos: list[dict[str, Any]] = []

            for linha in leitor:
                nome = _valor_ou_none(linha.get("nome"))
                if not nome:
                    continue

                aliases_texto = _valor_ou_none(
                    linha.get("aliases")
                )
                aliases = []
                if aliases_texto:
                    aliases = [
                        alias.strip()
                        for alias in aliases_texto.split("|")
                        if alias.strip()
                    ]

                produtos.append(
                    {
                        "nome": nome,
                        "aliases": aliases,
                        "fabricante": _valor_ou_none(
                            linha.get("fabricante")
                        ),
                        "categoria": _valor_ou_none(
                            linha.get("categoria")
                        ),
                        "product_code": _valor_ou_none(
                            linha.get("product_code")
                        ),
                        "gtin": _valor_ou_none(
                            linha.get("gtin")
                        ),
                        "peso_referencia_g": _peso_ou_none(
                            linha.get("peso_referencia_g")
                        ),
                        "fonte": (
                            _valor_ou_none(linha.get("fonte"))
                            or "catalogo_csv"
                        ),
                    }
                )

            return produtos

    except (OSError, csv.Error, UnicodeError):
        return []


def obter_produtos_catalogo() -> list[dict[str, Any]]:
    """Retorna o catálogo CSV quando disponível, senão o fallback."""

    produtos_csv = _carregar_catalogo_csv()
    if produtos_csv:
        return produtos_csv

    return [produto.copy() for produto in PRODUTOS_FALLBACK]


# Mantém compatibilidade com qualquer código que importe PRODUTOS.
PRODUTOS: list[dict[str, Any]] = obter_produtos_catalogo()


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def _normalizar(texto: str) -> str:
    """Normaliza o texto para comparação."""

    return " ".join(
        str(texto)
        .strip()
        .lower()
        .split()
    )


# ============================================================
# NOMES POSSÍVEIS DE UM PRODUTO
# ============================================================

def _nomes_produto(
    produto: dict[str, Any],
) -> list[str]:
    """Retorna o nome principal e todos os aliases."""

    nomes = [str(produto.get("nome", ""))]
    aliases = produto.get("aliases", [])

    if isinstance(aliases, list):
        nomes.extend(str(alias) for alias in aliases)

    return [nome for nome in nomes if nome.strip()]


# ============================================================
# BUSCA NO CATÁLOGO
# ============================================================

def buscar_produto_local(
    nome: str,
) -> dict[str, Any] | None:
    """Busca um produto no catálogo local.

    Prioridade:
    1. Correspondência exata.
    2. Alias exato.
    3. Nome/alias contido, quando suficientemente específico.

    Não utiliza busca aproximada para evitar falsos positivos.
    """

    consulta = _normalizar(nome)

    if not consulta:
        return None

    produtos = obter_produtos_catalogo()

    # 1. Correspondência exata
    for produto in produtos:
        for candidato in _nomes_produto(produto):
            candidato_normalizado = _normalizar(candidato)

            if candidato_normalizado == consulta:
                resultado = produto.copy()
                resultado["tipo_correspondencia"] = "exata"
                return resultado

    # 2. Correspondência por texto contido
    for produto in produtos:
        for candidato in _nomes_produto(produto):
            candidato_normalizado = _normalizar(candidato)

            if len(consulta) < 5:
                continue

            if len(candidato_normalizado) < 5:
                continue

            if consulta in candidato_normalizado:
                resultado = produto.copy()
                resultado[
                    "tipo_correspondencia"
                ] = "consulta_contida"
                return resultado

            if candidato_normalizado in consulta:
                resultado = produto.copy()
                resultado[
                    "tipo_correspondencia"
                ] = "produto_contido"
                return resultado

    return None


if __name__ == "__main__":
    testes = [
        "Samsung m55 5g",
        "Galaxy M55",
        "Samsung Odyssey G5",
        "PS5",
        "PlayStation 5",
        "Xbox Series X",
        "Dell Inspiron 15",
        "produto aleatório",
    ]

    for consulta in testes:
        resultado = buscar_produto_local(consulta)
        print("=" * 60)
        print("CONSULTA:", consulta)
        print("RESULTADO:", resultado)
