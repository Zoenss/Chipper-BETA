from dataclasses import dataclass
import pandas as pd

DESTINOS_VALIDOS = {"reuso", "reciclagem", "aterro", "armazenado"}


@dataclass(frozen=True)
class KPIResultado:
    massa_recebida_kg: float
    massa_reuso_kg: float
    massa_reciclagem_kg: float
    massa_aterro_kg: float
    taxa_reaproveitamento_pct: float
    desvio_aterro_pct: float

    valor_recuperado_rs: float
    valor_potencial_total_rs: float
    valor_perdido_aterro_rs: float
    eficiencia_economica_pct: float


def validar_df(df: pd.DataFrame) -> None:
    colunas_obrigatorias = {"data", "ponto_coleta", "categoria", "massa_kg", "destino"}
    faltando = colunas_obrigatorias - set(df.columns)

    if faltando:
        raise ValueError(f"CSV faltando colunas: {sorted(faltando)}")

    if df["massa_kg"].isna().any():
        raise ValueError("A coluna 'massa_kg' contém valores vazios.")

    if (df["massa_kg"] < 0).any():
        raise ValueError("A coluna 'massa_kg' não pode ter valores negativos.")

    destinos_invalidos = set(df["destino"].dropna().unique()) - DESTINOS_VALIDOS
    if destinos_invalidos:
        raise ValueError(f"Destino(s) inválido(s): {sorted(destinos_invalidos)}")

    if df["categoria"].isna().any():
        raise ValueError("A coluna 'categoria' contém valores vazios.")

    if df["destino"].isna().any():
        raise ValueError("A coluna 'destino' contém valores vazios.")


def calcular_kpis(df: pd.DataFrame, valor_por_kg: dict | None = None) -> KPIResultado:
    validar_df(df)

    df = df.copy()

    # =========================
    # NORMALIZAÇÃO
    # =========================
    df["categoria"] = df["categoria"].astype(str).str.strip().str.lower()
    df["destino"] = df["destino"].astype(str).str.strip().str.lower()

    if valor_por_kg:
        valor_por_kg = {k.strip().lower(): float(v) for k, v in valor_por_kg.items()}

    # =========================
    # MASSAS
    # =========================
    resumo_destino = df.groupby("destino")["massa_kg"].sum().to_dict()

    massa_recebida = float(df["massa_kg"].sum())
    massa_reuso = float(resumo_destino.get("reuso", 0.0))
    massa_reciclagem = float(resumo_destino.get("reciclagem", 0.0))
    massa_aterro = float(resumo_destino.get("aterro", 0.0))

    massa_reaproveitada = massa_reuso + massa_reciclagem

    # =========================
    # TAXAS
    # =========================
    taxa_reaproveitamento = (
        (massa_reaproveitada / massa_recebida) * 100
        if massa_recebida > 0 else 0
    )

    desvio_aterro = (
        ((massa_recebida - massa_aterro) / massa_recebida) * 100
        if massa_recebida > 0 else 0
    )

    # =========================
    # FINANCEIRO
    # =========================
    valor_recuperado = 0.0
    valor_potencial = 0.0
    valor_perdido = 0.0
    eficiencia = 0.0

    if valor_por_kg:
        df["preco_kg"] = df["categoria"].map(valor_por_kg).fillna(0)
        df["valor_rs"] = df["massa_kg"] * df["preco_kg"]

        # 💰 recuperado
        valor_recuperado = df.loc[
            df["destino"].isin(["reuso", "reciclagem"]),
            "valor_rs"
        ].sum()

        # 📈 potencial total
        valor_potencial = df["valor_rs"].sum()

        # 💸 perdido no aterro
        valor_perdido = df.loc[
            df["destino"] == "aterro",
            "valor_rs"
        ].sum()

        # ⚡ eficiência
        eficiencia = (
            (valor_recuperado / valor_potencial) * 100
            if valor_potencial > 0 else 0
        )

    # =========================
    # RETURN
    # =========================
    return KPIResultado(
        massa_recebida_kg=round(massa_recebida, 2),
        massa_reuso_kg=round(massa_reuso, 2),
        massa_reciclagem_kg=round(massa_reciclagem, 2),
        massa_aterro_kg=round(massa_aterro, 2),
        taxa_reaproveitamento_pct=round(taxa_reaproveitamento, 2),
        desvio_aterro_pct=round(desvio_aterro, 2),

        valor_recuperado_rs=round(valor_recuperado, 2),
        valor_potencial_total_rs=round(valor_potencial, 2),
        valor_perdido_aterro_rs=round(valor_perdido, 2),
        eficiencia_economica_pct=round(eficiencia, 2),
    )