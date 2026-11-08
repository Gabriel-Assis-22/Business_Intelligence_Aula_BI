"""
Módulo de inteligência analítica e visualizações para o dataset da Fórmula 1 (2010-2026).
Consolida métricas e gráficos para os 4 painéis estratégicos de BI:
1. Macro Finanças & Era Liberty Media
2. Equipes, Orçamentos & Efeito Cost Cap
3. Economia dos Circuitos & Geopolítica da F1
4. Eficiência de Investimento & ROI Esportivo
"""

from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Paleta esportiva e executiva premium inspirada na F1
F1_PALETTE = [
    "#E10600",  # Vermelho F1
    "#1E293B",  # Slate Escuro
    "#00D2BE",  # Mercedes Ciano / Verde Água
    "#0600EF",  # Red Bull / Williams Azul
    "#FF8000",  # McLaren Laranja Papaia
    "#006F62",  # Aston Martin Verde Racing
    "#0090FF",  # Alpine Azul
    "#52E252",  # Stake / Sauber Verde Neon
    "#B6BABD",  # Haas Prata / Cinza
    "#6692FF",  # RB Azul Claro
]

COMMON_CONFIG = {
    "displayModeBar": "hover",
    "displaylogo": False,
    "modeBarButtonsToRemove": ["zoomIn2d", "zoomOut2d", "autoScale2d", "lasso2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "f1_analytics_chart",
        "height": 600,
        "width": 1000,
        "scale": 2,
    },
}


