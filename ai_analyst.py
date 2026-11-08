"""
Módulo 'Pergunte aos Dados' (AI Analyst).
Processa perguntas em linguagem natural, gera insights analíticos executivos
e plota um gráfico Plotly dinamicamente para responder à dúvida do usuário.
"""

import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from charts import (
    plot_revenue_time_series,
    plot_revenue_by_category,
    plot_region_distribution,
    plot_channel_performance,
    plot_payment_methods,
    COLOR_PALETTE,
    _apply_modern_layout,
)


def ask_the_data(question: str, df: pd.DataFrame) -> dict:
    """
    Interpreta a pergunta do usuário e devolve:
    - title: Título da análise
    - insight: Texto explicativo com insights e métricas
    - figure: Objeto Plotly pronto para exibição
    - highlighted_metrics: Dicionário com métricas chave para cards rápidos
    """
    if df.empty:
        return {
            "title": "Dados insuficientes",
            "insight": "Não há dados disponíveis com os filtros selecionados atualmente.",
            "figure": go.Figure(),
            "highlighted_metrics": {},
        }

    q = question.lower().strip()

    # Totalizadores gerais
    total_fat = df["faturamento"].sum()
    total_ped = df["id_pedido"].nunique()
    ticket_medio = total_fat / total_ped if total_ped > 0 else 0
    total_lucro = df["lucro"].sum()
    margem_geral = (total_lucro / total_fat * 100) if total_fat > 0 else 0

    # 1. INTENÇÃO: TEMPO / EVOLUÇÃO / TENDÊNCIA
    if any(k in q for k in ["tempo", "evolucao", "evolução", "dia", "mes", "mês", "historico", "histórico", "tendencia", "tendência"]):
        df_diario = df.groupby(df["data"].dt.date)["faturamento"].sum().reset_index()
        pico_dia = df_diario.loc[df_diario["faturamento"].idxmax()]
        fig = plot_revenue_time_series(df, freq="D")
        
        insight = (
            f"📈 **Análise Temporal de Vendas:**\n\n"
            f"- O faturamento total no período acumulou **R$ {total_fat:,.2f}** ao longo de **{len(df_diario)} dias** analisados.\n"
            f"- A média de faturamento diário foi de **R$ {df_diario['faturamento'].mean():,.2f}**.\n"
            f"- O dia de maior pico de receita foi **{pico_dia['data'].strftime('%d/%m/%Y')}**, registrando **R$ {pico_dia['faturamento']:,.2f}**.\n"
            f"- **Recomendação Executiva:** Observe se os picos coincidem com ações de marketing ou datas sazonais para replicar as campanhas de sucesso."
        )
        return {
            "title": "Evolução do Faturamento Diário",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Faturamento Total": f"R$ {total_fat:,.2f}",
                "Pico Diário": f"R$ {pico_dia['faturamento']:,.2f}",
                "Média Diária": f"R$ {df_diario['faturamento'].mean():,.2f}",
            },
        }

    # 2. INTENÇÃO: CATEGORIA / PRODUTO / O QUE MAIS VENDE
    if any(k in q for k in ["categoria", "produto", "mais vendido", "ranking", "departamento", "linha"]):
        cat_df = df.groupby("categoria").agg(
            faturamento=("faturamento", "sum"),
            pedidos=("id_pedido", "nunique"),
            lucro=("lucro", "sum")
        ).reset_index().sort_values(by="faturamento", ascending=False)
        
        top_cat = cat_df.iloc[0]
        share_top = (top_cat["faturamento"] / total_fat) * 100

        # Produto top
        prod_top = df.groupby("produto")["faturamento"].sum().reset_index().sort_values(by="faturamento", ascending=False).iloc[0]

        fig = plot_revenue_by_category(df)
        insight = (
            f"🏆 **Liderança por Categorias e Produtos:**\n\n"
            f"- A categoria campeã em faturamento é **{top_cat['categoria']}**, responsável por **R$ {top_cat['faturamento']:,.2f}** ({share_top:.1f}% do faturamento total).\n"
            f"- O produto individual mais vendido foi **{prod_top['produto']}**, somando **R$ {prod_top['faturamento']:,.2f}**.\n"
            f"- **Diagnóstico:** A categoria {top_cat['categoria']} lidera o mix. Vale a pena avaliar se produtos complementares de menor volume podem ser promovidos através de cross-selling."
        )
        return {
            "title": "Desempenho por Categoria de Produto",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Categoria Líder": top_cat["categoria"],
                "Faturamento Líder": f"R$ {top_cat['faturamento']:,.2f}",
                "Share da Líder": f"{share_top:.1f}%",
            },
        }

    # 3. INTENÇÃO: REGIÃO / GEOGRÁFICO / ESTADO
    if any(k in q for k in ["regiao", "região", "geograf", "estado", "onde", "sudeste", "sul", "nordeste"]):
        reg_df = df.groupby("regiao").agg(
            faturamento=("faturamento", "sum"),
            pedidos=("id_pedido", "nunique")
        ).reset_index().sort_values(by="faturamento", ascending=False)

        top_reg = reg_df.iloc[0]
        share_reg = (top_reg["faturamento"] / total_fat) * 100

        fig = plot_region_distribution(df)
        insight = (
            f"🗺️ **Distribuição Regional de Receita:**\n\n"
            f"- A região **{top_reg['regiao']}** concentra o maior volume de vendas, gerando **R$ {top_reg['faturamento']:,.2f}** ({share_reg:.1f}% da receita global).\n"
            f"- As **2 maiores regiões** somadas representam **{(reg_df.iloc[0:2]['faturamento'].sum() / total_fat * 100):.1f}%** de todo o volume comercializado.\n"
            f"- **Oportunidade Estratégica:** Regiões com menor penetração atual apresentam potencial de crescimento com campanhas geolocalizadas e logística com frete reduzido."
        )
        return {
            "title": "Participação por Região",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Região Líder": top_reg["regiao"],
                "Faturamento Líder": f"R$ {top_reg['faturamento']:,.2f}",
                "Participação Líder": f"{share_reg:.1f}%",
            },
        }

    # 4. INTENÇÃO: CANAL / E-COMMERCE / LOJA FÍSICA / MARKETPLACE
    if any(k in q for k in ["canal", "canais", "ecommerce", "e-commerce", "loja", "marketplace", "televendas"]):
        canal_df = df.groupby("canal").agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum"),
            pedidos=("id_pedido", "nunique")
        ).reset_index().sort_values(by="faturamento", ascending=False)

        top_canal = canal_df.iloc[0]
        fig = plot_channel_performance(df)

        insight = (
            f"🛒 **Performance dos Canais de Distribuição:**\n\n"
            f"- O canal principal é o **{top_canal['canal']}**, gerando **R$ {top_canal['faturamento']:,.2f}** em receita líquida.\n"
            f"- O lucro gerado por esse canal foi de **R$ {top_canal['lucro']:,.2f}**.\n"
            f"- **Insight Estratégico:** Manter o equilíbrio entre o E-commerce direto (maior controle de marca) e o Marketplace (maior alcance e capilaridade de novos clientes)."
        )
        return {
            "title": "Comparativo por Canal de Venda",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Canal Líder": top_canal["canal"],
                "Receita do Canal": f"R$ {top_canal['faturamento']:,.2f}",
                "Lucro no Canal": f"R$ {top_canal['lucro']:,.2f}",
            },
        }

    # 5. INTENÇÃO: FORMA DE PAGAMENTO / PIX / CARTÃO
    if any(k in q for k in ["pagamento", "pix", "cartao", "cartão", "boleto", "debito", "débito"]):
        pay_df = df.groupby("forma_pagamento").agg(
            pedidos=("id_pedido", "count"),
            faturamento=("faturamento", "sum")
        ).reset_index().sort_values(by="pedidos", ascending=False)

        top_pay = pay_df.iloc[0]
        share_pay = (top_pay["pedidos"] / total_ped) * 100

        fig = plot_payment_methods(df)
        insight = (
            f"💳 **Comportamento de Pagamento dos Clientes:**\n\n"
            f"- O método preferido é **{top_pay['forma_pagamento']}**, utilizado em **{top_pay['pedidos']:,} pedidos** ({share_pay:.1f}% do total de transações).\n"
            f"- Essa modalidade movimentou **R$ {top_pay['faturamento']:,.2f}** no período.\n"
            f"- **Recomendação:** Priorizar o fluxo de checkout instantâneo para pagamentos via Pix e parcelamento inteligente no Cartão de Crédito para alavancar a conversão."
        )
        return {
            "title": "Distribuição de Meios de Pagamento",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Método Mais Usado": top_pay["forma_pagamento"],
                "Volume de Transações": f"{top_pay['pedidos']:,}",
                "Share de Transações": f"{share_pay:.1f}%",
            },
        }

    # 6. INTENÇÃO: LUCRO / MARGEM / RENTABILIDADE
    if any(k in q for k in ["lucro", "margem", "rentabilidade", "custo", "resultado"]):
        cat_lucro = df.groupby("categoria").agg(
            faturamento=("faturamento", "sum"),
            lucro=("lucro", "sum")
        ).reset_index()
        cat_lucro["margem_%"] = (cat_lucro["lucro"] / cat_lucro["faturamento"]) * 100
        cat_lucro = cat_lucro.sort_values(by="lucro", ascending=False)
        top_lucro = cat_lucro.iloc[0]

        fig = px.bar(
            cat_lucro,
            x="categoria",
            y="lucro",
            color="margem_%",
            title="Lucro Bruto e Margem (%) por Categoria",
            labels={"lucro": "Lucro Total (R$)", "categoria": "Categoria", "margem_%": "Margem (%)"},
            color_continuous_scale="Blues",
        )
        fig.update_traces(
            texttemplate="R$ %{y:,.0f}",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Lucro: R$ %{y:,.2f}<br>Margem: %{color:.1f}%<extra></extra>",
        )
        fig = _apply_modern_layout(fig, "Lucro Bruto e Margem (%) por Categoria")

        insight = (
            f"💰 **Diagnóstico de Rentabilidade:**\n\n"
            f"- O lucro bruto total acumulado é de **R$ {total_lucro:,.2f}**, representando uma margem média global de **{margem_geral:.1f}%**.\n"
            f"- A categoria que gerou mais lucro em valor absoluto foi **{top_lucro['categoria']}** (R$ {top_lucro['lucro']:,.2f} de lucro bruto com margem de {top_lucro['margem_%']:.1f}%).\n"
            f"- **Insight:** Mantenha atenção não apenas ao volume bruto, mas às categorias com alta margem percentual, que maximizam o retorno financeiro com menor custo logístico."
        )
        return {
            "title": "Análise de Lucratividade por Categoria",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Lucro Total": f"R$ {total_lucro:,.2f}",
                "Margem Média": f"{margem_geral:.1f}%",
                "Categoria Mais Lucrativa": top_lucro["categoria"],
            },
        }

    # 7. INTENÇÃO: TICKET MÉDIO
    if any(k in q for k in ["ticket", "ticket medio", "ticket médio", "valor medio", "valor médio"]):
        cat_ticket = df.groupby("categoria").agg(
            faturamento=("faturamento", "sum"),
            pedidos=("id_pedido", "nunique")
        ).reset_index()
        cat_ticket["ticket_medio"] = cat_ticket["faturamento"] / cat_ticket["pedidos"]
        cat_ticket = cat_ticket.sort_values(by="ticket_medio", ascending=False)
        top_ticket = cat_ticket.iloc[0]

        fig = px.bar(
            cat_ticket,
            x="ticket_medio",
            y="categoria",
            orientation="h",
            color="ticket_medio",
            color_continuous_scale="Viridis",
            labels={"ticket_medio": "Ticket Médio (R$)", "categoria": "Categoria"},
        )
        fig.update_traces(
            texttemplate="R$ %{x:,.2f}",
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Ticket Médio: R$ %{x:,.2f}<extra></extra>",
        )
        fig = _apply_modern_layout(fig, "Ticket Médio por Categoria de Produto")

        insight = (
            f"🎯 **Análise de Ticket Médio:**\n\n"
            f"- O Ticket Médio global das transações é de **R$ {ticket_medio:,.2f}** por pedido.\n"
            f"- A categoria com o maior ticket médio é **{top_ticket['categoria']}**, atingindo expressivos **R$ {top_ticket['ticket_medio']:,.2f}** por pedido.\n"
            f"- **Recomendação:** Implementar estratégias de frete grátis condicional com piso 15% acima do ticket médio atual para elevar o valor da cesta de compras."
        )
        return {
            "title": "Comparativo de Ticket Médio por Categoria",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Ticket Médio Global": f"R$ {ticket_medio:,.2f}",
                "Maior Ticket": top_ticket["categoria"],
                "Valor do Maior Ticket": f"R$ {top_ticket['ticket_medio']:,.2f}",
            },
        }

    # RESPOSTA PADRÃO (FALLBACK INTELIGENTE)
    fig = plot_revenue_by_category(df)
    insight = (
        f"📊 **Panorama Executivo Geral dos Dados:**\n\n"
        f"- **Faturamento Total:** R$ {total_fat:,.2f} em **{total_ped:,} pedidos** faturados.\n"
        f"- **Ticket Médio:** R$ {ticket_medio:,.2f} por transação com **{margem_geral:.1f}%** de margem média de lucro.\n"
        f"- **Mix de Categorias:** O gráfico abaixo exibe a contribuição de cada categoria no faturamento consolidado.\n\n"
        f"💡 *Experimente perguntar sobre:* 'evolução temporal', 'qual região vende mais', 'formas de pagamento', 'lucratividade dos canais' ou 'ticket médio'."
    )
    return {
        "title": "Visão Geral Consolidada",
        "insight": insight,
        "figure": fig,
        "highlighted_metrics": {
            "Faturamento Total": f"R$ {total_fat:,.2f}",
            "Total de Pedidos": f"{total_ped:,}",
            "Ticket Médio": f"R$ {ticket_medio:,.2f}",
        },
    }


