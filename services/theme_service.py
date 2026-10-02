from __future__ import annotations

import streamlit as st


THEME_KEY = "chipper_theme"


def tema_atual() -> str:
    tema = str(st.session_state.get(THEME_KEY, "dark")).strip().lower()
    return "light" if tema == "light" else "dark"


def seletor_tema() -> str:
    """Renderiza o seletor Dark/Light e persiste a escolha na sessão."""

    claro_ativo = tema_atual() == "light"
    novo_claro = st.toggle(
        "Modo claro",
        value=claro_ativo,
        key="chipper_light_toggle",
        help="Alterna entre o visual escuro original e o modo claro do CHIPPER.",
    )

    st.session_state[THEME_KEY] = "light" if novo_claro else "dark"
    return st.session_state[THEME_KEY]


def aplicar_tema() -> None:
    """Aplica somente overrides do modo claro; o modo escuro original é preservado."""

    if tema_atual() != "light":
        return

    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(
                        circle at 50% 18%,
                        #e0f2fe 0%,
                        #f8fafc 42%,
                        #ffffff 82%
                    ) !important;
                color: #0f172a !important;
            }

            .subtitle,
            .page-subtitle,
            .small-text,
            .metric-label,
            .system-line,
            .tales-note,
            .tales-text,
            .quantity-info,
            .footer {
                color: #475569 !important;
            }

            .core,
            .version,
            .tales-subtitle {
                color: #64748b !important;
            }

            .logo,
            .page-title,
            .section-title,
            .card-title,
            .system-title {
                color: #0369a1 !important;
                text-shadow: none !important;
            }

            .system-card,
            .card,
            .tales-panel,
            .notice {
                background: rgba(255, 255, 255, 0.92) !important;
                border-color: #bae6fd !important;
                box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08) !important;
            }

            .main-value,
            .technical-value,
            .tales-text,
            .stMarkdown,
            p,
            span,
            li {
                color: #0f172a;
            }

            .stTextInput label,
            .stNumberInput label,
            .stSelectbox label,
            .stTextArea label,
            .stToggle label {
                color: #0f172a !important;
            }

            .stTextInput input,
            .stNumberInput input,
            .stTextArea textarea,
            div[data-baseweb="select"] > div {
                background: #ffffff !important;
                color: #0f172a !important;
                border-color: #cbd5e1 !important;
            }

            .stTextInput input:focus,
            .stNumberInput input:focus,
            .stTextArea textarea:focus {
                border-color: #0284c7 !important;
                box-shadow: 0 0 0 1px #0284c7 !important;
            }

            div.stButton > button,
            div[data-testid="stFormSubmitButton"] > button,
            div[data-testid="stDownloadButton"] > button {
                background: linear-gradient(90deg, #0284c7, #06b6d4) !important;
                color: #ffffff !important;
                border-color: #0284c7 !important;
            }

            [data-testid="stDataFrame"],
            [data-testid="stTable"] {
                background: #ffffff !important;
                border-radius: 12px;
            }

            hr {
                border-color: #cbd5e1 !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
