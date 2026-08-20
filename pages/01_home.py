from textwrap import dedent

import streamlit as st


st.set_page_config(
    page_title="Chipper",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================
# ESTADO DO TALES
# =========================
if "tales_aberto" not in st.session_state:
    st.session_state["tales_aberto"] = False


# ============================================================
# ESTILO VISUAL DA HOME
# ============================================================
#
# GUIA RÁPIDO DE CORES:
#
# #020617 = fundo quase preto
# #0f172a = azul muito escuro
# #0c4a6e = azul profundo
#
# #38bdf8 = azul principal do CHIPPER
# #22d3ee = ciano
# #22c55e = verde / sucesso / reciclagem
#
# #818cf8 = azul-violeta do Tales
#
# #cbd5e1 = texto claro
# #94a3b8 = texto secundário
# #64748b = texto discreto
#
# DICA:
# Troque uma coisa de cada vez para conseguir perceber
# exatamente o que cada alteração está fazendo.
# ============================================================

st.markdown(
    dedent(
        """
        <style>

            /* =================================================
               FUNDO PRINCIPAL
               =================================================
               MEXE EM:
               - Cor de fundo da página inteira
               - Iluminação atrás do CHIPPER
               - Atmosfera geral do sistema
               ================================================= */

            .stApp {
                background:
                    radial-gradient(
                        circle at 51% 25%,
                        #0c4a6e 0%,
                        #0f172a 40%,
                        #020617 80%
                    );

                color: white;
            }

            /* SIDEBAR */
            [data-testid="stSidebar"] {
                display: none;
            }

            /* HEADER E FOOTER PADRÃO DO STREAMLIT */
            header,
            footer {
                visibility: hidden;
            }

            /* ÁREA PRINCIPAL */
            .block-container {
                max-width: 850px;
                padding-top: 60px;
                padding-bottom: 100px;
            }

            /* ÁREA DO LOGO */
            .hero {
                text-align: center;
                margin-bottom: 35px;
            }

            /* LOGO CHIPPER */
            .logo {
                font-family: "Brush Script MT", Brush Script Std, cursive;
                font-size: 68px;
                font-weight: 900;
                letter-spacing: 12px;

                color: #67e8f9;

                text-shadow:
                    0 0 5px #22d3ee,
                    0 0 15px #22d3ee,
                    0 0 30px #0284c7,
                    0 0 55px rgba(2, 132, 199, 0.55);
            }

            /* SUBTÍTULO */
            .subtitle {
                color: #cbd5e1;
                letter-spacing: 3px;
                font-size: 17px;
                margin-top: 6px;
            }

            /* VERSÃO */
            .version {
                color: #2E8B57;
                font-family: monospace;
                margin-top: 8px;
            }

            /* CARD STATUS DO SISTEMA */
            .system-card {
                background:
                    linear-gradient(
                        135deg,
                        rgba(15, 23, 42, 0.88),
                        rgba(12, 74, 110, 0.24)
                    );
                backdrop-filter: blur(12px);
                border: 1px solid rgba(56, 189, 248, 0.25);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 25px;
                box-shadow:
                    0 8px 30px rgba(0, 0, 0, 0.25),
                    0 0 25px rgba(2, 132, 199, 0.10);
            }

            /* TÍTULO DO STATUS */
            .system-title {
                color: #22d3ee;
                font-family: monospace;
                font-weight: bold;
                margin-bottom: 12px;
                letter-spacing: 1px;
            }

            /* LINHAS DO STATUS */
            .system-line {
                color: #94a3b8;
                font-family: monospace;
                margin: 7px 0;
            }

            /* INDICADOR VERDE */
            .ok {
                color: #22c55e;
            }

            /* TÍTULOS DOS CAMPOS */
            .stTextInput label,
            .stNumberInput label {
                color: #cbd5e1 !important;
                font-weight: 700 !important;
            }

            /* CAMPOS DE ENTRADA */
            .stTextInput input,
            .stNumberInput input {
                background-color: rgba(15, 23, 42, 0.95) !important;
                border: 1px solid #334155 !important;
                color: white !important;
                border-radius: 12px !important;
                min-height: 52px;
            }

            /* CAMPO EM FOCO */
            .stTextInput input:focus,
            .stNumberInput input:focus {
                border-color: #38bdf8 !important;
                box-shadow:
                    0 0 15px rgba(56, 189, 248, 0.30) !important;
            }

            /* BOTÃO INICIAR ANÁLISE */
            div[data-testid="stFormSubmitButton"] > button {
                width: 100%;
                min-height: 55px;
                margin-top: 18px;
                border-radius: 12px;
                border: 1px solid #38bdf8;
                background:
                    linear-gradient(
                        90deg,
                        #0284c7,
                        #06b6d4,
                        #10b981
                    );
                color: white;
                font-weight: 800;
                letter-spacing: 2px;
                transition: 0.25s;
            }

            /* HOVER DO BOTÃO */
            div[data-testid="stFormSubmitButton"] > button:hover {
                border-color: #67e8f9;
                box-shadow:
                    0 0 12px rgba(34, 211, 238, 0.70),
                    0 0 30px rgba(16, 185, 129, 0.30);
                transform: translateY(-2px);
            }

            /* TEXTO ABAIXO DA QUANTIDADE */
            .quantity-info {
                color: #64748b;
                font-size: 13px;
                margin-top: -8px;
                margin-bottom: 8px;
            }

            /* PAINEL DO TALES */
            .tales-panel {
                background:
                    linear-gradient(
                        135deg,
                        rgba(15, 23, 42, 0.98),
                        rgba(30, 27, 75, 0.92)
                    );
                border: 1px solid #818cf8;
                border-radius: 18px;
                padding: 20px;
                margin-top: 16px;
                box-shadow:
                    0 0 20px rgba(99, 102, 241, 0.25);
            }

            /* NOME TALES */
            .tales-title {
                color: #818cf8;
                font-size: 21px;
                font-weight: 900;
                margin-bottom: 5px;
                text-shadow:
                    0 0 12px rgba(99, 102, 241, 0.50);
            }

            /* SUBTÍTULO DO TALES */
            .tales-subtitle {
                color: #64748b;
                font-size: 13px;
                margin-bottom: 15px;
            }

            /* TEXTO PRINCIPAL DO TALES */
            .tales-text {
                color: #cbd5e1;
                font-size: 15px;
                line-height: 1.8;
            }

            /* OBSERVAÇÃO DO TALES */
            .tales-note {
                color: #94a3b8;
                font-size: 13px;
                margin-top: 14px;
                line-height: 1.6;
            }

            /* RODAPÉ DO CHIPPER */
            .footer {
                text-align: center;
                color: #475569;
                font-family: monospace;
                font-size: 12px;
                margin-top: 45px;
            }

        </style>
        """
    ),
    unsafe_allow_html=True,
)


# =========================
# CABEÇALHO
# =========================
st.markdown(
    '<div class="hero">'
    '<div class="logo" translate="no">CHIPPER</div>'
    '<div class="subtitle">'
    'REVERSE LOGISTICS INTELLIGENCE'
    '</div>'
    '<div class="version">SYSTEM v2.0</div>'
    '</div>',
    unsafe_allow_html=True,
)


# =========================
# STATUS DO SISTEMA
# =========================
st.markdown(
    '<div class="system-card">'
    '<div class="system-title">STATUS DO SISTEMA</div>'

    '<div class="system-line">'
    '<span class="ok">●</span> Interface disponível'
    '</div>'

    '<div class="system-line">'
    '<span class="ok">●</span> Sistema híbrido preparado'
    '</div>'

    '<div class="system-line">'
    '<span class="ok">●</span> Catálogo local disponível'
    '</div>'

    '<div class="system-line">'
    '<span class="ok">●</span> Motor econômico disponível'
    '</div>'

    '<div class="system-line">'
    '<span class="ok">●</span> Sistema aguardando nova análise'
    '</div>'

    '</div>',
    unsafe_allow_html=True,
)


# =========================
# FORMULÁRIO DE ANÁLISE
# =========================
with st.form(
    "formulario_analise",
    clear_on_submit=False,
):
    aparelho = st.text_input(
        "Identifique o equipamento",
        placeholder=(
            "Ex.: Samsung Galaxy M55 5G, "
            "PlayStation 5 ou Dell Inspiron 15"
        ),
    )

    quantidade = st.number_input(
        "Quantidade de unidades",
        min_value=1,
        value=1,
        step=1,
    )

    st.markdown(
        '<div class="quantity-info">'
        'Para uma única unidade, mantenha o valor em 1.'
        '</div>',
        unsafe_allow_html=True,
    )

    peso = st.number_input(
        "Massa total medida em gramas",
        min_value=0.0,
        step=1.0,
        format="%.1f",
    )

    iniciar_analise = st.form_submit_button(
        "INICIAR ANÁLISE",
        use_container_width=True,
    )


# =========================
# VALIDAÇÃO
# =========================
if iniciar_analise:
    nome_aparelho = aparelho.strip()

    if not nome_aparelho:
        st.warning(
            "Informe o nome do equipamento."
        )

    elif quantidade <= 0:
        st.warning(
            "Informe pelo menos uma unidade."
        )

    elif peso <= 0:
        st.warning(
            "Informe uma massa total maior que zero."
        )

    else:
        st.session_state[
            "aparelho"
        ] = nome_aparelho

        st.session_state[
            "quantidade"
        ] = int(
            quantidade
        )

        st.session_state[
            "peso"
        ] = float(
            peso
        )

        st.switch_page(
            "pages/02_analisar.py"
        )


# =========================
# TALES
# =========================
st.markdown("---")

col_espaco, col_tales = st.columns(
    [8, 1]
)

with col_tales:
    st.image(
        "assets/tales.png",
        width=75,
    )

    if st.button(
        "Tales",
        help="Abrir assistente Tales",
        use_container_width=True,
    ):
        st.session_state[
            "tales_aberto"
        ] = not st.session_state[
            "tales_aberto"
        ]


# =========================
# PAINEL DO TALES
# =========================
if st.session_state[
    "tales_aberto"
]:
    st.markdown(
        '<div class="tales-panel">'

        '<div class="tales-title">'
        'Tales'
        '</div>'

        '<div class="tales-subtitle">'
        'ASSISTENTE CHIPPER'
        '</div>'

        '<div class="tales-text">'

        '<strong>1.</strong> '
        'Informe o modelo do equipamento.<br>'

        '<strong>2.</strong> '
        'Informe quantas unidades serão analisadas.<br>'

        '<strong>3.</strong> '
        'Pese todas as unidades juntas.<br>'

        '<strong>4.</strong> '
        'Informe a massa total em gramas.<br>'

        '<strong>5.</strong> '
        'Clique em '
        '<strong>INICIAR ANÁLISE</strong>.<br><br>'

        'O CHIPPER irá identificar o equipamento, '
        'consultar as fontes disponíveis e estimar '
        'componentes, materiais recuperáveis, '
        'potencial de recuperação e valor econômico.'

        '</div>'

        '<div class="tales-note">'
        'Exemplo: para 10 celulares que juntos pesam '
        '1.800 g, informe quantidade 10 e massa total '
        '1.800 g.'
        '</div>'

        '</div>',
        unsafe_allow_html=True,
    )


# =========================
# RODAPÉ
# =========================
st.markdown(
    '<div class="footer">'
    'CHIPPER CORE • MATERIAL INTELLIGENCE • Chipper International • 2026 • '
    'REVERSE LOGISTICS'
    '</div>',
    unsafe_allow_html=True,
)