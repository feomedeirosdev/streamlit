import streamlit as st
import pandas as pd

st.set_page_config(page_title="Finanças", page_icon=":moneybag:")

st.markdown("""

# Boas vindas
## Nosso APP Financeiro
Espero que você curta a experiência da nossa solução para organização financeira.

""")

# Widget de upload de dados
file_upload = st.file_uploader(label="Faça upload dos dados aqui", type=['csv', 'txt', 'tsv', 'dat'])

# Condicional de arquivo existente/carregado
if file_upload:

    # Leitura dos dados
    df = pd.read_csv(file_upload)

    # Sanitarizando datas
    df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y").dt.date

    df = df.rename(columns={
        "Valor": "Valor (R$)",
        "Instituição": "Banco"
        })

    # Exibição dos dados no APP

    ## Dados Brudos
    exp1 = st.expander("Dados Brutos")
    exp1.dataframe(df, hide_index=True)

    ## Bancos/Instiuição
    exp2 = st.expander("Bancos")

    ### Abas para diferentes visualizações
    tab_data, tab_history, tab_share = exp2.tabs(["Dados", "Histórico", "Distribuição"])

    with tab_data:
        df_banco = df.pivot_table(index="Data", columns="Banco", values="Valor (R$)")
        st.dataframe(df_banco)
    
    with tab_history:
        st.line_chart(df_banco)

    with tab_share:

        date = st.selectbox("Selecione a Data", options=df_banco.index)

        st.bar_chart(df_banco.loc[date])
