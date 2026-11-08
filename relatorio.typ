#set page(
  paper: "a4",
  margin: (x: 2.5cm, top: 3cm, bottom: 2.5cm),
)

#set text(
  font: ("Arial", "Segoe UI"),
  size: 11pt,
  lang: "pt",
)

#set par(justify: true, leading: 0.8em)

// Cabeçalho / Título
#align(center)[
  #text(size: 20pt, weight: "bold", fill: rgb("#E10600"))[Fórmula 1: Business Intelligence]
  
  #v(0.3em)
  #text(size: 13pt, style: "italic", fill: rgb("#334155"))[
    Resumo Analítico da Base de Dados (2010 – 2026)
  ]
]

#v(1.5em)
#line(length: 100%, stroke: 0.8pt + rgb("#CBD5E1"))
#v(1em)

// Seção de Integrantes
#text(size: 12pt, weight: "bold", fill: rgb("#0F172A"))[Integrantes do Projeto:]

#v(0.5em)
#grid(
  columns: (1fr, 1fr),
  row-gutter: 0.8em,
  [• Gabriel Rodella De Assis],
  [• Vinicius Marquesin],
  [• Cleiton Rodrigues],
  [• Luana Abrantes],
  [• Douglas Felipe Mariano],
  [• Joice Soato Brito],
)

#v(1.5em)
#line(length: 100%, stroke: 0.8pt + rgb("#CBD5E1"))
#v(1.5em)

// Seção do Resumo da Base
#text(size: 14pt, weight: "bold", fill: rgb("#0F172A"))[Sobre a Base de Dados]

#v(0.6em)
A base de dados reúne informações corporativas, financeiras e esportivas da *Fórmula 1* ao longo de 17 temporadas (*2010 a 2026*), organizada em 5 tabelas principais:

+ *`f1_business` (Finanças da F1):* Faturamento global da categoria, direitos de transmissão na TV, patrocínios e audiência mundial impulsionada pela série _Drive to Survive_ da Netflix.
+ *`constructor_finances` (Equipes & Construtores):* Orçamento anual, patrocínios de escuderias e o impacto do *Teto Orçamentário* (_Cost Cap_) a partir de 2021, que tornou as equipes altamente lucrativas.
+ *`circuit_economics` (Circuitos & Autódromos):* Taxas pagas pelos países para sediar GPs (_Hosting Fees_), público presente no final de semana e comparação entre pistas tradicionais e circuitos de rua.
+ *`race_results` (Corridas):* Histórico detalhado de 337 provas, incluindo vencedores, poles positions e ocorrência de _Safety Cars_.
+ *`driver_standings` (Pilotos):* Classificação anual com pontos, vitórias, pódios e títulos mundiais.

#v(1.5em)
#rect(
  width: 100%,
  fill: rgb("#F8FAFC"),
  stroke: 1pt + rgb("#E2E8F0"),
  radius: 6pt,
  inset: 12pt,
)[
  #text(weight: "bold", fill: rgb("#0F172A"))[Objetivo Central:]
  
  #v(0.3em)
  Conectar as finanças corporativas e o impacto das novas mídias com o desempenho real das escuderias nas pistas, fornecendo indicadores chave de ROI, margens operacionais e expansão geopolítica do esporte.
]
