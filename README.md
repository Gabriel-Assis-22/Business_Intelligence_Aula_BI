# 🏎️ F1 Business & Sports Intelligence — Guia Rápido de Execução

Painel executivo de **Business Intelligence (BI)** focado em Fórmula 1 (2010–2026), desenvolvido com **Python**, **Streamlit**, **Plotly Express** e **DuckDB**.

---

## 👥 Integrantes do Projeto

- Gabriel Rodella De Assis
- Vinicius Marquesin
- Cleiton Rodrigues
- Luana Abrantes
- Douglas Felipe Mariano
- Joice Soato Brito

---

## 🚀 Como Rodar o Projeto

Escolha **uma** das opções abaixo:

### Opção 1: Via Docker (Mais Simples e Recomendada)

> **Pré-requisito:** Ter o [Docker Desktop](https://www.docker.com/) instalado e aberto.

1. Abra o terminal na raiz do projeto (`Business_Intelligence_Aula_BI`).
2. Execute o comando:
   ```bash
   docker compose up --build
   ```
3. Aguarde o build e abra no navegador:
   👉 **[http://localhost:8501](http://localhost:8501)**
4. Para encerrar a aplicação:
   ```bash
   docker compose down
   ```

---

### Opção 2: Execução Local com Python

> **Pré-requisitos:** Python 3.11 ou 3.12 instalado.

1. Abra o terminal na pasta do projeto:
   ```bash
   cd c:\Users\gabri\Documents\GitHub\Business_Intelligence_Aula_BI
   ```

2. *(Opcional, porém recomendado)* Crie e ative um ambiente virtual:
   - **Windows (PowerShell):**
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie o dashboard:
   ```bash
   streamlit run app.py
   ```

5. O navegador abrirá automaticamente em:
   👉 **[http://localhost:8501](http://localhost:8501)**

---

## 📊 O que Você Vai Ver na Aplicação

O dashboard conta com 6 visões analíticas principais:

1. **🏛️ Macro Finanças & Liberty Media:** Evolução das 4 fontes de receita da F1, audiência nos EUA e correlação com a série *Drive to Survive* da Netflix.
2. **🏎️ Equipes & Cost Cap:** Comparativo de orçamento vs. receita e o impacto da introdução do teto de gastos a partir de 2021.
3. **🗺️ Economia dos Circuitos:** Relação entre taxa paga pelos autódromos (*Hosting Fees*), público de fim de semana e circuitos de rua vs. tradicionais.
4. **🏆 Eficiência & Desempenho Esportivo:** Ranking dos pilotos com mais vitórias/títulos e retorno esportivo sobre o investimento dos construtores.
5. **🤖 Pergunte aos Dados (AI Analyst):** Campo em linguagem natural com sugestões de 1 clique que gera respostas e gráficos dinâmicos instantaneamente.
6. **🦆 DuckDB SQL Playground:** Console interativo para rodar consultas SQL em tempo real com `JOIN`s diretos sobre as 5 planilhas.

---

## 📁 Estrutura de Arquivos

```text
Business_Intelligence_Aula_BI/
│
├── data/                                # Base de dados da F1 (5 planilhas Kaggle)
│   ├── f1_business.csv                  # Macro finanças da F1 e audiência
│   ├── circuit_economics.csv            # Taxas e público dos autódromos
│   ├── constructor_finances.csv         # Finanças das 10 equipes e Cost Cap
│   ├── race_results.csv                 # Resultados de 337 corridas
│   └── driver_standings.csv             # Classificação anual de pilotos
│
├── app.py                               # Interface web do Streamlit
├── f1_analytics.py                      # Funções de KPIs e gráficos Plotly da F1
├── ai_analyst.py                        # Motor do 'Pergunte aos Dados' (NLP)
├── data_manager.py                      # Conector e engine SQL DuckDB/Pandas
├── charts.py                            # Paleta e layouts de gráficos
├── relatorio.typ                        # Código fonte do resumo em Typst
├── relatorio.pdf                        # Resumo executivo exportado em PDF
├── PLANEJAMENTO_BI.md                   # Documentação detalhada e DER relacional
├── Dockerfile                           # Imagem do container Docker
├── docker-compose.yml                   # Orquestrador do container
├── requirements.txt                     # Dependências Python
└── README.md                            # Este guia de execução
```

---

## ⚠️ Solução de Dúvidas / Problemas Frequentes

- **A porta 8501 já está em uso?**  
  Execute `streamlit run app.py --server.port 8502` para abrir em outra porta.
- **Erro de permissão no PowerShell ao ativar `.venv`?**  
  Execute `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` no terminal antes do script de ativação.
- **Exportar novamente o relatório em PDF?**  
  Execute:
  ```bash
  typst compile relatorio.typ relatorio.pdf
  ```
