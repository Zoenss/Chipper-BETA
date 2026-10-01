from __future__ import annotations

from typing import Any


# ============================================================
# CATÁLOGO LOCAL DE PRODUTOS
# ============================================================

PRODUTOS: list[dict[str, Any]] = [
    {
        "nome": "PlayStation 5",
        "aliases": [
            "PS5",
            "Sony PlayStation 5",
        ],
        "fabricante": "Sony",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
    },
    {
        "nome": "PlayStation 4",
        "aliases": [
            "PS4",
            "Sony PlayStation 4",
        ],
        "fabricante": "Sony",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
    },
    {
        "nome": "Xbox Series X",
        "aliases": [
            "Xbox X",
            "Microsoft Xbox Series X",
        ],
        "fabricante": "Microsoft",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
    },
    {
        "nome": "Xbox Series S",
        "aliases": [
            "Xbox S",
            "Microsoft Xbox Series S",
        ],
        "fabricante": "Microsoft",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
    },
    {
        "nome": "Nintendo Switch",
        "aliases": [
            "Switch",
            "Nintendo Switch Console",
        ],
        "fabricante": "Nintendo",
        "categoria": "console",
        "product_code": None,
        "gtin": None,
    },
    {
        "nome": "Dell Inspiron 15",
        "aliases": [
            "Inspiron 15",
            "Dell Inspiron",
        ],
        "fabricante": "Dell",
        "categoria": "notebook",
        "product_code": None,
        "gtin": None,
    },
    {
        "nome": "Lenovo IdeaPad 3",
        "aliases": [
            "IdeaPad 3",
            "Lenovo Ideapad",
        ],
        "fabricante": "Lenovo",
        "categoria": "notebook",
        "product_code": None,
        "gtin": None,
    },
    {
        "nome": "Acer Aspire 5",
        "aliases": [
            "Aspire 5",
            "Acer Aspire",
        ],
        "fabricante": "Acer",
        "categoria": "notebook",
        "product_code": None,
        "gtin": None,
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
    },
    {
        "nome": "Samsung Odyssey G5",
        "aliases": [
            "Odyssey G5",
            "Samsung Odyssey G5",
            "Samsung G5",
            "Samsung Odyssey G5 27",
            "Samsung Odyssey G5 27\"",
            "S27CG552EL",
            "LS27CG552ELMZD",
        ],
        "fabricante": "Samsung",
        "categoria": "monitor",
        "product_code": "LS27CG552ELMZD",
        "mpn": "LS27CG552ELMZD",
        "modelo": "S27CG552EL",
        "gtin": None,
    },
]


# ============================================================
# NORMALIZAÇÃO
# ============================================================

def _normalizar(texto: str) -> str:
    """
    Normaliza o texto para comparação.
    """

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
    """
    Retorna o nome principal e todos os aliases.
    """

    nomes = [
        str(
            produto.get(
                "nome",
                "",
            )
        )
    ]

    aliases = produto.get(
        "aliases",
        [],
    )

    if isinstance(aliases, list):
        nomes.extend(
            str(alias)
            for alias in aliases
        )

    return [
        nome
        for nome in nomes
        if nome.strip()
    ]


# ============================================================
# BUSCA NO CATÁLOGO
# ============================================================

def buscar_produto_local(
    nome: str,
) -> dict[str, Any] | None:
    """
    Busca um produto no catálogo local.

    Prioridade:

    1. Correspondência exata.
    2. Alias exato.
    3. Nome/alias contido, apenas quando o texto é
       suficientemente específico.

    Não utiliza busca aproximada para evitar falsos positivos.
    """

    consulta = _normalizar(
        nome
    )

    if not consulta:
        return None

    # ========================================================
    # 1. CORRESPONDÊNCIA EXATA
    # ========================================================

    for produto in PRODUTOS:
        for candidato in _nomes_produto(
            produto
        ):
            candidato_normalizado = _normalizar(
                candidato
            )

            if candidato_normalizado == consulta:
                resultado = produto.copy()
                resultado[
                    "tipo_correspondencia"
                ] = "exata"

                return resultado

    # ========================================================
    # 2. CORRESPONDÊNCIA POR TEXTO CONTIDO
    # ========================================================

    for produto in PRODUTOS:
        for candidato in _nomes_produto(
            produto
        ):
            candidato_normalizado = _normalizar(
                candidato
            )

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
        "Samsung Odyssey G5 27\"",
        "LS27CG552ELMZD",
        "PS5",
        "PlayStation 5",
        "Xbox Series X",
        "Dell Inspiron 15",
        "produto aleatório",
    ]

    for consulta in testes:
        resultado = buscar_produto_local(
            consulta
        )

        print("=" * 60)
        print(
            "CONSULTA:",
            consulta,
        )
        print(
            "RESULTADO:",
            resultado,
        )