import streamlit as st
import pandas as pd
import plotly.express as px
from kpis import calcular_kpis

st.set_page_config(page_title="Chipper Recycling", layout="wide")

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp { background-color: #0f172a; }
section[data-testid="stSidebar"] { background-color: #020617; }
h1 { color: #38bdf8; }
h2 { color: #22c55e; }
[data-testid="stMetricValue"] { color: #22c55e; }
</style>
""", unsafe_allow_html=True)

st.title("♻️ Chipper Recycling - Inteligência de Resíduos")

# =========================
# VALORES PADRÃO (BASE)
# =========================
VALORES_PADRAO = {
    "smartphone": 120.0,
    "notebook": 90.0,
    "tablet": 75.0,
    "perifericos": 30.0,
    "tv": 50.0,
    "robos": 150.0
}

# =========================
# SIDEBAR INTELIGENTE
# =========================
st.sidebar.header("⚙️ Configurações")

arquivo = st.sidebar.file_uploader("Carregar CSV", type=["csv"])

modo_simulacao = st.sidebar.toggle("🎛️ Modo simulação econômica")

VALOR_POR_KG = VALORES_PADRAO.copy()

if modo_simulacao:
    st.sidebar.markdown("### 💰 Ajustar valores")
    for k in VALOR_POR_KG:
        VALOR_POR_KG[k] = st.sidebar.number_input(
            k.capitalize(),
            min_value=0.0,
            value=float(VALOR_POR_KG[k])
        )

if all(v == 0 for v in VALOR_POR_KG.values()):
    st.sidebar.warning("⚠️ Todos os valores estão zerados")

# =========================
# LOAD
# =========================
try:
    if arquivo:
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_csv("data_sample.csv")

    if "data" in df.columns:
        df["data"] = pd.to_datetime(df["data"], errors="coerce")

    df["categoria"] = (
        df["categoria"].astype(str).str.strip().str.lower()
        .replace({"periféricos": "perifericos", "robôs": "robos"})
    )

    df["destino"] = df["destino"].astype(str).str.strip().str.lower()
    df["ponto_coleta"] = df["ponto_coleta"].astype(str).str.strip()

    df["massa_kg"] = pd.to_numeric(df["massa_kg"], errors="coerce").fillna(0)

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# =========================
# VALIDAÇÃO
# =========================
categorias_invalidas = set(df["categoria"].unique()) - set(VALORES_PADRAO.keys())

if categorias_invalidas:
    st.error(f"Categorias inválidas: {categorias_invalidas}")
    st.stop()

# =========================
# FILTROS
# =========================
st.sidebar.header("🎯 Filtros")

def filtro(col):
    return st.sidebar.selectbox(col, ["Todos"] + sorted(df[col].dropna().unique()))

f_cat = filtro("categoria")
f_ponto = filtro("ponto_coleta")
f_dest = filtro("destino")

df_filtrado = df.copy()

if f_cat != "Todos":
    df_filtrado = df_filtrado[df_filtrado["categoria"] == f_cat]

if f_ponto != "Todos":
    df_filtrado = df_filtrado[df_filtrado["ponto_coleta"] == f_ponto]

if f_dest != "Todos":
    df_filtrado = df_filtrado[df_filtrado["destino"] == f_dest]

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado.")
    st.stop()

# =========================
# KPIs
# =========================
resultado = calcular_kpis(df_filtrado, VALOR_POR_KG)

def brl(x):
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.markdown("## 📊 Indicadores")

c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)

c1.metric("Massa", f"{resultado.massa_recebida_kg:.1f} kg")
c2.metric("Reaproveitamento", f"{resultado.taxa_reaproveitamento_pct:.1f}%")
c3.metric("Desvio Aterro", f"{resultado.desvio_aterro_pct:.1f}%")

c4.metric("💰 Recuperado", brl(resultado.valor_recuperado_rs))
c5.metric("📈 Potencial", brl(resultado.valor_potencial_total_rs))
c6.metric("💸 Perdido", brl(resultado.valor_perdido_aterro_rs))

st.metric("⚡ Eficiência Econômica", f"{resultado.eficiencia_economica_pct:.1f}%")

# =========================
# GRÁFICOS
# =========================
st.markdown("## 📈 Análise visual")

col1, col2 = st.columns(2)

with col1:
    fig1 = px.pie(df_filtrado, names="destino", values="massa_kg", hole=0.4)
    st.plotly_chart(fig1, width='stretch')

with col2:
    fig2 = px.bar(
        df_filtrado.groupby("categoria")["massa_kg"].sum().reset_index(),
        x="categoria", y="massa_kg", color="massa_kg"
    )
    st.plotly_chart(fig2, width='stretch')

# =========================
# FINANCEIRO
# =========================
st.markdown("## 💰 Financeiro")

df_fin = df_filtrado.copy()
df_fin["preco"] = df_fin["categoria"].map(VALOR_POR_KG).fillna(0)
df_fin["valor"] = df_fin["massa_kg"] * df_fin["preco"]

fig_fin = px.bar(
    df_fin.groupby("destino")["valor"].sum().reset_index(),
    x="destino",
    y="valor",
    color="valor",
    title="Valor por destino"
)

st.plotly_chart(fig_fin, width='stretch')

# =========================
# PERDA
# =========================
st.markdown("## 💸 Perda no aterro")

perda = df_fin[df_fin["destino"] == "aterro"]

fig_perda = px.bar(
    perda.groupby("categoria")["valor"].sum().reset_index(),
    x="categoria",
    y="valor"
)

st.plotly_chart(fig_perda, width='stretch')

# =========================
# TENDÊNCIA
# =========================
if "data" in df_filtrado.columns:
    temp = df_fin.dropna(subset=["data"])

    if not temp.empty:
        fig = px.line(
            temp.groupby("data")["valor"].sum().reset_index(),
            x="data", y="valor",
            title="Evolução do valor"
        )
        st.plotly_chart(fig, width='stretch')

# =========================
# TABELA
# =========================
st.markdown("## 📋 Dados")
st.dataframe(df_filtrado, width='stretch')

with st.expander("📖 Dicionário, Fórmulas e Interpretação dos Indicadores"):

    st.markdown("## 🧠 Como interpretar os dados")

    st.markdown("""
Este sistema não mostra apenas números — ele revela **fluxo de valor e eficiência operacional**.

A unidade principal utilizada é **quilograma (kg)** porque:
- resíduos são medidos fisicamente em massa
- logística e transporte são baseados em peso
- permite comparação direta entre categorias diferentes

👉 O valor financeiro é derivado da massa:
**valor = massa × preço por kg**
""")

    st.markdown("---")

    st.markdown("## 📊 Indicadores operacionais")

    st.markdown("""
### 🧱 Massa recebida
Total de resíduos coletados.

📌 Fórmula:
massa_total = soma(massa_kg)

👉 Base de todo o sistema — sem massa, não há valor.
""")

    st.markdown("""
### ♻️ Reaproveitamento (%)
Percentual que virou valor (reuso + reciclagem)

📌 Fórmula:
(reuso + reciclagem) / total × 100

👉 Mede eficiência ambiental e econômica.
""")

    st.markdown("""
### 🚫 Desvio de aterro (%)
Quanto foi salvo do descarte final.

📌 Fórmula:
(total - aterro) / total × 100

👉 Quanto maior, melhor o impacto ambiental.
""")

    st.markdown("---")

    st.markdown("## 💰 Indicadores financeiros")

    st.markdown("""
### 💰 Valor recuperado
Dinheiro gerado com reaproveitamento.

📌 Fórmula:
Σ (massa × preço) para reuso + reciclagem

👉 Representa receita potencial real.
""")

    st.markdown("""
### 📈 Valor potencial
Quanto poderia ser recuperado se tudo fosse reaproveitado.

📌 Fórmula:
Σ (massa total × preço)

👉 Mostra o teto máximo de valor.
""")

    st.markdown("""
### 💸 Valor perdido
Valor que foi para o aterro.

📌 Fórmula:
Σ (massa no aterro × preço)

👉 Indica desperdício econômico.
""")

    st.markdown("""
### ⚡ Eficiência econômica
Quanto do valor possível foi capturado.

📌 Fórmula:
(valor recuperado / valor potencial) × 100

👉 Métrica estratégica de performance.
""")

    st.markdown("---")

    st.markdown("## 📊 Por que os gráficos usam kg?")

    st.markdown("""
Os gráficos operacionais usam **massa (kg)** porque:

- 📦 representa o fluxo físico real
- 🚛 logística é baseada em peso
- ♻️ decisões ambientais usam volume/massa

Já os gráficos financeiros usam **R$** para:

- 💰 análise de valor
- 📈 tomada de decisão econômica
- ⚖️ comparação de eficiência

👉 Em resumo:

massa = realidade física  
valor = realidade econômica  

E o sistema conecta os dois.
""")

    st.markdown("---")

    st.success("""
🎯 Leitura estratégica:

Se a massa é alta e o valor é baixo → problema de qualidade dos resíduos  
Se o valor potencial é alto e o recuperado é baixo → oportunidade  
Se o perdido é alto → falha operacional  

👉 O objetivo do sistema é transformar lixo em decisão.
""")