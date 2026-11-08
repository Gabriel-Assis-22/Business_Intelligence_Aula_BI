# 📁 Pasta de Dados (Kaggle / Local)

Coloque aqui os seus arquivos de dados (ex: planilhas baixadas do Kaggle).

### Formatos suportados:
- `.csv` (separado por vírgula ou ponto-e-vírgula)
- `.xlsx` ou `.xls` (planilhas do Excel)
- `.parquet`

### Como funciona:
1. Cole seus 5 arquivos (ou sua planilha com múltiplas abas) diretamente nesta pasta `data/`.
2. Como esta pasta está mapeada no Docker (`volumes: ./data:/app/data`), o container enxerga seus arquivos **em tempo real**, sem precisar reconstruir o container!
3. Na aplicação web, o Streamlit detectará automaticamente os arquivos encontrados e permitirá inspecionar, cruzar tabelas via DuckDB/SQL ou utilizá-los no dashboard.

