"""
Aplicação Principal de Business Intelligence (BI) com Streamlit, Plotly e DuckDB.
Modo Principal: F1 Business & Sports Intelligence (2010-2026) com Cross-Filtering Interativo.
Modo Alternativo: E-Commerce & Varejo (Dados Sintéticos Demo).
"""

from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

import data_manager
import charts
import ai_analyst
import f1_analytics

# -------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# -------------------------------------------------------------
st.set_page_config(
    page_title="Executive F1 & Business Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------------------
# 2. ESTILIZAÇÃO CUSTOMIZADA (CSS MODERNO)
# -------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Container de KPIs modernos */
        .kpi-card {
            background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 18px 22px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
            border-color: #CBD5E1;
        }
        .kpi-title {
            color: #64748B;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 6px;
        }
        .kpi-value {
            color: #0F172A;
            font-size: 1.85rem;
            font-weight: 800;
            line-height: 1.2;
        }
        .kpi-badge {
            display: inline-flex;
            align-items: center;
            font-size: 0.75rem;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 6px;
            margin-top: 6px;
        }
        .badge-green {
            color: #059669;
            background-color: #ECFDF5;
        }
        .badge-red {
            color: #DC2626;
            background-color: #FEF2F2;
        }
        .badge-blue {
            color: #2563EB;
            background-color: #EFF6FF;
        }

        /* Barra de Cross-Filtering Ativo */
        .cross-filter-banner {
            background: linear-gradient(90deg, #FEF2F2 0%, #FFF7ED 100%);
            border: 1px solid #FCA5A5;
            border-left: 5px solid #E10600;
            border-radius: 10px;
            padding: 10px 16px;
            margin-bottom: 12px;
            font-size: 0.9rem;
            color: #1E293B;
        }
        .cf-pill {
            display: inline-block;
            background-color: #E10600;
            color: #FFFFFF;
            font-weight: 600;
            font-size: 0.78rem;
            padding: 2px 10px;
            border-radius: 999px;
            margin-left: 6px;
        }

        .ai-response-box {
            background-color: #F8FAFC;
            border-left: 4px solid #E10600;
            border-radius: 0 10px 10px 0;
            padding: 16px 20px;
            margin-bottom: 20px;
        }

        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------------------
# 3. FUNÇÕES AUXILIARES DE CROSS-FILTERING (INTERATIVIDADE)
# -------------------------------------------------------------
if "cf_reset_id" not in st.session_state:
    st.session_state["cf_reset_id"] = 0


def _get_selected_points(chart_base_key: str) -> list:
    """Lê os pontos clicados/selecionados em um gráfico Plotly no Streamlit."""
    full_key = f"{chart_base_key}_{st.session_state['cf_reset_id']}"
    state = st.session_state.get(full_key)
    if not state:
        return []
    if isinstance(state, dict):
        return state.get("selection", {}).get("points", [])
    sel = getattr(state, "selection", None)
    if isinstance(sel, dict):
        return sel.get("points", [])
    return getattr(sel, "points", []) or []


def _extract_f1_cross_filters() -> dict:
    """
    Extrai todas as seleções feitas via clique nos gráficos de todas as abas
    para aplicar Cross-Filtering entre gráficos e KPIs.
    """
    cf = {
        "seasons_p1_streams": set(),
        "seasons_p1_us": set(),
        "teams_p2_fin": set(),
        "teams_p2_cap": set(),
        "seasons_p2_cap": set(),
        "circuits_p3_scatter": set(),
        "regions_p3_scatter": set(),
        "street_p3_bar": set(),
        "drivers_p4": set(),
        "teams_p4_eff": set(),
    }

    # Painel 1: Gráfico de Receitas (x = season)
    for pt in _get_selected_points("f1_p1_streams"):
        if pt.get("x") is not None:
            try:
                cf["seasons_p1_streams"].add(int(pt["x"]))
            except (ValueError, TypeError):
                pass

    # Painel 1: Gráfico Audiência EUA & DTS (x = season)
    for pt in _get_selected_points("f1_p1_us"):
        if pt.get("x") is not None:
            try:
                cf["seasons_p1_us"].add(int(pt["x"]))
            except (ValueError, TypeError):
                pass

    # Painel 2: Gráfico Orçamento vs Receita (x = team_name)
    for pt in _get_selected_points("f1_p2_fin"):
        if pt.get("x"):
            cf["teams_p2_fin"].add(str(pt["x"]))

    # Painel 2: Gráfico Convergência Cost Cap (customdata = [team_name, season], x = season)
    for pt in _get_selected_points("f1_p2_cap"):
        cdata = pt.get("customdata")
        if isinstance(cdata, (list, tuple)) and len(cdata) >= 1:
            cf["teams_p2_cap"].add(str(cdata[0]))
        if pt.get("x") is not None:
            try:
                cf["seasons_p2_cap"].add(int(pt["x"]))
            except (ValueError, TypeError):
                pass

    # Painel 3: Scatter Plot Circuitos (customdata = [region, circuit, grand_prix])
    for pt in _get_selected_points("f1_p3_scatter"):
        cdata = pt.get("customdata")
        if isinstance(cdata, (list, tuple)) and len(cdata) >= 2:
            cf["regions_p3_scatter"].add(str(cdata[0]))
            cf["circuits_p3_scatter"].add(str(cdata[1]))

    # Painel 3: Barras Circuito de Rua vs Pista Tradicional (x = "Circuito de Rua" | "Pista Tradicional")
    for pt in _get_selected_points("f1_p3_street"):
        if pt.get("x") == "Circuito de Rua":
            cf["street_p3_bar"].add(1)
        elif pt.get("x") == "Pista Tradicional":
            cf["street_p3_bar"].add(0)

    # Painel 4: Ranking de Pilotos (y = driver_name)
    for pt in _get_selected_points("f1_p4_drivers"):
        if pt.get("y"):
            cf["drivers_p4"].add(str(pt["y"]))

    # Painel 4: Eficiência Financeira por Equipe (x = team_name)
    for pt in _get_selected_points("f1_p4_team_eff"):
        if pt.get("x"):
            cf["teams_p4_eff"].add(str(pt["x"]))

    return cf


# -------------------------------------------------------------
# 4. DETECÇÃO E CARREGAMENTO DE DADOS
# -------------------------------------------------------------
@st.cache_data(show_spinner="Carregando datasets da Fórmula 1...")
def get_f1_data():
    return f1_analytics.load_f1_datasets()


@st.cache_data(show_spinner="Carregando dados sintéticos de demonstração...")
def get_retail_data(seed: int = 42):
    return data_manager.generate_sales_data(num_records=4500, days_back=180, seed=seed)


f1_tables = get_f1_data()
tem_f1 = not f1_tables.get("f1_business", pd.DataFrame()).empty

# -------------------------------------------------------------
# 5. BARRA LATERAL (FILTROS E CONTROLES)
# -------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏎️ **F1 & BI Studio Pro**")
    st.caption("Painel Executivo com Cross-Filtering")
    st.divider()

    # Seletor de Base de Dados
    opcoes_fonte = []
    if tem_f1:
        opcoes_fonte.append("🏁 F1 Business & Sports Intelligence (Base Kaggle)")
    opcoes_fonte.append("🛒 E-Commerce & Varejo (Dados Sintéticos Demo)")

    fonte_selecionada = st.selectbox(
        "Fonte de Dados Ativa:",
        options=opcoes_fonte,
        index=0,
    )

    is_f1_mode = "F1" in fonte_selecionada

    st.divider()

    if is_f1_mode:
        st.subheader("📅 Filtro de Temporadas")

        # Atalhos de Era
        c_era1, c_era2 = st.columns(2)
        with c_era1:
            if st.button("Liberty (2017+)", use_container_width=True):
                st.session_state["f1_season_range"] = (2017, 2026)
        with c_era2:
            if st.button("Cost Cap (2021+)", use_container_width=True):
                st.session_state["f1_season_range"] = (2021, 2026)

        if "f1_season_range" not in st.session_state:
            st.session_state["f1_season_range"] = (2010, 2026)

        temporadas = st.slider(
            "Selecione o intervalo de anos:",
            min_value=2010,
            max_value=2026,
            value=st.session_state["f1_season_range"],
            step=1,
        )

        st.divider()
        st.subheader("🏎️ Filtros Estratégicos")

        # Construtores
        df_team_raw = f1_tables.get("constructor_finances", pd.DataFrame())
        equipes_disponiveis = sorted(df_team_raw["team_name"].unique()) if not df_team_raw.empty else []
        sel_equipes = st.multiselect(
            "Construtores / Equipes:",
            options=equipes_disponiveis,
            default=equipes_disponiveis,
        )

        # Regiões dos GPs
        df_circ_raw = f1_tables.get("circuit_economics", pd.DataFrame())
        regioes_disponiveis = sorted(df_circ_raw["region"].unique()) if not df_circ_raw.empty else []
        sel_regioes = st.multiselect(
            "Regiões Geográficas:",
            options=regioes_disponiveis,
            default=regioes_disponiveis,
        )

        if st.button("🔄 Limpar Seleções de Gráficos", use_container_width=True):
            st.session_state["cf_reset_id"] += 1
            st.rerun()

    else:
        # Controles do modo de varejo sintético
        st.subheader("📅 Período de Análise")
        if "data_seed" not in st.session_state:
            st.session_state["data_seed"] = 42
        df_retail_raw = get_retail_data(st.session_state["data_seed"])
        min_d = df_retail_raw["data"].min().date()
        max_d = df_retail_raw["data"].max().date()
        date_range = st.date_input("Datas:", value=(max_d - timedelta(days=90), max_d))
        sel_equipes = []
        sel_regioes = []

    st.divider()
    st.caption(
        f"🦆 **DuckDB**: {'Ativo ⚡' if data_manager.HAS_DUCKDB else 'Modo Pandas'}<br>"
        "🖱️ **Cross-Filter**: Clique nas barras ou pontos",
        unsafe_allow_html=True,
    )


# =============================================================
# FLUXO 1: MODO FÓRMULA 1 BUSINESS & SPORTS INTELLIGENCE
# =============================================================
if is_f1_mode and tem_f1:
    s_min, s_max = temporadas
    rid = st.session_state["cf_reset_id"]

    # Base filtrada pelos controles da Barra Lateral
    df_f1_base = f1_tables["f1_business"]
    df_f1_base = df_f1_base[(df_f1_base["season"] >= s_min) & (df_f1_base["season"] <= s_max)].copy()

    df_team_base = f1_tables["constructor_finances"]
    df_team_base = df_team_base[(df_team_base["season"] >= s_min) & (df_team_base["season"] <= s_max)].copy()
    if sel_equipes:
        df_team_base = df_team_base[df_team_base["team_name"].isin(sel_equipes)]

    df_circ_base = f1_tables["circuit_economics"]
    df_circ_base = df_circ_base[(df_circ_base["season"] >= s_min) & (df_circ_base["season"] <= s_max)].copy()
    if sel_regioes:
        df_circ_base = df_circ_base[df_circ_base["region"].isin(sel_regioes)]

    df_race_base = f1_tables["race_results"]
    df_race_base = df_race_base[(df_race_base["season"] >= s_min) & (df_race_base["season"] <= s_max)].copy()

    df_driver_base = f1_tables["driver_standings"]
    df_driver_base = df_driver_base[(df_driver_base["season"] >= s_min) & (df_driver_base["season"] <= s_max)].copy()

    # Extrai filtros de clique ativo nos gráficos (Cross-Filtering)
    cf = _extract_f1_cross_filters()

    all_cf_seasons = cf["seasons_p1_streams"] | cf["seasons_p1_us"] | cf["seasons_p2_cap"]
    all_cf_teams = cf["teams_p2_fin"] | cf["teams_p2_cap"] | cf["teams_p4_eff"]
    all_cf_circuits = cf["circuits_p3_scatter"]
    all_cf_regions = cf["regions_p3_scatter"]
    all_cf_street = cf["street_p3_bar"]
    all_cf_drivers = cf["drivers_p4"]

    # DataFrames Globais Pós-Cross-Filter (para KPIs de Topo e Visões Cruzadas)
    df_f1_kpi = df_f1_base[df_f1_base["season"].isin(all_cf_seasons)] if all_cf_seasons else df_f1_base
    df_team_kpi = df_team_base.copy()
    if all_cf_seasons:
        df_team_kpi = df_team_kpi[df_team_kpi["season"].isin(all_cf_seasons)]
    if all_cf_teams:
        df_team_kpi = df_team_kpi[df_team_kpi["team_name"].isin(all_cf_teams)]

    df_circ_kpi = df_circ_base.copy()
    if all_cf_seasons:
        df_circ_kpi = df_circ_kpi[df_circ_kpi["season"].isin(all_cf_seasons)]
    if all_cf_circuits:
        df_circ_kpi = df_circ_kpi[df_circ_kpi["circuit"].isin(all_cf_circuits)]
    if all_cf_street:
        df_circ_kpi = df_circ_kpi[df_circ_kpi["is_street_circuit"].isin(all_cf_street)]

    # Cálculo dos KPIs Macroeconômicos (reage instantaneamente aos cliques nos gráficos!)
    kpis = f1_analytics.compute_macro_kpis(df_f1_kpi, df_team_kpi, df_circ_kpi)

    # Cabeçalho
    c_head, c_badge = st.columns([3, 1])
    with c_head:
        st.title("🏁 Fórmula 1: Business & Financial Intelligence")
        st.markdown(
            f"Analisando temporadas de **{s_min} até {s_max}** "
            f"| **Clique em qualquer barra ou ponto nos gráficos para filtrar os demais (Cross-Filtering)**."
        )
    with c_badge:
        st.markdown(
            "<div style='text-align: right; padding-top: 15px;'>"
            "<span style='background:#FEE2E2; color:#B91C1C; padding:6px 14px; border-radius:20px; font-weight:700; font-size:0.85rem;'>"
            "● CROSS-FILTERING ATIVO</span></div>",
            unsafe_allow_html=True,
        )

    # Banner de Cross-Filtering quando o usuário clicou em algum gráfico
    active_pills = []
    if all_cf_seasons:
        anos_str = ", ".join(str(y) for y in sorted(all_cf_seasons))
        active_pills.append(f"<span class='cf-pill'>📅 Ano(s): {anos_str}</span>")
    if all_cf_teams:
        eq_str = ", ".join(sorted(all_cf_teams))
        active_pills.append(f"<span class='cf-pill'>🏎️ Equipe(s): {eq_str}</span>")
    if all_cf_circuits:
        circ_str = ", ".join(sorted(all_cf_circuits))
        active_pills.append(f"<span class='cf-pill'>🏁 Circuito(s): {circ_str}</span>")
    if all_cf_street:
        st_str = ", ".join("Rua" if x == 1 else "Permanente" for x in sorted(all_cf_street))
        active_pills.append(f"<span class='cf-pill'>🛣️ Traçado: {st_str}</span>")
    if all_cf_drivers:
        drv_str = ", ".join(sorted(all_cf_drivers))
        active_pills.append(f"<span class='cf-pill'>🏆 Piloto(s): {drv_str}</span>")

    if active_pills:
        col_banner, col_clear = st.columns([4.2, 1])
        with col_banner:
            st.markdown(
                f"<div class='cross-filter-banner'>🎯 <b>Filtro por Clique nos Gráficos:</b> {''.join(active_pills)}</div>",
                unsafe_allow_html=True,
            )
        with col_clear:
            if st.button("✖ Limpar Filtro de Clique", type="primary", use_container_width=True):
                st.session_state["cf_reset_id"] += 1
                st.rerun()

    st.write("")

    # Linha de KPIs Executivos
    kcol1, kcol2, kcol3, kcol4 = st.columns(4)

    with kcol1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">💵 Receita Total F1 (FOM)</div>
                <div class="kpi-value">${kpis.get('faturamento_total_bilhoes', 0):,.2f}B</div>
                <div class="kpi-badge badge-blue">Média: ${kpis.get('faturamento_medio_anual', 0):,.0f}M/ano</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kcol2:
        # Se apenas anos pré-teto estiverem selecionados, exibe o resultado correspondente
        lucro_pos = kpis.get('lucro_medio_pos_cap', 0)
        if pd.isna(lucro_pos) or lucro_pos == 0:
            lucro_val = kpis.get('lucro_medio_pre_cap', 0) or 0.0
            label_era = "Resultado Médio (Período)"
        else:
            lucro_val = lucro_pos
            label_era = "Era Cost Cap (pós-2021)"
        badge_cls = "badge-green" if lucro_val >= 0 else "badge-red"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">🏎️ Lucro Médio das Equipes</div>
                <div class="kpi-value">${lucro_val:+,.1f}M</div>
                <div class="kpi-badge {badge_cls}">{label_era}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kcol3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">🏁 Taxas Pagas por Circuitos</div>
                <div class="kpi-value">${kpis.get('total_hosting_fees_bilhoes', 0):,.2f}B</div>
                <div class="kpi-badge badge-blue">Arrecadação de Hosting Fees</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kcol4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">📺 Audiência EUA por GP</div>
                <div class="kpi-value">{kpis.get('audiencia_us_atual', 0):.2f}M</div>
                <div class="kpi-badge badge-green">▲ Efeito Drive to Survive</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.write("")

    # ABAS DO PLANEJAMENTO ESTRATÉGICO
    tab_p1, tab_p2, tab_p3, tab_p4, tab_ai, tab_sql = st.tabs([
        "🏛️ Macro Finanças & Liberty Media",
        "🏎️ Equipes, Orçamentos & Cost Cap",
        "🗺️ Economia dos Circuitos & Geopolítica",
        "🏆 Eficiência & ROI Esportivo",
        "🤖 Pergunte aos Dados (AI Analyst)",
        "🦆 DuckDB SQL Playground",
    ])

    # ---------------------------------------------------------
    # PAINEL 1: MACRO FINANÇAS & LIBERTY MEDIA
    # ---------------------------------------------------------
    with tab_p1:
        st.subheader("Evolução Estratégica do Modelo de Negócios da F1")
        st.caption(
            "🖱️ **Dica Interativa:** Clique em um ponto/barra ou arraste uma caixa sobre um conjunto de temporadas "
            "em um gráfico para filtrar automaticamente o gráfico ao lado, os KPIs e a tabela abaixo."
        )

        # Gráfico 1 é filtrado pela seleção feita no Gráfico 2 (e vice-versa)
        df_p1_for_streams = (
            df_f1_base[df_f1_base["season"].isin(cf["seasons_p1_us"])]
            if cf["seasons_p1_us"]
            else df_f1_base
        )
        df_p1_for_us = (
            df_f1_base[df_f1_base["season"].isin(cf["seasons_p1_streams"])]
            if cf["seasons_p1_streams"]
            else df_f1_base
        )

        col_m1, col_m2 = st.columns([1.6, 1.4])
        with col_m1:
            fig_streams = f1_analytics.plot_f1_revenue_streams(df_p1_for_streams)
            st.plotly_chart(
                fig_streams,
                use_container_width=True,
                config=f1_analytics.COMMON_CONFIG,
                on_select="rerun",
                key=f"f1_p1_streams_{rid}",
            )

        with col_m2:
            fig_us = f1_analytics.plot_f1_us_audience_and_dts(df_p1_for_us)
            st.plotly_chart(
                fig_us,
                use_container_width=True,
                config=f1_analytics.COMMON_CONFIG,
                on_select="rerun",
                key=f"f1_p1_us_{rid}",
            )

        p1_seasons_sel = cf["seasons_p1_streams"] | cf["seasons_p1_us"]
        df_f1_table = df_f1_base[df_f1_base["season"].isin(p1_seasons_sel)] if p1_seasons_sel else df_f1_base

        with st.expander("📋 Ver Tabela de Indicadores Corporativos por Temporada", expanded=bool(p1_seasons_sel)):
            st.dataframe(
                df_f1_table.sort_values(by="season", ascending=False),
                use_container_width=True,
                column_config={
                    "season": st.column_config.NumberColumn("Temporada", format="%d"),
                    "total_revenue_usd_m": st.column_config.NumberColumn("Receita Total ($M)", format="$%.1fM"),
                    "race_promotion_fees_usd_m": st.column_config.NumberColumn("Taxas de GP ($M)", format="$%.1fM"),
                    "broadcast_media_usd_m": st.column_config.NumberColumn("Transmissão TV ($M)", format="$%.1fM"),
                    "sponsorship_usd_m": st.column_config.NumberColumn("Patrocínios ($M)", format="$%.1fM"),
                    "us_avg_race_viewers_m": st.column_config.NumberColumn("Audiência EUA (M)", format="%.2fM"),
                },
            )

    # ---------------------------------------------------------
    # PAINEL 2: EQUIPES, ORÇAMENTOS & COST CAP
    # ---------------------------------------------------------
    with tab_p2:
        st.subheader("Sustentabilidade dos Construtores & Teto Orçamentário")
        st.caption(
            "🖱️ **Dica Interativa:** Clique em qualquer equipe no gráfico da esquerda (ex: *Ferrari* ou *Red Bull Racing*) "
            "para isolar sua curva histórica no gráfico da direita e recalcular os KPIs do topo!"
        )

        # Gráfico da Esquerda (Barras) filtra pelos anos/equipes clicados no Gráfico da Direita
        df_team_for_fin = df_team_base.copy()
        if cf["seasons_p2_cap"]:
            df_team_for_fin = df_team_for_fin[df_team_for_fin["season"].isin(cf["seasons_p2_cap"])]
        if cf["teams_p2_cap"] and not cf["teams_p2_fin"]:
            df_team_for_fin = df_team_for_fin[df_team_for_fin["team_name"].isin(cf["teams_p2_cap"])]

        # Gráfico da Direita (Linhas) filtra pelas equipes clicadas no Gráfico da Esquerda
        df_team_for_cap = (
            df_team_base[df_team_base["team_name"].isin(cf["teams_p2_fin"])]
            if cf["teams_p2_fin"]
            else df_team_base
        )

        col_t1, col_t2 = st.columns(2)
        with col_t1:
            fig_fin = f1_analytics.plot_team_finances_comparison(df_team_for_fin)
            st.plotly_chart(
                fig_fin,
                use_container_width=True,
                config=f1_analytics.COMMON_CONFIG,
                on_select="rerun",
                key=f"f1_p2_fin_{rid}",
            )

        with col_t2:
            fig_cap = f1_analytics.plot_cost_cap_budget_convergence(df_team_for_cap)
            st.plotly_chart(
                fig_cap,
                use_container_width=True,
                config=f1_analytics.COMMON_CONFIG,
                on_select="rerun",
                key=f"f1_p2_cap_{rid}",
            )

        # Se o usuário clicou em uma equipe ou temporada, exibe o detalhamento financeiro
        p2_teams_sel = cf["teams_p2_fin"] | cf["teams_p2_cap"]
        if p2_teams_sel or cf["seasons_p2_cap"]:
            df_team_detail = df_team_base.copy()
            if p2_teams_sel:
                df_team_detail = df_team_detail[df_team_detail["team_name"].isin(p2_teams_sel)]
            if cf["seasons_p2_cap"]:
                df_team_detail = df_team_detail[df_team_detail["season"].isin(cf["seasons_p2_cap"])]
            df_team_detail["lucro_liquido_usd_m"] = (
                df_team_detail["total_revenue_usd_m"] - df_team_detail["operating_budget_usd_m"]
            ).round(1)
            st.markdown("##### 📊 Detalhamento da Seleção de Equipe(s)")
            st.dataframe(
                df_team_detail[
                    ["season", "team_name", "operating_budget_usd_m", "total_revenue_usd_m", "lucro_liquido_usd_m", "prize_money_usd_m"]
                ].sort_values(by="season", ascending=False),
                use_container_width=True,
            )

        st.info(
            "💡 **Insight Analítico:** Antes de 2021, equipes como Mercedes, Ferrari e Red Bull "
            "gastavam mais de **$400M por temporada**, acumulando prejuízos. Com o teto de gastos fixado em torno de $135M-$145M, "
            "as equipes atingiram lucro operacional médio de **+$75.4M ao ano**."
        )

    # ---------------------------------------------------------
    # PAINEL 3: ECONOMIA DOS CIRCUITOS & GEOPOLÍTICA
    # ---------------------------------------------------------
    with tab_p3:
        st.subheader("Economia dos Autódromos: Taxas vs. Público Presencial")
        st.caption(
            "🖱️ **Dica Interativa:** Clique em um ponto (ou selecione vários com a caixa) no gráfico de dispersão para "
            "filtrar a rosca regional e o gráfico de traçados abaixo — ou clique em *Circuito de Rua* no gráfico inferior para filtrar o mapa de dispersão!"
        )

        # Scatter Plot é filtrado caso o usuário clique nas barras de "Circuito de Rua vs Pista Tradicional"
        df_circ_for_scatter = (
            df_circ_base[df_circ_base["is_street_circuit"].isin(cf["street_p3_bar"])]
            if cf["street_p3_bar"]
            else df_circ_base
        )

        # Donut Chart é filtrado tanto pelos circuitos clicados no Scatter quanto pelo tipo de traçado clicado abaixo
        df_circ_for_donut = df_circ_base.copy()
        if cf["circuits_p3_scatter"]:
            df_circ_for_donut = df_circ_for_donut[df_circ_for_donut["circuit"].isin(cf["circuits_p3_scatter"])]
        if cf["street_p3_bar"]:
            df_circ_for_donut = df_circ_for_donut[df_circ_for_donut["is_street_circuit"].isin(cf["street_p3_bar"])]

        # Barras de Rua vs Permanente são filtradas pelos circuitos clicados no Scatter Plot
        df_circ_for_street = (
            df_circ_base[df_circ_base["circuit"].isin(cf["circuits_p3_scatter"])]
            if cf["circuits_p3_scatter"]
            else df_circ_base
        )

        col_c1, col_c2 = st.columns([1.7, 1.3])
        with col_c1:
            fig_scatter = f1_analytics.plot_circuit_fees_vs_attendance(df_circ_for_scatter)
            st.plotly_chart(
                fig_scatter,
                use_container_width=True,
                config=f1_analytics.COMMON_CONFIG,
                on_select="rerun",
                key=f"f1_p3_scatter_{rid}",
            )

        with col_c2:
            fig_donut = f1_analytics.plot_regional_fees_donut(df_circ_for_donut)
            st.plotly_chart(
                fig_donut,
                use_container_width=True,
                config=f1_analytics.COMMON_CONFIG,
                key=f"f1_p3_donut_{rid}",
            )

        st.divider()
        st.subheader("Circuitos de Rua vs. Pistas Tradicionais (Clique nas barras para filtrar acima)")
        fig_street = f1_analytics.plot_street_vs_permanent(df_circ_for_street, df_race_base)
        st.plotly_chart(
            fig_street,
            use_container_width=True,
            config=f1_analytics.COMMON_CONFIG,
            on_select="rerun",
            key=f"f1_p3_street_{rid}",
        )

    # ---------------------------------------------------------
    # PAINEL 4: EFICIÊNCIA & DESEMPENHO ESPORTIVO
    # ---------------------------------------------------------
    with tab_p4:
        st.subheader("Retorno sobre Investimento Esportivo & Conquistas")
        st.caption(
            "🖱️ **Dica Interativa:** Clique em uma barra de piloto à esquerda ou de equipe à direita para "
            "filtrar as corridas vencidas e o histórico da seleção logo abaixo!"
        )

        col_e1, col_e2 = st.columns([1.4, 1.6])
        with col_e1:
            fig_drivers = f1_analytics.plot_driver_championship_wins(df_driver_base)
            st.plotly_chart(
                fig_drivers,
                use_container_width=True,
                config=f1_analytics.COMMON_CONFIG,
                on_select="rerun",
                key=f"f1_p4_drivers_{rid}",
            )

        with col_e2:
            fig_team_eff = f1_analytics.plot_team_financial_efficiency(df_team_base, df_driver_base)
            st.plotly_chart(
                fig_team_eff,
                use_container_width=True,
                config=f1_analytics.COMMON_CONFIG,
                on_select="rerun",
                key=f"f1_p4_team_eff_{rid}",
            )

        if cf["drivers_p4"]:
            st.divider()
            drv_list = sorted(cf["drivers_p4"])
            st.markdown(f"##### 🏆 Histórico e Corridas Vencidas por: **{', '.join(drv_list)}**")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.caption("Temporadas e Títulos no Campeonato")
                st.dataframe(
                    df_driver_base[df_driver_base["driver_name"].isin(drv_list)].sort_values(by="season", ascending=False),
                    use_container_width=True,
                )
            with col_d2:
                st.caption("Grandes Prêmios Vencidos")
                st.dataframe(
                    df_race_base[df_race_base["winner"].isin(drv_list)][
                        ["season", "grand_prix", "circuit", "winner", "pole_position", "safety_car_periods"]
                    ].sort_values(by="season", ascending=False),
                    use_container_width=True,
                )

    # ---------------------------------------------------------
    # PAINEL 5: PERGUNTE AOS DADOS (AI ANALYST F1)
    # ---------------------------------------------------------
    with tab_ai:
        st.subheader("🤖 Assistente de IA: Pergunte aos Dados da F1")
        st.markdown(
            "Digite uma dúvida estratégica em linguagem natural ou clique em uma das sugestões abaixo. "
            "O assistente interpreta a questão e gera a análise executiva acompanhada do gráfico Plotly ideal."
        )

        sugestoes_f1 = [
            "🏎️ Qual o impacto do teto de gastos (cost cap)?",
            "📈 Como a Liberty Media mudou as receitas da F1?",
            "🏁 Quais circuitos pagam as maiores taxas de realização?",
            "📺 Como a série Drive to Survive e a audiência dos EUA cresceram?",
            "🏆 Qual piloto tem mais vitórias e títulos?",
            "🏙️ Qual a diferença entre circuitos de rua e tradicionais?",
        ]

        if "user_f1_q" not in st.session_state:
            st.session_state["user_f1_q"] = sugestoes_f1[0]

        cs1, cs2, cs3 = st.columns(3)
        cs4, cs5, cs6 = st.columns(3)

        if cs1.button(sugestoes_f1[0], use_container_width=True):
            st.session_state["user_f1_q"] = sugestoes_f1[0]
        if cs2.button(sugestoes_f1[1], use_container_width=True):
            st.session_state["user_f1_q"] = sugestoes_f1[1]
        if cs3.button(sugestoes_f1[2], use_container_width=True):
            st.session_state["user_f1_q"] = sugestoes_f1[2]
        if cs4.button(sugestoes_f1[3], use_container_width=True):
            st.session_state["user_f1_q"] = sugestoes_f1[3]
        if cs5.button(sugestoes_f1[4], use_container_width=True):
            st.session_state["user_f1_q"] = sugestoes_f1[4]
        if cs6.button(sugestoes_f1[5], use_container_width=True):
            st.session_state["user_f1_q"] = sugestoes_f1[5]

        st.write("")
        q_input = st.text_input("Sua pergunta sobre a Fórmula 1:", value=st.session_state["user_f1_q"])

        if q_input:
            with st.spinner("Analisando padrões e gerando visualização da F1..."):
                resp = ai_analyst.ask_f1_data(q_input, f1_tables)

            if resp.get("highlighted_metrics"):
                m_cols = st.columns(len(resp["highlighted_metrics"]))
                for i, (k, v) in enumerate(resp["highlighted_metrics"].items()):
                    with m_cols[i]:
                        st.metric(label=k, value=v)
                st.write("")

            st.markdown(
                f"""
                <div class="ai-response-box">
                    {resp['insight']}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if resp.get("figure"):
                st.plotly_chart(resp["figure"], use_container_width=True, config=f1_analytics.COMMON_CONFIG)

    # ---------------------------------------------------------
    # PAINEL 6: DUCKDB SQL PLAYGROUND (COM TODAS AS 5 TABELAS)
    # ---------------------------------------------------------
    with tab_sql:
        st.subheader("🦆 Playground SQL com DuckDB (5 Tabelas da F1)")
        st.markdown(
            "Todas as 5 planilhas estão registradas em memória no DuckDB: "
            "`f1_business`, `circuit_economics`, `constructor_finances`, `race_results` e `driver_standings`. "
            "Você pode executar consultas analíticas complexas e fazer `JOIN`s instantâneos!"
        )

        queries_f1_prontas = {
            "P1: Decomposição de Receita F1 por Era": """SELECT 
    season,
    CASE WHEN is_liberty_media_era = 1 THEN 'Liberty Media' ELSE 'Bernie / CVC' END AS era,
    total_revenue_usd_m AS receita_total,
    race_promotion_fees_usd_m AS taxas_gp,
    broadcast_media_usd_m AS transmissao_tv,
    sponsorship_usd_m AS patrocinios,
    us_avg_race_viewers_m AS audiencia_eua_m
FROM f1_business
ORDER BY season DESC;""",
            "P2: Rentabilidade das Equipes Pré vs Pós Cost Cap": """SELECT 
    team_name,
    in_cost_cap_era,
    ROUND(AVG(operating_budget_usd_m), 1) AS orcamento_medio,
    ROUND(AVG(total_revenue_usd_m), 1) AS receita_media,
    ROUND(AVG(total_revenue_usd_m - operating_budget_usd_m), 1) AS lucro_medio
FROM constructor_finances
GROUP BY team_name, in_cost_cap_era
ORDER BY lucro_medio DESC;""",
            "P3: Hosting Fee Médio e Público por Região": """SELECT 
    region,
    COUNT(*) AS total_corridas,
    ROUND(AVG(hosting_fee_usd_m_est), 1) AS taxa_media_m,
    ROUND(AVG(weekend_attendance_k), 0) AS publico_medio_k,
    ROUND(SUM(hosting_fee_usd_m_est), 1) AS faturamento_total_m
FROM circuit_economics
GROUP BY region
ORDER BY faturamento_total_m DESC;""",
            "P4: Top 10 Pilotos Mais Vitoriosos": """SELECT 
    driver_name,
    SUM(wins) AS total_vitorias,
    SUM(poles) AS total_poles,
    SUM(is_world_champion) AS titulos_mundiais,
    SUM(total_points) AS pontos_totais
FROM driver_standings
GROUP BY driver_name
ORDER BY total_vitorias DESC
LIMIT 10;""",
            "P5: JOIN entre Circuitos e Safety Cars de Corrida": """SELECT 
    c.grand_prix,
    c.circuit,
    c.region,
    c.is_street_circuit,
    ROUND(AVG(c.hosting_fee_usd_m_est), 1) AS taxa_media,
    ROUND(AVG(r.safety_car_periods), 1) AS media_safety_cars
FROM circuit_economics c
JOIN race_results r ON c.season = r.season AND c.grand_prix = r.grand_prix
GROUP BY c.grand_prix, c.circuit, c.region, c.is_street_circuit
ORDER BY media_safety_cars DESC
LIMIT 10;""",
        }

        q_sel = st.selectbox("Selecione uma Consulta Pronta do Planejamento:", list(queries_f1_prontas.keys()))
        sql_input = st.text_area("Consulta SQL:", value=queries_f1_prontas[q_sel], height=160)

        if st.button("▶️ Executar Consulta no DuckDB", type="primary"):
            try:
                ini = datetime.now()
                res_df = data_manager.execute_duckdb_multi_table(sql_input, f1_tables)
                ms = (datetime.now() - ini).total_seconds() * 1000
                st.success(f"Consulta executada com sucesso em **{ms:.2f} ms**! ({len(res_df)} linhas retornadas)")
                st.dataframe(res_df, use_container_width=True)
            except Exception as e:
                st.error(f"Erro ao executar consulta: {str(e)}")

# =============================================================
# FLUXO 2: MODO VAREJO / E-COMMERCE (DEMO COMPLEMENTAR)
# =============================================================
else:
    df_raw = get_retail_data(st.session_state.get("data_seed", 42))
    df_filtrado = data_manager.filter_sales_data(df=df_raw, only_completed=True)

    # Extrai seleção de categoria se o usuário clicou no gráfico de barras
    pts_cat = _get_selected_points("retail_cat_chart")
    cats_clicadas = [str(p.get("y")) for p in pts_cat if p.get("y")]

    df_kpi_retail = df_filtrado[df_filtrado["categoria"].isin(cats_clicadas)] if cats_clicadas else df_filtrado
    kpis = data_manager.calculate_kpis(df_kpi_retail)

    st.title("🛒 Dashboard de Vendas & E-Commerce (Demo Interativo)")
    if cats_clicadas:
        st.info(f"🎯 **Filtro por Clique Ativo:** Categoria = `{', '.join(cats_clicadas)}`")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Faturamento Total", f"R$ {kpis['faturamento_total']:,.2f}")
    with k2:
        st.metric("Total de Pedidos", f"{kpis['total_pedidos']:,}")
    with k3:
        st.metric("Ticket Médio", f"R$ {kpis['ticket_medio']:,.2f}")
    with k4:
        st.metric("Margem de Lucro", f"{kpis['margem_media']:.1f}%")

    st.write("")
    rid = st.session_state["cf_reset_id"]
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.plotly_chart(
            charts.plot_revenue_time_series(df_kpi_retail),
            use_container_width=True,
            config=charts.COMMON_CONFIG,
        )
    with col_r2:
        st.plotly_chart(
            charts.plot_revenue_by_category(df_filtrado),
            use_container_width=True,
            config=charts.COMMON_CONFIG,
            on_select="rerun",
            key=f"retail_cat_chart_{rid}",
        )
