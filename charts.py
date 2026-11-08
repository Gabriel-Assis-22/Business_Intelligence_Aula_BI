"""
Módulo de visualização com Plotly Express.
Projetado para máxima simplicidade, personalização moderna e fácil adição de novos gráficos.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Paleta moderna e profissional para o Dashboard
COLOR_PALETTE = [
    "#4361EE",  # Azul Principal
    "#3A0CA3",  # Índigo Escuro
    "#4CC9F0",  # Azul Claro / Ciano
    "#F72585",  # Magenta / Rosa Vibrante
    "#7209B7",  # Roxo
    "#06D6A0",  # Verde Menta
    "#FFB703",  # Amarelo Ouro
    "#FB8500",  # Laranja
]

COMMON_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "toImageButtonOptions": {
        "format": "png",
        "filename": "grafico_bi",
        "height": 600,
        "width": 1000,
        "scale": 2,  # Exporta em alta resolução
    },
}


def _apply_modern_layout(fig: go.Figure, title: str = "") -> go.Figure:
    """Aplica tema e formatação moderna padrão a qualquer gráfico."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>" if title else "",
            "font": {"size": 16, "family": "Inter, sans-serif", "color": "#1E293B"},
            "x": 0.02,
            "y": 0.95,
        },
        template="plotly_white",
        clickmode="event+select",
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title="",
            font=dict(size=11),
        ),
        font=dict(family="Inter, sans-serif", color="#334155"),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor="#E2E8F0",
        ),
    )
    return fig


# -------------------------------------------------------------
# 1. GRÁFICO DE LINHAS / ÁREA TEMPORAL
# -------------------------------------------------------------
def plot_revenue_time_series(df: pd.DataFrame, freq: str = "D") -> go.Figure:
    """
    Gráfico de área/linha para evolução do faturamento no tempo.
    freq: 'D' (Diário), 'W' (Semanal), 'M' (Mensal)
    """
    if df.empty:
        return go.Figure()

    # Agrupamento temporal
    df_temp = df.copy()
    df_temp["data_grp"] = df_temp["data"].dt.to_period(freq).dt.to_timestamp()
    
    resumo_temporal = (
        df_temp.groupby("data_grp")
        .agg(faturamento=("faturamento", "sum"), pedidos=("id_pedido", "nunique"))
        .reset_index()
    )

    fig = px.area(
        resumo_temporal,
        x="data_grp",
        y="faturamento",
        title="Evolução Temporal do Faturamento",
        labels={"data_grp": "Data", "faturamento": "Faturamento (R$)"},
        color_discrete_sequence=[COLOR_PALETTE[0]],
    )

    # Adiciona linha suave sobre a área
    fig.update_traces(
        line=dict(width=2.5, color=COLOR_PALETTE[0]),
        fillcolor="rgba(67, 97, 238, 0.15)",
        hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Faturamento:</b> R$ %{y:,.2f}<extra></extra>",
    )

    fig.update_xaxes(showgrid=False, title="")
    fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9", tickprefix="R$ ")
    return _apply_modern_layout(fig, "Evolução do Faturamento no Tempo")


# -------------------------------------------------------------
# 2. GRÁFICO DE BARRAS COMPARATIVO
# -------------------------------------------------------------
def plot_revenue_by_category(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras horizontal ordenado com faturamento por categoria.
    """
    if df.empty:
        return go.Figure()

    cat_summary = (
        df.groupby("categoria")
        .agg(faturamento=("faturamento", "sum"), pedidos=("id_pedido", "nunique"))
        .reset_index()
        .sort_values(by="faturamento", ascending=True)
    )

    fig = px.bar(
        cat_summary,
        x="faturamento",
        y="categoria",
        orientation="h",
        title="Faturamento por Categoria",
        labels={"faturamento": "Faturamento (R$)", "categoria": "Categoria"},
        color="categoria",
        color_discrete_sequence=COLOR_PALETTE,
    )

    fig.update_traces(
        texttemplate="R$ %{x:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Faturamento: R$ %{x:,.2f}<extra></extra>",
        showlegend=False,
    )

    fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", tickprefix="R$ ")
    fig.update_yaxes(showgrid=False, title="")
    return _apply_modern_layout(fig, "Faturamento por Categoria de Produto")


# -------------------------------------------------------------
# 3. GRÁFICO DE PIZZA / DONUT (DISTRIBUIÇÃO PERCENTUAL)
# -------------------------------------------------------------
def plot_region_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de Donut mostrando a distribuição percentual e total de faturamento por região.
    """
    if df.empty:
        return go.Figure()

    reg_summary = (
        df.groupby("regiao")
        .agg(faturamento=("faturamento", "sum"))
        .reset_index()
        .sort_values(by="faturamento", ascending=False)
    )

    total_fat = reg_summary["faturamento"].sum()

    fig = px.pie(
        reg_summary,
        values="faturamento",
        names="regiao",
        hole=0.55,
        title="Distribuição de Vendas por Região",
        color_discrete_sequence=COLOR_PALETTE,
    )

    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Faturamento: R$ %{value:,.2f}<br>Participação: %{percent}<extra></extra>",
        marker=dict(line=dict(color="#FFFFFF", width=2)),
    )

    # Anotação com o valor total no centro do donut
    fig.add_annotation(
        text=f"Total<br><b>R$ {total_fat:,.0f}</b>",
        x=0.5,
        y=0.5,
        font_size=13,
        showarrow=False,
        align="center",
    )

    return _apply_modern_layout(fig, "Participação por Região Geográfica")