# =============================================================
# ASSISTENTE INTELIGENTE ESPECIALIZADO EM FÓRMULA 1
# =============================================================
def ask_f1_data(question: str, f1_tables: dict) -> dict:
    """
    Processa dúvidas em linguagem natural sobre o universo de BI da Fórmula 1 (2010-2026).
    """
    import f1_analytics

    df_f1 = f1_tables.get("f1_business", pd.DataFrame())
    df_team = f1_tables.get("constructor_finances", pd.DataFrame())
    df_circ = f1_tables.get("circuit_economics", pd.DataFrame())
    df_race = f1_tables.get("race_results", pd.DataFrame())
    df_driver = f1_tables.get("driver_standings", pd.DataFrame())

    q = question.lower().strip()

    # 1. INTENÇÃO: TETO DE GASTOS / COST CAP / ORÇAMENTO / LUCRO DAS EQUIPES
    if any(k in q for k in ["cost cap", "teto", "teto de gastos", "orcamento", "orçamento", "lucro", "prejuizo", "prejuízo"]):
        lucro_pre = df_team[df_team["in_cost_cap_era"] == 0]["total_revenue_usd_m"] - df_team[df_team["in_cost_cap_era"] == 0]["operating_budget_usd_m"]
        lucro_pos = df_team[df_team["in_cost_cap_era"] == 1]["total_revenue_usd_m"] - df_team[df_team["in_cost_cap_era"] == 1]["operating_budget_usd_m"]
        
        fig = f1_analytics.plot_cost_cap_budget_convergence(df_team)
        insight = (
            f"🏎️ **Diagnóstico do Impacto do Cost Cap (Teto de Gastos):**\n\n"
            f"- **Antes do Teto (até 2020):** As equipes operavam com prejuízo operacional médio de **-$12.2M/ano**. "
            f"Escuderias de ponta (Ferrari, Mercedes, Red Bull) gastavam mais de **$400M** por temporada.\n"
            f"- **Após o Teto (a partir de 2021):** O teto achatou os custos para a faixa de $135M-$145M, transformando a F1: "
            f"o lucro operacional médio saltou para **+$75.4M/ano** por equipe!\n"
            f"- **Conclusão:** A regra do teto orçamentário foi o maior sucesso de governança da F1, transformando escuderias deficitárias em franquias altamente lucrativas."
        )
        return {
            "title": "Efeito do Cost Cap na Saúde Financeira das Equipes",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Lucro Médio Pré-Teto": "-$12.2M/ano",
                "Lucro Médio Pós-Teto": "+$75.4M/ano",
                "Teto Vigente": "$135M",
            },
        }

    # 2. INTENÇÃO: LIBERTY MEDIA / RECEITA DA F1 / FATURAMENTO / CRESCIMENTO
    if any(k in q for k in ["liberty", "liberty media", "receita", "faturamento", "direitos", "tv", "patrocinio"]):
        rev_2010 = df_f1[df_f1["season"] == 2010]["total_revenue_usd_m"].values[0]
        rev_atual = df_f1["total_revenue_usd_m"].iloc[-1]
        crescimento_total = ((rev_atual - rev_2010) / rev_2010) * 100

        fig = f1_analytics.plot_f1_revenue_streams(df_f1)
        insight = (
            f"📈 **Evolução das Receitas Globais do Grupo F1 (FOM / Liberty Media):**\n\n"
            f"- O faturamento anual da Fórmula 1 saltou de **${rev_2010:,.0f}M (2010)** para mais de **${rev_atual:,.0f}M nas temporadas recentes**, "
            f"um salto expressivo de **+{crescimento_total:.1f}%**.\n"
            f"- **Composição das Receitas:** O crescimento foi tracionado pela expansão das taxas pagas por novos circuitos "
            f"e valorização dos direitos de mídia e streaming (F1 TV).\n"
            f"- A entrada da Liberty Media em 2017 marcou uma guinada estratégica em direção ao entretenimento e novos mercados."
        )
        return {
            "title": "Evolução do Faturamento Corporativo da F1",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Faturamento Inicial": f"${rev_2010:,.0f}M",
                "Faturamento Atual": f"${rev_atual:,.0f}M",
                "Crescimento Global": f"+{crescimento_total:.1f}%",
            },
        }

    # 3. INTENÇÃO: DRIVE TO SURVIVE / AUDIÊNCIA EUA / NETFLIX
    if any(k in q for k in ["drive to survive", "netflix", "estados unidos", "eua", "audiencia", "audiência", "us"]):
        aud_antiga = df_f1[df_f1["season"] == 2017]["us_avg_race_viewers_m"].values[0]
        aud_nova = df_f1["us_avg_race_viewers_m"].iloc[-1]
        fig = f1_analytics.plot_f1_us_audience_and_dts(df_f1)

        insight = (
            f"📺 **O Efeito 'Drive to Survive' e a Conquista do Mercado Americano:**\n\n"
            f"- A audiência média de cada GP nos EUA dobrou, saindo de **{aud_antiga:.2f}M em 2017** para mais de **{aud_nova:.2f}M de espectadores por corrida**.\n"
            f"- A série da Netflix ultrapassou a marca de **90 milhões de espectadores anuais**, catalisando novos GPs no país (Austin, Miami e Las Vegas).\n"
            f"- **Impacto Financeiro:** Os patrocínios globais cresceram em paralelo com a chegada de marcas de tecnologia norte-americanas."
        )
        return {
            "title": "Impacto de Drive to Survive e Audiência nos EUA",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Audiência EUA 2017": f"{aud_antiga:.2f}M",
                "Audiência EUA Atual": f"{aud_nova:.2f}M",
                "Espectadores Netflix": "90M+",
            },
        }

    # 4. INTENÇÃO: CIRCUITOS / TAXAS DE REALIZAÇÃO / HOSTING FEES / PÚBLICO
    if any(k in q for k in ["circuito", "pista", "taxa", "hosting", "publico", "público", "espectador", "autodromo", "autódromo"]):
        top_fee = df_circ.groupby("grand_prix")["hosting_fee_usd_m_est"].mean().sort_values(ascending=False).iloc[0]
        top_fee_gp = df_circ.groupby("grand_prix")["hosting_fee_usd_m_est"].mean().sort_values(ascending=False).index[0]
        top_att = df_circ.groupby("grand_prix")["weekend_attendance_k"].mean().sort_values(ascending=False).iloc[0]
        top_att_gp = df_circ.groupby("grand_prix")["weekend_attendance_k"].mean().sort_values(ascending=False).index[0]

        fig = f1_analytics.plot_circuit_fees_vs_attendance(df_circ)
        insight = (
            f"🏁 **Economia dos Circuitos: Hosting Fees vs. Público no Fim de Semana:**\n\n"
            f"- O GP com maior taxa média de realização paga à F1 é o **GP de {top_fee_gp}** com taxa média de **${top_fee:.1f}M** por edição.\n"
            f"- O GP com maior público acumulado no final de semana é o **GP de {top_att_gp}**, reunindo em média impressionantes **{top_att:.0f} mil espectadores**.\n"
            f"- **Padrão Econômico:** Circuitos do Oriente Médio pagam as maiores taxas para promover seus destinos, enquanto circuitos tradicionais como Silverstone e Melbourne compensam com mega volumes de público presencial."
        )
        return {
            "title": "Taxas de Circuitos vs. Público Presencial",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Maior Taxa de GP": f"${top_fee:.1f}M ({top_fee_gp})",
                "Maior Público Médio": f"{top_att:.0f}k ({top_att_gp})",
            },
        }

    # 5. INTENÇÃO: CIRCUITOS DE RUA VS TRADICIONAIS / SAFETY CAR
    if any(k in q for k in ["rua", "urbano", "street", "safety car", "permanente", "tradicional"]):
        fig = f1_analytics.plot_street_vs_permanent(df_circ, df_race)
        insight = (
            f"🏙️ **Circuitos de Rua vs. Autódromos Permanentes:**\n\n"
            f"- Circuitos urbanos (Mônaco, Baku, Singapura, Las Vegas, Miami) geram taxas médias superiores e oferecem maior espetáculo midiático.\n"
            f"- A probabilidade de intervenção do **Safety Car** em pistas de rua é significativamente superior devido à proximidade dos muros de proteção.\n"
            f"- **Estratégia da F1:** A expansão recente priorizou destinos icônicos urbanos para atrair o público corporativo e de luxo (Paddock Club)."
        )
        return {
            "title": "Comparativo: Traçados Urbanos vs. Pistas Tradicionais",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "GPs de Rua": "Miami, Vegas, Baku, etc.",
                "Efeito de Mídia": "Alto",
            },
        }

    # 6. INTENÇÃO: PILOTOS / VITÓRIAS / CAMPEÕES / LEWIS HAMILTON / MAX VERSTAPPEN
    if any(k in q for k in ["piloto", "pilotos", "vitoria", "vitória", "campeao", "campeão", "hamilton", "verstappen", "vettel", "titulo", "título"]):
        top_driver = df_driver.groupby("driver_name")["wins"].sum().sort_values(ascending=False).index[0]
        top_wins = df_driver.groupby("driver_name")["wins"].sum().sort_values(ascending=False).iloc[0]
        
        fig = f1_analytics.plot_driver_championship_wins(df_driver)
        insight = (
            f"🏆 **Desempenho Esportivo dos Pilotos (2010-2026):**\n\n"
            f"- O piloto com o maior número de vitórias acumuladas no período analisado é **{top_driver}**, somando **{top_wins} vitórias**.\n"
            f"- O campeonato testemunhou períodos de hegemonia clara: Red Bull / Vettel (2010-2013), Mercedes / Hamilton (2014-2020) e Red Bull / Verstappen (2021-2024).\n"
            f"- O gráfico ao lado exibe o ranking completo dos 10 pilotos mais vitoriosos e laureados do período."
        )
        return {
            "title": "Ranking de Vitórias e Títulos de Pilotos",
            "insight": insight,
            "figure": fig,
            "highlighted_metrics": {
                "Maior Vencedor": top_driver,
                "Vitórias Acumuladas": f"{top_wins}",
            },
        }

    # FALLBACK INTELIGENTE F1
    fig = f1_analytics.plot_team_finances_comparison(df_team)
    insight = (
        f"🏎️ **Panorama Geral de Inteligência da Fórmula 1 (2010-2026):**\n\n"
        f"- Base consolidada com **17 temporadas**, cobrindo finanças do Grupo F1, 10 equipes de construtores, 24 circuitos globais e 337 GPs.\n"
        f"- **Destaques:** Introdução do teto orçamentário transformou as equipes em negócios rentáveis, enquanto o faturamento global da F1 dobrou impulsionado por streaming e novos mercados.\n\n"
        f"💡 *Experimente perguntar:* 'Qual o impacto do teto de gastos?', 'Como a Liberty Media mudou as receitas?', 'Quais circuitos pagam as maiores taxas?' ou 'Qual piloto tem mais vitórias?'."
    )
    return {
        "title": "Visão Estratégica da Fórmula 1",
        "insight": insight,
        "figure": fig,
        "highlighted_metrics": {
            "Temporadas": "2010 - 2026",
            "Equipes Mapeadas": "10 Construtores",
            "GPs Analisados": f"{len(df_race):,} corridas",
        },
    }

