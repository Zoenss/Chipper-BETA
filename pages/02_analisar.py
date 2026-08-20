from html import escape
from typing import Any

import streamlit as st

from services.analysis_service import estimar_analise
from services.economic_service import (
    calcular_valor_economico,
    formatar_real,
)
from services.hybrid_product_service import resolver_produto_hibrido


st.set_page_config(
    page_title="Chipper - Análise",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def valor_seguro(
    dados: dict[str, Any],
    chave: str,
    padrao: str = "Não informado",
) -> str:
    valor = dados.get(chave)
    if valor is None or str(valor).strip() == "":
        valor = padrao
    return escape(str(valor))


def montar_lista_html(itens: list[str]) -> str:
    return "".join(
        '<div class="list-item">'
        '<span class="list-marker">•</span>'
        f'{escape(str(item))}'
        '</div>'
        for item in itens
    )


def traduzir_categoria(categoria: str) -> str:
    traducoes = {
        "phone": "Smartphone",
        "tablet": "Tablet",
        "notebook": "Notebook",
        "desktop": "Computador desktop",
        "console": "Console de videogame",
        "monitor": "Monitor",
        "desconhecido": "Equipamento eletrônico",
    }
    categoria_normalizada = categoria.strip().lower()
    return traducoes.get(categoria_normalizada, categoria.capitalize())


st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 50% 15%,
                    #0c4a6e 0%,
                    #0f172a 35%,
                    #020617 75%
                );
            color: white;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        header,
        footer {
            visibility: hidden;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 45px;
            padding-bottom: 60px;
        }

        .page-title {
            font-size: 48px;
            font-weight: 900;
            color: #38bdf8;
            text-shadow: 0 0 14px rgba(56, 189, 248, 0.65);
            margin-bottom: 4px;
        }

        .page-subtitle {
            color: #94a3b8;
            font-size: 17px;
            margin-bottom: 32px;
        }

        .section-title {
            color: #e2e8f0;
            font-size: 27px;
            font-weight: 850;
            margin-top: 28px;
            margin-bottom: 17px;
        }

        .card {
            background: rgba(15, 23, 42, 0.84);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 21px;
            margin-bottom: 17px;
            box-shadow: 0 0 22px rgba(2, 132, 199, 0.09);
        }

        .card-title {
            color: #22d3ee;
            font-size: 14px;
            font-weight: 850;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }

        .main-value {
            color: #ffffff;
            font-size: 23px;
            font-weight: 750;
        }

        .technical-value {
            color: #e2e8f0;
            font-size: 16px;
            font-weight: 650;
            line-height: 1.55;
        }

        .small-text {
            color: #94a3b8;
            font-size: 14px;
            line-height: 1.65;
            margin-top: 7px;
        }

        .source-success {
            color: #22c55e;
            font-size: 19px;
            font-weight: 750;
        }

        .source-warning {
            color: #f59e0b;
            font-size: 19px;
            font-weight: 750;
        }

        .source-error {
            color: #ef4444;
            font-size: 19px;
            font-weight: 750;
        }

        .estimated-badge {
            display: inline-block;
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.55);
            border-radius: 999px;
            color: #fbbf24;
            font-size: 12px;
            font-weight: 800;
            padding: 5px 10px;
            margin-bottom: 14px;
        }

        .list-item {
            color: #cbd5e1;
            font-size: 15px;
            line-height: 1.65;
            padding: 3px 0;
        }

        .list-marker {
            color: #22d3ee;
            font-weight: 900;
            margin-right: 8px;
        }

        .metric-value {
            color: #38bdf8;
            font-size: 31px;
            font-weight: 900;
        }

        .metric-label {
            color: #94a3b8;
            font-size: 14px;
            margin-top: 5px;
        }

        .notice {
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.42);
            border-radius: 14px;
            color: #fcd34d;
            font-size: 14px;
            line-height: 1.65;
            padding: 17px;
            margin-top: 18px;
            margin-bottom: 20px;
        }

        div.stButton > button {
            width: 100%;
            min-height: 49px;
            border-radius: 11px;
            border: 1px solid #38bdf8;
            background: linear-gradient(90deg, #0284c7, #06b6d4);
            color: white;
            font-weight: 850;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


aparelho = st.session_state.get("aparelho")
peso = st.session_state.get("peso")
quantidade = int(
    st.session_state.get(
        "quantidade",
        1,
    )
)

if (
    not aparelho
    or peso is None
    or float(peso) <= 0
    or quantidade <= 0
):
    st.warning(
        "Nenhum equipamento válido foi enviado para análise."
    )

    if st.button("VOLTAR PARA A HOME"):
        st.switch_page("pages/01_home.py")

    st.stop()

nome_aparelho = str(aparelho).strip()
massa_total = float(peso)
massa_media = massa_total / quantidade
nome_aparelho_seguro = escape(nome_aparelho)

st.markdown(
    '<div class="page-title">ANÁLISE DO EQUIPAMENTO</div>'
    '<div class="page-subtitle">'
    'Identificação técnica, estimativa de composição e apoio à '
    'decisão de logística reversa.'
    '</div>',
    unsafe_allow_html=True,
)

col_aparelho, col_quantidade, col_massa, col_media = st.columns(4)

with col_aparelho:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">EQUIPAMENTO INFORMADO</div>'
        f'<div class="main-value">{nome_aparelho_seguro}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_quantidade:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">QUANTIDADE</div>'
        f'<div class="main-value">{quantidade}</div>'
        '<div class="small-text">unidade(s)</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_massa:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">MASSA TOTAL</div>'
        f'<div class="main-value">{massa_total:.2f} g</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_media:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">MASSA MÉDIA</div>'
        f'<div class="main-value">{massa_media:.2f} g</div>'
        '<div class="small-text">por unidade</div>'
        '</div>',
        unsafe_allow_html=True,
    )

# ==================================================
# SISTEMA HÍBRIDO DE IDENTIFICAÇÃO
# ==================================================
resultado_hibrido: dict[str, Any] | None = None
erro_hibrido: str | None = None

with st.spinner("Consultando as fontes do sistema híbrido..."):
    try:
        resultado_hibrido = resolver_produto_hibrido(
            nome_aparelho
        )
    except ValueError as erro:
        erro_hibrido = str(erro)
    except Exception as erro:
        erro_hibrido = (
            "Ocorreu um erro inesperado durante a identificação híbrida: "
            f"{type(erro).__name__}"
        )

if resultado_hibrido is None:
    resultado_hibrido = {
        "encontrado": False,
        "categoria_final": "desconhecido",
        "fonte_principal": "Motor interno do CHIPPER",
        "fontes_utilizadas": ["Motor interno do CHIPPER"],
        "catalogo_local": None,
        "mobileapi": None,
        "icecat": None,
        "erros": [],
    }

categoria_analise = str(
    resultado_hibrido.get(
        "categoria_final",
        "desconhecido",
    )
    or "desconhecido"
)

origem_categoria = str(
    resultado_hibrido.get(
        "fonte_principal",
        "Motor interno do CHIPPER",
    )
)

fontes_utilizadas = resultado_hibrido.get(
    "fontes_utilizadas",
    [],
)

if not isinstance(fontes_utilizadas, list):
    fontes_utilizadas = []

erros_fontes = resultado_hibrido.get(
    "erros",
    [],
)

if not isinstance(erros_fontes, list):
    erros_fontes = []

mobile_info = resultado_hibrido.get("mobileapi")
icecat_info = resultado_hibrido.get("icecat")
catalogo_info = resultado_hibrido.get("catalogo_local")

dados_mobile: dict[str, Any] | None = None
if isinstance(mobile_info, dict):
    dados = mobile_info.get("dados")
    if isinstance(dados, dict):
        dados_mobile = dados

dados_icecat: dict[str, Any] | None = None
if isinstance(icecat_info, dict) and icecat_info.get("encontrado"):
    dados_icecat = icecat_info

dados_catalogo: dict[str, Any] | None = None
if isinstance(catalogo_info, dict):
    dados_catalogo = catalogo_info


# ==================================================
# MOTOR DE ANÁLISE
# ==================================================
try:
    analise_estimada = estimar_analise(
        categoria=categoria_analise,
        massa_g=massa_total,
    )
except ValueError as erro:
    st.error(str(erro))
    st.stop()


# ==================================================
# ORIGEM DOS DADOS
# ==================================================
fontes_texto = ", ".join(
    str(fonte)
    for fonte in fontes_utilizadas
) or "Motor interno do CHIPPER"

if erro_hibrido:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">ORIGEM DOS DADOS</div>'
        '<div class="source-error">Sistema híbrido com falha parcial</div>'
        f'<div class="small-text">{escape(erro_hibrido)}</div>'
        '<div class="small-text">'
        'A análise foi mantida pelo motor interno do CHIPPER.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

elif dados_mobile or dados_icecat:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">ORIGEM DOS DADOS</div>'
        '<div class="source-success">Sistema híbrido ativo</div>'
        f'<div class="small-text">Fontes utilizadas: {escape(fontes_texto)}.</div>'
        '<div class="small-text">'
        'A ficha técnica externa complementa a identificação. '
        'Componentes, materiais, massas e recomendações continuam '
        'sendo estimados pelo motor CHIPPER.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

elif dados_catalogo:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">ORIGEM DOS DADOS</div>'
        '<div class="source-warning">Catálogo local utilizado</div>'
        f'<div class="small-text">Fontes utilizadas: {escape(fontes_texto)}.</div>'
        '<div class="small-text">'
        'O produto foi reconhecido pelo catálogo local. '
        'Quando houver GTIN ou código de fabricante cadastrado, '
        'o Icecat poderá complementar a ficha técnica.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

else:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">ORIGEM DOS DADOS</div>'
        '<div class="source-warning">Análise interna do CHIPPER</div>'
        f'<div class="small-text">Fontes utilizadas: {escape(fontes_texto)}.</div>'
        '<div class="small-text">'
        'Nenhuma ficha técnica externa foi localizada, '
        'mas a análise estimada continuará pela categoria identificada.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

if erros_fontes:
    with st.expander("Detalhes das fontes externas"):
        for erro in erros_fontes:
            st.caption(str(erro))


# ==================================================
# FICHA TÉCNICA HÍBRIDA
# ==================================================
if dados_mobile:
    st.markdown(
        '<div class="section-title">Ficha técnica</div>',
        unsafe_allow_html=True,
    )

    fabricante = valor_seguro(
        dados_mobile,
        "manufacturer_name",
    )
    modelo = valor_seguro(
        dados_mobile,
        "name",
    )
    categoria_exibicao = traduzir_categoria(
        str(
            dados_mobile.get(
                "device_type",
                categoria_analise,
            )
            or categoria_analise
        )
    )
    armazenamento = valor_seguro(
        dados_mobile,
        "storage",
    )
    tela = valor_seguro(
        dados_mobile,
        "screen_resolution",
    )
    peso_referencia = valor_seguro(
        dados_mobile,
        "weight",
    )
    bateria = valor_seguro(
        dados_mobile,
        "battery_capacity",
    )
    hardware = valor_seguro(
        dados_mobile,
        "hardware",
    )
    lancamento = valor_seguro(
        dados_mobile,
        "release_date",
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            '<div class="card"><div class="card-title">FABRICANTE</div>'
            f'<div class="technical-value">{fabricante}</div></div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            '<div class="card"><div class="card-title">MODELO LOCALIZADO</div>'
            f'<div class="technical-value">{modelo}</div></div>',
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            '<div class="card"><div class="card-title">CATEGORIA</div>'
            f'<div class="technical-value">{escape(categoria_exibicao)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        sufixo = (
            ""
            if peso_referencia.lower().endswith("g")
            or peso_referencia == "Não informado"
            else " g"
        )
        st.markdown(
            '<div class="card"><div class="card-title">PESO DE REFERÊNCIA</div>'
            f'<div class="technical-value">{peso_referencia}{sufixo}</div></div>',
            unsafe_allow_html=True,
        )

    with c5:
        st.markdown(
            '<div class="card"><div class="card-title">BATERIA</div>'
            f'<div class="technical-value">{bateria}</div></div>',
            unsafe_allow_html=True,
        )

    with c6:
        st.markdown(
            '<div class="card"><div class="card-title">LANÇAMENTO</div>'
            f'<div class="technical-value">{lancamento}</div></div>',
            unsafe_allow_html=True,
        )

    c7, c8 = st.columns(2)

    with c7:
        st.markdown(
            '<div class="card"><div class="card-title">ARMAZENAMENTO</div>'
            f'<div class="technical-value">{armazenamento}</div></div>',
            unsafe_allow_html=True,
        )

    with c8:
        st.markdown(
            '<div class="card"><div class="card-title">TELA</div>'
            f'<div class="technical-value">{tela}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="card"><div class="card-title">HARDWARE</div>'
        f'<div class="technical-value">{hardware}</div></div>',
        unsafe_allow_html=True,
    )

elif dados_icecat:
    st.markdown(
        '<div class="section-title">Ficha técnica</div>',
        unsafe_allow_html=True,
    )

    fabricante = escape(
        str(
            dados_icecat.get(
                "fabricante",
                "Não informado",
            )
        )
    )
    modelo = escape(
        str(
            dados_icecat.get(
                "modelo",
                "Não informado",
            )
        )
    )
    categoria_exibicao = traduzir_categoria(
        str(
            dados_icecat.get(
                "categoria_chipper",
                categoria_analise,
            )
            or categoria_analise
        )
    )
    categoria_original = escape(
        str(
            dados_icecat.get(
                "categoria_original",
                "Não informado",
            )
            or "Não informado"
        )
    )
    codigo_fabricante = escape(
        str(
            dados_icecat.get(
                "codigo_fabricante",
                "Não informado",
            )
            or "Não informado"
        )
    )
    peso_referencia = escape(
        str(
            dados_icecat.get(
                "peso",
                "Não informado",
            )
            or "Não informado"
        )
    )

    gtin_valor = dados_icecat.get(
        "gtin",
        [],
    )

    if isinstance(gtin_valor, list):
        gtin_texto = ", ".join(
            str(item)
            for item in gtin_valor
        ) or "Não informado"
    else:
        gtin_texto = str(
            gtin_valor
            or "Não informado"
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            '<div class="card"><div class="card-title">FABRICANTE</div>'
            f'<div class="technical-value">{fabricante}</div></div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            '<div class="card"><div class="card-title">MODELO LOCALIZADO</div>'
            f'<div class="technical-value">{modelo}</div></div>',
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            '<div class="card"><div class="card-title">CATEGORIA CHIPPER</div>'
            f'<div class="technical-value">{escape(categoria_exibicao)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        st.markdown(
            '<div class="card"><div class="card-title">CATEGORIA ICECAT</div>'
            f'<div class="technical-value">{categoria_original}</div></div>',
            unsafe_allow_html=True,
        )

    with c5:
        st.markdown(
            '<div class="card"><div class="card-title">CÓDIGO DO FABRICANTE</div>'
            f'<div class="technical-value">{codigo_fabricante}</div></div>',
            unsafe_allow_html=True,
        )

    with c6:
        st.markdown(
            '<div class="card"><div class="card-title">PESO DE REFERÊNCIA</div>'
            f'<div class="technical-value">{peso_referencia}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="card"><div class="card-title">GTIN / EAN / UPC</div>'
        f'<div class="technical-value">{escape(gtin_texto)}</div></div>',
        unsafe_allow_html=True,
    )

    especificacoes = dados_icecat.get(
        "especificacoes",
        {},
    )

    if isinstance(especificacoes, dict) and especificacoes:
        with st.expander("Especificações adicionais do Icecat"):
            especificacoes_tabela = [
                {
                    "Especificação": str(chave),
                    "Valor": str(valor),
                }
                for chave, valor in list(
                    especificacoes.items()
                )[:40]
            ]

            st.dataframe(
                especificacoes_tabela,
                use_container_width=True,
                hide_index=True,
            )

elif dados_catalogo:
    st.markdown(
        '<div class="section-title">Identificação pelo catálogo</div>',
        unsafe_allow_html=True,
    )

    nome_catalogo = escape(
        str(
            dados_catalogo.get(
                "nome",
                nome_aparelho,
            )
        )
    )
    fabricante_catalogo = escape(
        str(
            dados_catalogo.get(
                "fabricante",
                "Não informado",
            )
        )
    )
    categoria_catalogo = traduzir_categoria(
        str(
            dados_catalogo.get(
                "categoria",
                categoria_analise,
            )
            or categoria_analise
        )
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            '<div class="card"><div class="card-title">PRODUTO RECONHECIDO</div>'
            f'<div class="technical-value">{nome_catalogo}</div></div>',
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            '<div class="card"><div class="card-title">FABRICANTE</div>'
            f'<div class="technical-value">{fabricante_catalogo}</div></div>',
            unsafe_allow_html=True,
        )

    with c3:
        st.markdown(
            '<div class="card"><div class="card-title">CATEGORIA</div>'
            f'<div class="technical-value">{escape(categoria_catalogo)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

else:
    categoria_exibicao = escape(
        str(
            analise_estimada.get(
                "categoria_exibicao",
                "Equipamento eletrônico",
            )
        )
    )

    st.markdown(
        '<div class="section-title">Identificação interna</div>'
        '<div class="card">'
        '<div class="card-title">CATEGORIA IDENTIFICADA</div>'
        f'<div class="main-value">{categoria_exibicao}</div>'
        '<div class="small-text">'
        f'Categoria definida pelo {escape(origem_categoria)}.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


st.markdown(
    '<div class="section-title">Componentes estimados</div>'
    '<div class="estimated-badge">RESULTADOS ESTIMADOS</div>',
    unsafe_allow_html=True,
)

componentes = analise_estimada.get("componentes", [])
if componentes:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">COMPONENTES PROVÁVEIS</div>'
        f'{montar_lista_html(componentes)}'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    st.warning("Não existe um perfil de componentes para esta categoria.")

st.markdown(
    '<div class="section-title">'
    'Materiais potencialmente recuperáveis'
    '</div>',
    unsafe_allow_html=True,
)

materiais = analise_estimada.get("materiais", [])
analise_economica = calcular_valor_economico(
    materiais
)

if materiais:
    tabela_materiais = [
        {
            "Material": item.get("material", "Não informado"),
            "Massa estimada (g)": round(
                float(item.get("massa_estimada_g", 0.0)),
                4,
            ),
            "Participação estimada (%)": round(
                float(item.get("percentual_estimado", 0.0)),
                3,
            ),
        }
        for item in materiais
    ]
    st.dataframe(
        tabela_materiais,
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("Não foi possível estimar os materiais desta categoria.")

st.markdown(
    '<div class="section-title">Potencial de recuperação</div>',
    unsafe_allow_html=True,
)

massa_recuperavel = float(
    analise_estimada.get("massa_recuperavel_g", 0.0)
)
percentual_recuperavel = float(
    analise_estimada.get("percentual_recuperavel", 0.0)
)

r1, r2 = st.columns(2)
with r1:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">MASSA POTENCIALMENTE RECUPERÁVEL</div>'
        f'<div class="metric-value">{massa_recuperavel:.2f} g</div>'
        '<div class="metric-label">Estimativa baseada na massa total informada para o lote.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
with r2:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">PERCENTUAL POTENCIALMENTE RECUPERÁVEL</div>'
        f'<div class="metric-value">{percentual_recuperavel:.2f}%</div>'
        '<div class="metric-label">'
        'Percentual aproximado do perfil da categoria.'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="section-title">'
    'Recomendação de logística reversa'
    '</div>',
    unsafe_allow_html=True,
)

recomendacoes = analise_estimada.get("recomendacoes", [])
if recomendacoes:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">DESTINO RECOMENDADO</div>'
        f'{montar_lista_html(recomendacoes)}'
        '</div>',
        unsafe_allow_html=True,
    )

observacao = escape(
    str(
        analise_estimada.get(
            "observacao",
            "Os resultados apresentados são estimativas.",
        )
    )
)

st.markdown(
    '<div class="notice">'
    '<strong>Aviso técnico:</strong> '
    f'{observacao} '
    'A composição exata exige desmontagem física, pesagem individual '
    'dos componentes ou análise laboratorial.'
    '</div>',
    unsafe_allow_html=True,
)

# ==================================================
# VALOR ECONÔMICO ESTIMADO
# ==================================================
st.markdown(
    '<div class="section-title">'
    'Valor econômico estimado'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="estimated-badge">'
    'CÁLCULO ECONÔMICO ESTIMADO'
    '</div>',
    unsafe_allow_html=True,
)

materiais_economicos = analise_economica.get(
    "materiais",
    [],
)

if materiais_economicos:
    tabela_economica = []

    for item in materiais_economicos:
        tabela_economica.append(
            {
                "Material": item.get(
                    "material",
                    "Não informado",
                ),
                "Massa estimada (g)": round(
                    float(item.get("massa_estimada_g", 0.0)),
                    6,
                ),
                "Preço de referência (R$/g)": round(
                    float(item.get("preco_por_grama", 0.0)),
                    4,
                ),
                "Valor estimado (R$)": round(
                    float(item.get("valor_estimado", 0.0)),
                    2,
                ),
            }
        )

    st.dataframe(
        tabela_economica,
        use_container_width=True,
        hide_index=True,
    )

valor_total = float(
    analise_economica.get(
        "valor_total_estimado",
        0.0,
    )
)

st.markdown(
    '<div class="card">'
    '<div class="card-title">'
    'VALOR ECONÔMICO TOTAL ESTIMADO'
    '</div>'
    f'<div class="metric-value">{formatar_real(valor_total)}</div>'
    '<div class="metric-label">'
    'Estimativa baseada nos materiais identificados '
    'e nos preços internos de referência.'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

massa_precificada = float(
    analise_economica.get(
        "massa_precificada_g",
        0.0,
    )
)

massa_sem_preco = float(
    analise_economica.get(
        "massa_sem_preco_g",
        0.0,
    )
)

col_preco1, col_preco2 = st.columns(2)

with col_preco1:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">'
        'MASSA COM PREÇO DE REFERÊNCIA'
        '</div>'
        f'<div class="technical-value">{massa_precificada:.2f} g</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with col_preco2:
    st.markdown(
        '<div class="card">'
        '<div class="card-title">'
        'MASSA SEM PREÇO CADASTRADO'
        '</div>'
        f'<div class="technical-value">{massa_sem_preco:.2f} g</div>'
        '</div>',
        unsafe_allow_html=True,
    )

observacao_economica = escape(
    str(
        analise_economica.get(
            "observacao",
            "Valor econômico estimado.",
        )
    )
)

st.markdown(
    '<div class="notice">'
    '<strong>Aviso econômico:</strong> '
    f'{observacao_economica}'
    '</div>',
    unsafe_allow_html=True,
)


st.caption(
    "Ficha técnica: MobileAPI, Icecat ou catálogo local, quando disponíveis. "
    "Componentes, materiais, massas, recomendações e valor econômico: "
    "estimativas calculadas pelo motor CHIPPER."
)

col_voltar, col_exportar = st.columns(2)

with col_voltar:
    if st.button("NOVA ANÁLISE"):
        st.session_state.pop("aparelho", None)
        st.session_state.pop("peso", None)
        st.session_state.pop("quantidade", None)
        st.switch_page("pages/01_home.py")

with col_exportar:
    st.button(
        "EXPORTAR CSV",
        disabled=True,
        help=(
            "A exportação CSV poderá ser ativada em uma próxima etapa."
        ),
    )