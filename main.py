import streamlit as st
import pandas as pd

def calc_stats(df):
    df = df.groupby(by="Data")[["Valor (R$)"]].sum()
    df["shift"] = df["Valor (R$)"].shift(1)
    df["Diff Mensal (abs) (R$)"] = (df["Valor (R$)"] - df["shift"]).fillna(0)
    df["Diff Mensal (rel) (%)"] = (((df["Valor (R$)"] / df["shift"])-1)*100).fillna(0)

    df["Avg Diff 6 (abs) (R$)"] = df["Diff Mensal (abs) (R$)"].rolling(6).mean().fillna(0)
    df["Evl 6 (abs) (R$)"] = df["Valor (R$)"].rolling(6).apply(lambda x: x[-1]-x[0]).fillna(0)
    df["Evl 6 (rel) (%)"] = df["Valor (R$)"].rolling(6).apply(lambda x: (((x[-1]/x[0])-1)*100)).fillna(0)
    # df["Amp_6 (R$)"] = df["Valor (R$)"].rolling(6).apply(lambda x: x.max()-x.min()).fillna(0)

    df = df.drop(columns=["shift"])

    return df

def formatar(df):

    def formatar_br(valor, prefixo="", sufixo=""):
        sinal = "- " if valor < 0 else ""
        valor_fmt = f"{abs(valor):_.2f}".replace(".", ",").replace("_", ".")
        return f"{sinal}{prefixo}{valor_fmt}{sufixo}"

    for col in df.columns:
        pfx = "R$ " if "(R$)" in col else ""
        sfx = "%" if "(%)" in col else ""
        if pfx or sfx:
            df[col] = df[col].apply(formatar_br, prefixo=pfx, sufixo=sfx)
    
    lst_values = []
    lst_keys = df.columns.tolist()
    for col in lst_keys:
        nova_col = col.replace(" (R$)", "").replace(" (%)", "")
        lst_values.append(nova_col)

    df = df.rename(columns=dict(zip(lst_keys, lst_values)))

    return df

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

    #### Exibe DataFrame
    with tab_data:
        df_banco = df.pivot_table(index="Data", columns="Banco", values="Valor (R$)")
        st.dataframe(df_banco)
    
    #### Exibe Histórico
    with tab_history:
        st.line_chart(df_banco)

    #### Exibe Distribuição
    with tab_share:
        ##### Filtro de Data
        date = st.selectbox("Selecione a Data", options=df_banco.index)
        ##### Gráfico da Distribuição
        st.bar_chart(df_banco.loc[date])

    ## Datas
    exp3 = st.expander("Estatísticas Gerais")

    df_stats = calc_stats(df)
    df_formated = formatar(df_stats.copy())

    abs_cols = [col for col in df_stats.columns.tolist() if "(abs)" in col]
    rel_cols = [col for col in df_stats.columns.tolist() if "(rel)" in col]

    tab_formated, tab_abs, tab_rel = exp3.tabs(["Dados", "Histórico de Evolução (R$)", "Crescimento Relativo (%)"])

    with tab_formated:
        st.dataframe(df_formated)
    with tab_abs:
        st.line_chart(df_stats[abs_cols])
    with tab_rel:
        st.line_chart(df_stats[rel_cols])

with st.expander("Metas"):

    col1, col2 = st.columns(2)

    # Col 1
    data_inicio_meta = col1.date_input("Início da Meta", max_value=df_stats.index.max())

    custos_fixos = col1.number_input("Custos Fixos", min_value=0., format="%.2f")

    filter_data = df_stats.index <= data_inicio_meta
    data_filtrada = df_stats.index[filter_data][-1]

    valor_inicio = df_stats.loc[data_filtrada]["Valor (R$)"]
    col1.markdown(f"**Valor no Início da Meta**: R$ {valor_inicio:.2f}")

    # Col 2
    salario_bruto = col2.number_input("Salário Bruto", min_value=0., format="%.2f")
    salario_liq = col2.number_input("Salário Líquido", min_value=0., format="%.2f")


    col1_pot, col2_pot = st.columns(2)
    mensal = salario_liq - custos_fixos
    anual =  mensal * 12
    with col1_pot.container(border=True):
        st.markdown(f"""**Potencial de arrecadação Mês**:\n\n R$ {mensal:.2f}""")
    with col2_pot.container(border=True):
        st.markdown(f"""**Potencial de arrecadação Ano**:\n\n R$ {anual:.2f}""")
    
    with st.container(border=True):
        col1_meta, col2_meta = st.columns(2)
        with col1_meta:
            st.number_input("Meta estipulada", min_value=0., format="%.2f", value=anual)
        with col2_meta:
            patrimonio_final = anual + valor_inicio
            st.markdown(f"""Patrimônio Estimado Pós Meta: \n\n R$ {patrimonio_final:.2f}""")

    
