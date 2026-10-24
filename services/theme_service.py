"""Seletor de paleta do CYPHER; preferência preservada na sessão."""
import streamlit as st

TEMAS = {
    "Escuro (original)": ("#020617", "#0f172a", "#e2e8f0", "#67e8f9"),
    "Branco": ("#f8fafc", "#ffffff", "#0f172a", "#0369a1"),
    "Azul": ("#eaf4ff", "#ffffff", "#12365c", "#0759ac"),
    "Verde": ("#edf9f0", "#ffffff", "#143b27", "#16733e"),
}


def aplicar_tema():
    nome = st.session_state.get("cypher_tema", "Escuro (original)")
    fundo, painel, texto, destaque = TEMAS.get(nome, TEMAS["Escuro (original)"])
    claro = nome != "Escuro (original)"
    extras = ""
    if claro:
        extras = f"""
        .stApp .card, .stApp .tales-panel, .stApp .notice,
        .stApp [data-testid="stForm"], .stApp [data-testid="stExpander"] {{
            background: {painel} !important;
            color: {texto} !important;
            border: 1px solid {destaque}55 !important;
        }}
        .stApp .card-title, .stApp .technical-value, .stApp .main-value,
        .stApp .metric-value, .stApp .small-text, .stApp .section-title,
        .stApp .page-title, .stApp .page-subtitle, .stApp .tales-text,
        .stApp .tales-title, .stApp .tales-subtitle, .stApp .tales-note,
        .stApp .subtitle, .stApp .system-title, .stApp .system-line {{
            color: {texto} !important;
        }}
        .stApp [data-testid="stWidgetLabel"] *, .stApp p, .stApp label {{
            color: {texto};
        }}
        """
    st.markdown(f"""<style>
        .stApp {{ background: {fundo} !important; color: {texto} !important; }}
        .stApp h1, .stApp h2, .stApp h3 {{ color: {texto}; }}
        .stApp a {{ color: {destaque}; }}
        {extras}
    </style>""", unsafe_allow_html=True)


def alternar_modo():
    """Alterna claro/escuro sem perder a cor clara escolhida."""
    atual = st.session_state.get("cypher_tema", "Escuro (original)")
    if atual == "Escuro (original)":
        st.session_state["cypher_tema"] = st.session_state.get(
            "cypher_ultima_cor_clara", "Branco"
        )
    else:
        st.session_state["cypher_ultima_cor_clara"] = atual
        st.session_state["cypher_tema"] = "Escuro (original)"


def lembrar_cor():
    atual = st.session_state.get("cypher_tema")
    if atual in {"Branco", "Azul", "Verde"}:
        st.session_state["cypher_ultima_cor_clara"] = atual


def seletor_tema():
    atual = st.session_state.get("cypher_tema", "Escuro (original)")
    rotulo = "☀️ Light Mode" if atual == "Escuro (original)" else "🌙 Dark Mode"
    st.button(rotulo, key="cypher_alternar_modo", on_click=alternar_modo)
    st.selectbox(
        "🎨 Cores do CYPHER",
        list(TEMAS),
        key="cypher_tema",
        on_change=lembrar_cor,
        help="Escolha a paleta. O botão acima alterna claro e escuro.",
    )
    aplicar_tema()
