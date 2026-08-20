import time

import streamlit as st


st.set_page_config(
    page_title="Chipper",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(
                    circle at 50% 25%,
                    #0c4a6e 0%,
                    #0f172a 40%,
                    #020617 80%,
                    #000000 100%
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
            max-width: 850px;
            padding-top: 110px;
        }

        .boot {
            text-align: center;
            margin-bottom: 50px;
        }

        .core {
            color: #64748b;
            font-family: monospace;
            letter-spacing: 4px;
            font-size: 13px;
        }

        .logo {
            font-size: 76px;
            font-weight: 900;
            letter-spacing: 13px;
            color: #38bdf8;
            text-shadow:
                0 0 12px rgba(56, 189, 248, 0.9),
                0 0 35px rgba(2, 132, 199, 0.7);
        }

        .subtitle {
            color: #cbd5e1;
            letter-spacing: 4px;
            font-size: 17px;
            margin-top: 8px;
        }

        .version {
            color: #475569;
            font-family: monospace;
            margin-top: 12px;
            font-size: 12px;
        }

        .loading-text {
            text-align: center;
            font-family: monospace;
            color: #22d3ee;
            font-size: 16px;
            margin-top: 18px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="boot">'
    '<div class="core">CHIPPER CORE SYSTEM</div>'
    '<div class="logo" translate="no">CHIPPER</div>'
    '<div class="subtitle">REVERSE LOGISTICS INTELLIGENCE</div>'
    '<div class="version">SYSTEM v2.0</div>'
    '</div>',
    unsafe_allow_html=True,
)


mensagem = st.empty()
barra = st.progress(0)

etapas = [
    ("Preparando ambiente de inicialização...", 5),
    ("Inicializando núcleo do sistema...", 15),
    ("Carregando interface tecnológica...", 30),
    ("Preparando consulta de equipamentos...", 45),
    ("Conectando motor de análise...", 60),
    ("Carregando banco de componentes...", 75),
    ("Preparando materiais recuperáveis...", 90),
    ("Sistema pronto.", 100),
]

time.sleep(0.6)

for texto, progresso in etapas:
    mensagem.markdown(
        '<div class="loading-text">'
        f'{texto}<br>{progresso}%'
        '</div>',
        unsafe_allow_html=True,
    )

    barra.progress(progresso)
    time.sleep(0.45)

mensagem.markdown(
    '<div class="loading-text" style="color:#22c55e;">'
    'SISTEMA PRONTO'
    '</div>',
    unsafe_allow_html=True,
)

time.sleep(0.8)

st.switch_page("pages/01_home.py")