from __future__ import annotations

import streamlit as st

from services.reverse_logistics_service import (
    ReverseLogisticsError,
    buscar_pontos_eletroeletronicos,
    geocodificar_local,
)


st.set_page_config(
    page_title="Chipper - Onde descartar",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at 50% 15%, #0c4a6e 0%, #0f172a 35%, #020617 75%);
            color: white;
        }
        [data-testid="stSidebar"] { display: none; }
        header, footer { visibility: hidden; }
        .block-container { max-width: 1050px; padding-top: 45px; padding-bottom: 60px; }
        .page-title {
            font-size: 46px; font-weight: 900; color: #38bdf8;
            text-shadow: 0 0 14px rgba(56, 189, 248, 0.55); margin-bottom: 4px;
        }
        .page-subtitle { color: #94a3b8; font-size: 17px; margin-bottom: 28px; }
        .alpha {
            display: inline-block; border: 1px solid #f59e0b; color: #fbbf24;
            background: rgba(245, 158, 11, 0.08); padding: 5px 10px;
            border-radius: 999px; font-size: 12px; font-weight: 800; margin-bottom: 18px;
        }
        .point-card {
            background: rgba(15, 23, 42, 0.86); border: 1px solid #334155;
            border-radius: 16px; padding: 18px; margin: 12px 0;
        }
        .point-name { color: #22d3ee; font-size: 20px; font-weight: 850; }
        .point-text { color: #cbd5e1; line-height: 1.6; }
        .note {
            background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.42);
            border-radius: 14px; color: #fcd34d; padding: 16px; margin: 18px 0;
        }
        div.stButton > button {
            width: 100%; min-height: 49px; border-radius: 11px; border: 1px solid #38bdf8;
            background: linear-gradient(90deg, #0284c7, #06b6d4); color: white; font-weight: 850;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-title">ONDE DESCARTAR</div>'
    '<div class="page-subtitle">Localize pontos candidatos para logística reversa de equipamentos eletroeletrônicos.</div>'
    '<div class="alpha">ALPHA</div>',
    unsafe_allow_html=True,
)

equipamento = str(st.session_state.get("aparelho") or "").strip()
if equipamento:
    st.info(f"Equipamento em análise: {equipamento}")

with st.form("buscar_destino"):
    local = st.text_input(
        "Cidade ou CEP",
        placeholder="Ex.: Mairinque - SP ou 18120-000",
    )
    buscar = st.form_submit_button(
        "LOCALIZAR PONTOS DE DESCARTE",
        use_container_width=True,
    )

if buscar:
    try:
        with st.spinner("Localizando a região..."):
            origem = geocodificar_local(local)

        st.success(f"Região localizada: {origem['nome']}")

        with st.spinner("Buscando pontos de reciclagem de eletroeletrônicos próximos..."):
            pontos = buscar_pontos_eletroeletronicos(
                float(origem["latitude"]),
                float(origem["longitude"]),
            )

        if not pontos:
            st.warning(
                "Nenhum ponto específico para eletroeletrônicos foi localizado "
                "na base consultada em um raio aproximado de 20 km."
            )
        else:
            st.subheader(f"Pontos encontrados: {len(pontos)}")

            for indice, ponto in enumerate(pontos, start=1):
                nome = str(ponto["nome"])
                endereco = str(ponto["endereco"])
                distancia = float(ponto["distancia_km"])
                operador = str(ponto["operador"])
                telefone = str(ponto["telefone"])
                lat = float(ponto["latitude"])
                lon = float(ponto["longitude"])

                st.markdown(
                    '<div class="point-card">'
                    f'<div class="point-name">{indice}. {nome}</div>'
                    f'<div class="point-text"><strong>Endereço:</strong> {endereco}</div>'
                    f'<div class="point-text"><strong>Distância aproximada:</strong> {distancia:.1f} km</div>'
                    f'<div class="point-text"><strong>Operador:</strong> {operador}</div>'
                    f'<div class="point-text"><strong>Telefone:</strong> {telefone}</div>'
                    '<div class="point-text"><strong>Fonte:</strong> OpenStreetMap / Overpass</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )

                mapa = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=18/{lat}/{lon}"
                st.link_button("ABRIR NO MAPA", mapa, use_container_width=True)

        st.markdown(
            '<div class="note"><strong>Importante:</strong> esta funcionalidade está em fase alpha. '
            'Os locais são candidatos encontrados em base pública. Confirme diretamente com o '
            'estabelecimento se ele recebe o tipo específico de equipamento antes do deslocamento.</div>',
            unsafe_allow_html=True,
        )

    except ReverseLogisticsError as erro:
        st.error(str(erro))

st.markdown("---")
st.subheader("Outras referências para logística reversa")
st.caption(
    "Também é recomendável consultar programas oficiais e sistemas de logística reversa "
    "para confirmar pontos de recebimento disponíveis na região."
)

col1, col2 = st.columns(2)
with col1:
    st.link_button("GREEN ELETRON", "https://greeneletron.org.br/", use_container_width=True)
with col2:
    st.link_button("ABREE", "https://abree.org.br/", use_container_width=True)

st.markdown("---")
col_voltar, col_home = st.columns(2)
with col_voltar:
    if st.button("VOLTAR À ANÁLISE"):
        if equipamento:
            st.switch_page("pages/02_analisar.py")
        else:
            st.switch_page("pages/01_home.py")
with col_home:
    if st.button("NOVA ANÁLISE"):
        st.session_state.pop("aparelho", None)
        st.session_state.pop("peso", None)
        st.session_state.pop("quantidade", None)
        st.switch_page("pages/01_home.py")
