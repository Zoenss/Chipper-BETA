"""Importação de produtos existentes — CYPHER."""
from io import BytesIO
import pandas as pd
import streamlit as st
from services.batch_service import analisar_linha

st.set_page_config(page_title="CYPHER - Importar Planilha", page_icon="♻️", layout="wide")
st.title("Analisar produtos já existentes")
st.caption("Importe uma planilha CSV ou Excel com as colunas equipamento, quantidade e massa_total_g.")
st.info("Análise em lote usa o catálogo local e perfis por categoria. Não confirma cada modelo por API externa; massas, composições e preços são estimativas, não recuperação nem lucro.")
modelo = pd.DataFrame([
    {"equipamento": "Samsung Galaxy M55 5G", "quantidade": 10, "massa_total_g": 1800},
    {"equipamento": "PlayStation 5", "quantidade": 2, "massa_total_g": 9000},
])
st.download_button("Baixar modelo CSV", modelo.to_csv(index=False).encode("utf-8-sig"), "modelo_cypher.csv", "text/csv")
arquivo = st.file_uploader("Escolha um CSV ou XLSX", type=["csv", "xlsx"])
if arquivo:
    try:
        if arquivo.name.lower().endswith(".xlsx"):
            entrada = pd.read_excel(BytesIO(arquivo.getvalue()))
        else:
            conteudo = BytesIO(arquivo.getvalue())
            try:
                entrada = pd.read_csv(conteudo, sep=None, engine="python", encoding="utf-8-sig")
            except UnicodeDecodeError:
                entrada = pd.read_csv(BytesIO(arquivo.getvalue()), sep=None, engine="python", encoding="latin-1")
        entrada.columns = [str(c).strip().lower() for c in entrada.columns]
        obrigatorias = {"equipamento", "quantidade", "massa_total_g"}
        faltantes = obrigatorias - set(entrada.columns)
        if faltantes:
            st.error("Colunas ausentes: " + ", ".join(sorted(faltantes)))
            st.stop()
        if entrada.empty:
            st.warning("A planilha está vazia.")
            st.stop()
        if len(entrada) > 500:
            st.error("Limite de 500 linhas por importação. Divida a planilha em arquivos menores.")
            st.stop()
    except (ValueError, ImportError, UnicodeDecodeError) as erro:
        st.error(f"Não foi possível ler a planilha: {erro}. Para XLSX, instale openpyxl.")
        st.stop()

    st.write(f"{len(entrada)} linha(s) carregada(s).")
    st.dataframe(entrada.head(10), use_container_width=True)
    if st.button("ANALISAR PLANILHA", type="primary"):
        linhas = []
        for indice, item in entrada.iterrows():
            try:
                resultado = analisar_linha(
                    item["equipamento"], item["quantidade"], item["massa_total_g"]
                )
                resultado["linha_planilha"] = int(indice) + 2
            except (ValueError, TypeError, KeyError) as erro:
                resultado = {
                    "linha_planilha": int(indice) + 2,
                    "equipamento": str(item.get("equipamento", "")),
                    "status": "ERRO", "alertas": str(erro)
                }
            linhas.append(resultado)
        saida = pd.DataFrame(linhas)
        st.success(f"{sum(saida['status'] != 'ERRO')} de {len(saida)} linha(s) processadas.")
        st.dataframe(saida, use_container_width=True, hide_index=True)
        st.download_button(
            "BAIXAR RESULTADOS CSV",
            saida.to_csv(index=False, sep=";").encode("utf-8-sig"),
            "cypher_resultado_lote.csv", "text/csv",
        )
if st.button("VOLTAR AO CADASTRO"):
    st.switch_page("pages/01_home.py")