def _apply_f1_layout(fig: go.Figure, title: str = "") -> go.Figure:
    """Aplica estilo visual moderno e consistente aos gráficos da F1 com suporte a Cross-Filtering."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else "",
            "font": {"size": 14, "family": "Inter, sans-serif", "color": "#0F172A"},
            "x": 0.01,
            "y": 0.92,
            "xanchor": "left",
            "yanchor": "top",
        },
        template="plotly_white",
        clickmode="event+select",
        margin=dict(l=20, r=20, t=75, b=65),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.18,
            xanchor="center",
            x=0.5,
            title="",
            font=dict(size=11),
        ),
        font=dict(family="Inter, sans-serif", color="#334155"),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor="#CBD5E1",
        ),
    )
    return fig


# -------------------------------------------------------------
# 1. CARREGAMENTO DOS DADOS DA F1
# -------------------------------------------------------------
def load_f1_datasets(data_dir: Path = Path("data")) -> dict:
    """Carrega as 5 tabelas da F1 a partir da pasta data/."""
    tables = {}
    files_map = {
        "f1_business": "f1_business.csv",
        "circuit_economics": "circuit_economics.csv",
        "constructor_finances": "constructor_finances.csv",
        "race_results": "race_results.csv",
        "driver_standings": "driver_standings.csv",
    }
    for key, filename in files_map.items():
        filepath = data_dir / filename
        if filepath.exists():
            tables[key] = pd.read_csv(filepath)
        else:
            tables[key] = pd.DataFrame()
    return tables


# -------------------------------------------------------------
# 2. CÁLCULO DE KPIS EXECUTIVOS
# -------------------------------------------------------------
def compute_macro_kpis(df_f1: pd.DataFrame, df_team: pd.DataFrame, df_circ: pd.DataFrame) -> dict:
    """Calcula os indicadores macroeconômicos e executivos da F1."""
    if df_f1.empty:
        return {}

    total_rev = df_f1["total_revenue_usd_m"].sum()
    avg_rev = df_f1["total_revenue_usd_m"].mean()

    # Comparativo Pré vs Pós Liberty Media
    liberty_df = df_f1[df_f1["is_liberty_media_era"] == 1]
    pre_liberty_df = df_f1[df_f1["is_liberty_media_era"] == 0]
    avg_liberty = liberty_df["total_revenue_usd_m"].mean() if not liberty_df.empty else 0
    avg_pre_liberty = pre_liberty_df["total_revenue_usd_m"].mean() if not pre_liberty_df.empty else 1
    crescimento_liberty = ((avg_liberty - avg_pre_liberty) / avg_pre_liberty) * 100

    # Lucro médio por equipe pré vs pós teto
    lucro_pre_cap = 0
    lucro_pos_cap = 0
    if not df_team.empty:
        df_team_calc = df_team.copy()
        df_team_calc["net_profit"] = df_team_calc["total_revenue_usd_m"] - df_team_calc["operating_budget_usd_m"]
        lucro_pre_cap = df_team_calc[df_team_calc["in_cost_cap_era"] == 0]["net_profit"].mean()
        lucro_pos_cap = df_team_calc[df_team_calc["in_cost_cap_era"] == 1]["net_profit"].mean()

    # Total de taxas pagas pelos circuitos
    total_hosting_fees = df_circ["hosting_fee_usd_m_est"].sum() if not df_circ.empty else 0
    media_audiencia_us = df_f1["us_avg_race_viewers_m"].iloc[-1] if not df_f1.empty else 0

    return {
        "faturamento_total_bilhoes": total_rev / 1000.0,
        "faturamento_medio_anual": avg_rev,
        "crescimento_liberty_pct": crescimento_liberty,
        "lucro_medio_pre_cap": lucro_pre_cap,
        "lucro_medio_pos_cap": lucro_pos_cap,
        "total_hosting_fees_bilhoes": total_hosting_fees / 1000.0,
        "audiencia_us_atual": media_audiencia_us,
    }


# -------------------------------------------------------------
# 3. PAINEL 1: MACRO FINANÇAS & LIBERTY MEDIA
# -------------------------------------------------------------
def plot_f1_revenue_streams(df_f1: pd.DataFrame) -> go.Figure:
    """Gráfico de área empilhada da evolução das linhas de receita do Grupo F1."""
    if df_f1.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_f1["season"],
        y=df_f1["race_promotion_fees_usd_m"],
        mode="lines+markers",
        name="Taxas de Circuitos (GPs)",
        stackgroup="one",
        line=dict(width=0.5, color="#E10600"),
        fillcolor="rgba(225, 6, 0, 0.75)",
        hovertemplate="Taxas de GP (%{x}): $%{y:.1f}M<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_f1["season"],
        y=df_f1["broadcast_media_usd_m"],
        mode="lines+markers",
        name="Direitos de Transmissão (TV)",
        stackgroup="one",
        line=dict(width=0.5, color="#1E293B"),
        fillcolor="rgba(30, 41, 59, 0.75)",
        hovertemplate="Transmissão (%{x}): $%{y:.1f}M<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_f1["season"],
        y=df_f1["sponsorship_usd_m"],
        mode="lines+markers",
        name="Patrocínios Globais",
        stackgroup="one",
        line=dict(width=0.5, color="#00D2BE"),
        fillcolor="rgba(0, 210, 190, 0.75)",
        hovertemplate="Patrocínios (%{x}): $%{y:.1f}M<extra></extra>",
    ))

    fig.add_trace(go.Scatter(
        x=df_f1["season"],
        y=df_f1["other_revenue_usd_m"],
        mode="lines+markers",
        name="Outras Receitas (Paddock/Frete)",
        stackgroup="one",
        line=dict(width=0.5, color="#FF8000"),
        fillcolor="rgba(255, 128, 0, 0.75)",
        hovertemplate="Outras (%{x}): $%{y:.1f}M<extra></extra>",
    ))

    # Linha vertical marcando a entrada da Liberty Media (2017)
    fig.add_vline(
        x=2017,
        line_width=2,
        line_dash="dash",
        line_color="#475569",
        annotation_text="Entrada Liberty Media (2017)",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#334155"),
    )

    fig.update_xaxes(title="Temporada", tickmode="linear", dtick=2, showgrid=False)
    fig.update_yaxes(title="Receita (Milhões USD)", tickprefix="$", gridcolor="#F1F5F9")
    return _apply_f1_layout(fig, "Decomposição das Linhas de Receita da F1 ($M)")


def plot_f1_us_audience_and_dts(df_f1: pd.DataFrame) -> go.Figure:
    """Evolução da audiência nos EUA, espectadores de Drive to Survive e patrocínios."""
    if df_f1.empty:
        return go.Figure()

    fig = go.Figure()

    # Barras de espectadores de Drive to Survive
    fig.add_trace(go.Bar(
        x=df_f1["season"],
        y=df_f1["drive_to_survive_viewers_m_est"],
        name="Espectadores Netflix (DTS)",
        marker_color="rgba(225, 6, 0, 0.25)",
        yaxis="y2",
        hovertemplate="DTS: %{y}M espectadores<extra></extra>",
    ))

    # Linha de audiência média nos EUA
    fig.add_trace(go.Scatter(
        x=df_f1["season"],
        y=df_f1["us_avg_race_viewers_m"],
        name="Audiência Média EUA (M)",
        mode="lines+markers",
        line=dict(color="#E10600", width=3),
        hovertemplate="Audiência EUA: %{y:.2f}M<extra></extra>",
    ))

    # Linha de patrocínios globais da F1 (em escala secundária)
    fig.add_trace(go.Scatter(
        x=df_f1["season"],
        y=df_f1["sponsorship_usd_m"] / 100.0,
        name="Patrocínios ($ centenas M)",
        mode="lines+markers",
        line=dict(color="#0F172A", width=2.5, dash="dot"),
        hovertemplate="Patrocínios: $%{y:.2f} centenas M<extra></extra>",
    ))

    fig.update_layout(
        yaxis=dict(title="Audiência Média EUA (Milhões)", gridcolor="#F1F5F9"),
        yaxis2=dict(
            title="Drive to Survive (Milhões)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )
    fig.update_xaxes(title="Temporada", tickmode="linear", dtick=2)
    return _apply_f1_layout(fig, "Efeito Drive to Survive & Expansão de Audiência nos EUA")


# -------------------------------------------------------------
# 4. PAINEL 2: EQUIPES, ORÇAMENTOS & COST CAP
# -------------------------------------------------------------
def plot_team_finances_comparison(df_team: pd.DataFrame, season: int = None) -> go.Figure:
    """Compara Orçamento Operacional vs Receita Total e Lucro por Equipe."""
    if df_team.empty:
        return go.Figure()

    df_filtered = df_team[df_team["season"] == season] if season else df_team

    agg_team = df_filtered.groupby("team_name").agg(
        orcamento=("operating_budget_usd_m", "mean"),
        receita=("total_revenue_usd_m", "mean"),
    ).reset_index()

    agg_team["lucro"] = agg_team["receita"] - agg_team["orcamento"]
    agg_team = agg_team.sort_values(by="receita", ascending=False)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=agg_team["team_name"],
        y=agg_team["orcamento"],
        name="Orçamento Operacional",
        marker_color="#475569",
        hovertemplate="<b>%{x}</b><br>Orçamento: $%{y:.1f}M<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=agg_team["team_name"],
        y=agg_team["receita"],
        name="Receita Total",
        marker_color="#00D2BE",
        hovertemplate="<b>%{x}</b><br>Receita: $%{y:.1f}M<extra></extra>",
    ))

    fig.update_layout(barmode="group")
    fig.update_yaxes(title="Milhões USD ($M)", tickprefix="$", gridcolor="#F1F5F9")
    fig.update_xaxes(title="")
    title_suffix = f"({season})" if season else "(Média das Temporadas)"
    return _apply_f1_layout(fig, f"Orçamento vs Receita por Construtor {title_suffix}")


def plot_cost_cap_budget_convergence(df_team: pd.DataFrame) -> go.Figure:
    """Mostra como os orçamentos das grandes escuderias convergiram após o teto de 2021."""
    if df_team.empty:
        return go.Figure()

    if df_team["team_name"].nunique() <= 6:
        df_top = df_team.copy()
    else:
        top_teams = ["Ferrari", "Mercedes", "Red Bull Racing", "McLaren", "Williams", "Haas"]
        df_top = df_team[df_team["team_name"].isin(top_teams)]

    fig = px.line(
        df_top,
        x="season",
        y="operating_budget_usd_m",
        color="team_name",
        custom_data=["team_name", "season"],
        title="Impacto do Cost Cap: Achatamento e Convergência Orçamentária",
        labels={"operating_budget_usd_m": "Orçamento ($M)", "season": "Temporada", "team_name": "Equipe"},
        color_discrete_sequence=F1_PALETTE,
    )

    fig.update_traces(mode="lines+markers", line=dict(width=2.5))

    # Marcação da linha do teto orçamentário
    fig.add_vline(
        x=2021,
        line_width=2,
        line_dash="dash",
        line_color="#E10600",
        annotation_text="Início do Cost Cap ($145M)",
        annotation_position="top left",
        annotation_font=dict(size=11, color="#E10600"),
    )

    fig.update_xaxes(tickmode="linear", dtick=2)
    fig.update_yaxes(tickprefix="$", gridcolor="#F1F5F9")
    return _apply_f1_layout(fig, "Evolução do Orçamento Operacional ($M) e o Efeito Teto")


# -------------------------------------------------------------
# 5. PAINEL 3: ECONOMIA DOS CIRCUITOS & GEOPOLÍTICA
# -------------------------------------------------------------
def plot_circuit_fees_vs_attendance(df_circ: pd.DataFrame, season: int = None) -> go.Figure:
    """Dispersão entre Taxa de Realização ($M) e Público no Final de Semana."""
    if df_circ.empty:
        return go.Figure()

    df_filtered = df_circ[df_circ["season"] == season] if season else df_circ

    circ_agg = df_filtered.groupby(["circuit", "grand_prix", "region", "is_street_circuit"]).agg(
        taxa_media=("hosting_fee_usd_m_est", "mean"),
        publico_medio=("weekend_attendance_k", "mean"),
        corridas=("season", "count"),
    ).reset_index()

    circ_agg["tipo_pista"] = circ_agg["is_street_circuit"].map({1: "Circuito de Rua", 0: "Pista Permanente"})

    fig = px.scatter(
        circ_agg,
        x="publico_medio",
        y="taxa_media",
        color="region",
        size="corridas",
        symbol="tipo_pista",
        hover_name="circuit",
        custom_data=["region", "circuit", "grand_prix"],
        labels={
            "publico_medio": "Público no Fim de Semana (Milhares)",
            "taxa_media": "Taxa de Realização ($M)",
            "region": "Região Geográfica",
            "corridas": "Edições no Calendário",
        },
        color_discrete_sequence=F1_PALETTE,
    )

    fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#FFFFFF")))
    fig.update_xaxes(gridcolor="#F1F5F9", title="Público Acumulado no Fim de Semana (milhares)")
    fig.update_yaxes(gridcolor="#F1F5F9", tickprefix="$", title="Taxa de Realização ($ Milhões)")
    return _apply_f1_layout(fig, "Taxa Paga pelos Circuitos vs. Público Presente no Autódromo")


def plot_regional_fees_donut(df_circ: pd.DataFrame, season: int = None) -> go.Figure:
    """Gráfico Donut da distribuição regional das taxas de corrida."""
    if df_circ.empty:
        return go.Figure()

    df_filtered = df_circ[df_circ["season"] == season] if season else df_circ

    reg_summary = (
        df_filtered.groupby("region")
        .agg(taxas_totais=("hosting_fee_usd_m_est", "sum"))
        .reset_index()
        .sort_values(by="taxas_totais", ascending=False)
    )

    total_fees = reg_summary["taxas_totais"].sum()

    fig = px.pie(
        reg_summary,
        names="region",
        values="taxas_totais",
        hole=0.55,
        color_discrete_sequence=F1_PALETTE,
    )

    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Total Taxas: $%{value:,.1f}M<br>Participação: %{percent}<extra></extra>",
    )

    fig.add_annotation(
        text=f"Total<br><b>${total_fees:,.0f}M</b>",
        x=0.5,
        y=0.5,
        font_size=13,
        showarrow=False,
    )

    return _apply_f1_layout(fig, "Participação Geográfica nas Taxas de GP (Hosting Fees)")


def plot_street_vs_permanent(df_circ: pd.DataFrame, df_race: pd.DataFrame) -> go.Figure:
    """Compara circuitos de rua vs circuitos permanentes em taxas, público e safety cars."""
    if df_circ.empty:
        return go.Figure()

    merged = pd.merge(df_circ, df_race[["season", "grand_prix", "safety_car_periods"]], on=["season", "grand_prix"], how="left")

    summary = merged.groupby("is_street_circuit").agg(
        taxa_media=("hosting_fee_usd_m_est", "mean"),
        publico_medio=("weekend_attendance_k", "mean"),
        safety_cars=("safety_car_periods", "mean"),
    ).reset_index()

    summary["Tipo de Traçado"] = summary["is_street_circuit"].map({1: "Circuito de Rua", 0: "Pista Tradicional"})

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=summary["Tipo de Traçado"],
        y=summary["taxa_media"],
        name="Taxa Média ($M)",
        marker_color="#E10600",
        hovertemplate="%{x}<br>Taxa: $%{y:.1f}M<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=summary["Tipo de Traçado"],
        y=summary["publico_medio"] / 10.0,
        name="Público Médio (x10k)",
        marker_color="#1E293B",
        hovertemplate="%{x}<br>Público: %{y:.1f} x10k<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=summary["Tipo de Traçado"],
        y=summary["safety_cars"] * 10.0,
        name="Safety Cars por Corrida (x10)",
        marker_color="#FF8000",
        hovertemplate="%{x}<br>Safety Cars: %{y:.1f}<extra></extra>",
    ))

    fig.update_layout(barmode="group")
    fig.update_yaxes(gridcolor="#F1F5F9")
    return _apply_f1_layout(fig, "Comparativo: Circuitos de Rua vs. Pistas Tradicionais")


# -------------------------------------------------------------
# 6. PAINEL 4: EFICIÊNCIA DE INVESTIMENTO & ROI ESPORTIVO
# -------------------------------------------------------------
def plot_driver_championship_wins(df_driver: pd.DataFrame) -> go.Figure:
    """Ranking dos pilotos mais vitoriosos e com mais títulos mundiais no período."""
    if df_driver.empty:
        return go.Figure()

    top_drivers = df_driver.groupby("driver_name").agg(
        vitorias=("wins", "sum"),
        poles=("poles", "sum"),
        podios=("podiums_est", "sum"),
        titulos=("is_world_champion", "sum"),
        pontos=("total_points", "sum"),
    ).reset_index().sort_values(by="vitorias", ascending=False).head(10)

    fig = px.bar(
        top_drivers,
        x="vitorias",
        y="driver_name",
        orientation="h",
        color="titulos",
        title="Top 10 Pilotos Mais Vitoriosos (2010-2026)",
        labels={"vitorias": "Total de Vitórias", "driver_name": "Piloto", "titulos": "Títulos Mundiais"},
        color_continuous_scale="Reds",
    )

    fig.update_traces(
        texttemplate="%{x} vitórias (%{color} títulos)",
        textposition="inside",
        hovertemplate="<b>%{y}</b><br>Vitórias: %{x}<br>Títulos Mundiais: %{color}<extra></extra>",
    )
    fig.update_xaxes(gridcolor="#F1F5F9")
    fig.update_yaxes(categoryorder="total ascending", title="")
    return _apply_f1_layout(fig, "Ranking de Pilotos: Vitórias e Títulos Mundiais")


def plot_team_financial_efficiency(df_team: pd.DataFrame, df_driver: pd.DataFrame) -> go.Figure:
    """Ranking de gastos acumulados e premiações das escuderias."""
    if df_team.empty:
        return go.Figure()

    team_stats = df_team.groupby("team_name").agg(
        orcamento_acumulado=("operating_budget_usd_m", "sum"),
        receita_acumulada=("total_revenue_usd_m", "sum"),
        premiacao_acumulada=("prize_money_usd_m", "sum"),
        titulos_construtores=("is_constructors_champion", "sum"),
    ).reset_index().sort_values(by="orcamento_acumulado", ascending=False)

    fig = px.bar(
        team_stats,
        x="team_name",
        y=["orcamento_acumulado", "premiacao_acumulada"],
        barmode="group",
        labels={"value": "Total em Milhões ($M)", "team_name": "Equipe", "variable": "Métrica"},
        color_discrete_sequence=["#475569", "#E10600"],
    )

    fig.update_yaxes(tickprefix="$", gridcolor="#F1F5F9")
    fig.update_xaxes(title="")
    return _apply_f1_layout(fig, "Gasto Operacional Acumulado vs. Premiações F1 Recebidas ($M)")