# -------------------------------------------------------------
# 4. GRÁFICOS COMPLEMENTARES
# -------------------------------------------------------------
def plot_channel_performance(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras agrupadas comparando Faturamento e Lucro por Canal de Venda.
    """
    if df.empty:
        return go.Figure()

    canal_summary = (
        df.groupby("canal")
        .agg(Faturamento=("faturamento", "sum"), Lucro=("lucro", "sum"))
        .reset_index()
    )

    # Converte para formato longo para gráfico agrupado
    df_melted = pd.melt(
        canal_summary,
        id_vars=["canal"],
        value_vars=["Faturamento", "Lucro"],
        var_name="Métrica",
        value_name="Valor",
    )

    fig = px.bar(
        df_melted,
        x="canal",
        y="Valor",
        color="Métrica",
        barmode="group",
        color_discrete_sequence=[COLOR_PALETTE[0], COLOR_PALETTE[5]],
        labels={"Valor": "R$", "canal": "Canal de Venda"},
    )

    fig.update_traces(
        hovertemplate="<b>%{x}</b> (%{fullData.name})<br>Valor: R$ %{y:,.2f}<extra></extra>",
    )
    fig.update_yaxes(tickprefix="R$ ", gridcolor="#F1F5F9")
    return _apply_modern_layout(fig, "Desempenho por Canal de Venda")


def plot_payment_methods(df: pd.DataFrame) -> go.Figure:
    """
    Gráfico de barras de volume e percentual por meio de pagamento.
    """
    if df.empty:
        return go.Figure()

    pay_summary = (
        df.groupby("forma_pagamento")
        .agg(pedidos=("id_pedido", "count"), faturamento=("faturamento", "sum"))
        .reset_index()
        .sort_values(by="pedidos", ascending=False)
    )

    fig = px.bar(
        pay_summary,
        x="forma_pagamento",
        y="pedidos",
        color="forma_pagamento",
        color_discrete_sequence=COLOR_PALETTE,
        labels={"pedidos": "Total de Pedidos", "forma_pagamento": "Forma de Pagamento"},
    )

    fig.update_traces(
        texttemplate="%{y:,}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Pedidos: %{y:,}<extra></extra>",
        showlegend=False,
    )
    fig.update_yaxes(gridcolor="#F1F5F9")
    return _apply_modern_layout(fig, "Preferência por Forma de Pagamento")


# -------------------------------------------------------------
# 5. GERADOR GENÉRICO (FÁCIL EXTENSÃO / CRIAÇÃO DE NOVOS GRÁFICOS)
# -------------------------------------------------------------
def create_generic_chart(
    df: pd.DataFrame,
    chart_type: str,
    x: str,
    y: str = None,
    color: str = None,
    title: str = None,
) -> go.Figure:
    """
    Função utilitária para criar qualquer novo gráfico em apenas 1 linha de código!
    Tipos suportados: 'bar', 'line', 'area', 'pie', 'scatter', 'box'.
    """
    if df.empty:
        return go.Figure()

    chart_type = chart_type.lower()
    title_str = title or f"{chart_type.capitalize()} de {y or x}"

    if chart_type == "bar":
        # Se x e y forem fornecidos, agrupa se necessário
        if y in ["faturamento", "lucro", "quantidade"] and df[x].dtype == "object":
            df_plot = df.groupby(x)[y].sum().reset_index()
        else:
            df_plot = df
        fig = px.bar(df_plot, x=x, y=y, color=color, color_discrete_sequence=COLOR_PALETTE)

    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, color=color, color_discrete_sequence=COLOR_PALETTE)

    elif chart_type == "area":
        fig = px.area(df, x=x, y=y, color=color, color_discrete_sequence=COLOR_PALETTE)

    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y, hole=0.5, color_discrete_sequence=COLOR_PALETTE)

    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, color=color, color_discrete_sequence=COLOR_PALETTE)

    elif chart_type == "box":
        fig = px.box(df, x=x, y=y, color=color, color_discrete_sequence=COLOR_PALETTE)

    else:
        fig = px.bar(df, x=x, y=y, color=color, color_discrete_sequence=COLOR_PALETTE)

    return _apply_modern_layout(fig, title_str)

