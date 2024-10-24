import streamlit as st
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

url_padrao = 'https://raw.githubusercontent.com/GustavoDasa/StreamlitApps/refs/heads/main/Back/base_inmet_08_24.csv'
 
st.set_page_config(page_title="PAST - Plataforma de Análise de Séries Temporais",initial_sidebar_state='expanded', page_icon=":chart_with_upwards_trend:", layout="wide")


########################################################################################
#######################         FUNÇÕES         ########################################

@st.cache_data
def load_files(site):
    df = pd.read_csv(site)
    return df

# Função para plotar o gráfico
def plot_series(df, coluna_data, coluna_valores):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df[coluna_data], df[coluna_valores], label="Dados Originais", color='blue')
    ax.plot(df[coluna_data], df['Média Móvel'], label=f"Média Móvel ({window_size} dias)", color='orange')
    ax.set_xlabel('Data')
    ax.set_ylabel(coluna_valores)
    ax.set_title("Análise de Série Temporal")
    ax.legend()
    st.pyplot(fig)

def converter_para_csv(df):
    return df.to_csv(index=False).encode('utf-8')


########################################################################################
#######################         CÓDIGO         #########################################


logo1 = 'https://github.com/GustavoDasa/StreamlitApps/blob/main/Back/LogoPASTw.png?raw=true'
with st.sidebar:
    st.image(logo1, width=200, use_column_width="always")


st.title("PA:red[S]T - Plataforma de Análise de Séries Temporais")
st.write("Nesta plataforma você poderá analisar o comportamento da Série Temporal que desejar, de forma rápida e intuitiva. Aproveite!")


st.title("Análise de Séries Temporais")

st.sidebar.header("1. Base de Dados")
# Opção para inserir URL ou API
data_source = st.sidebar.radio("Escolha a fonte de dados", ('Base Padrão','Upload de CSV', 'URL de Dados (CSV ou API)'))




if data_source == 'Base Padrão':
    df = load_files(url_padrao)
if data_source == 'Upload de CSV':
    uploaded_file = st.sidebar.file_uploader("Carregar arquivo CSV", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Dados carregados com sucesso!")
        st.write(df.head())
if data_source == 'URL de Dados (CSV ou API)':
    url = st.sidebar.text_input("Insira a URL de um CSV ou API de dados")
    if url:
        df = load_files(url)



# Se os dados forem carregados, prosseguir para a análise
if 'df' in locals():

    colunas = list(df.columns)

    st.sidebar.header("2. Configuração da Análise")
    
    # Seção 2: Escolha das colunas de interesse
    st.subheader("Configurar Série Temporal")

    # Selecionar a coluna de datas e a coluna de valores
    col1, col2, col3 = st.columns(3)
    with col1:
        coluna_data = st.selectbox("Selecione a coluna de data", list(df.columns))
    colunas.remove(str(coluna_data))
    with col2:
        coluna_valores = st.selectbox("Selecione a coluna de valores", colunas,index=2)
    with col3:
        window_size = st.slider("Selecione o tamanho da janela para a média móvel", 1, 360, 7)
    
    
    teste = st.toggle("Selecione a coluna de valores")
    
    
    # Converter a coluna de df para datetime
    df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
    df = df.dropna(subset=[coluna_data])  # Remover linhas com datas inválidas
    
    # Seção 3: Opções de análise
    st.sidebar.header("3. Análise de Séries Temporais")
    
    # Opção de análise: Média Móvel
    
    # Gerar a média móvel
    df['Média Móvel'] = df[coluna_valores].rolling(window=window_size).mean()


    fig = px.scatter(
        df,
        x=coluna_data,
        y=coluna_valores,
        color=coluna_valores,
        color_continuous_scale="reds",
    )


    tab1, tab2 = st.tabs(["Streamlit theme (default)", "Plotly native theme"])
    with tab1:
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    with tab2:
        st.plotly_chart(fig, theme=None, use_container_width=True)

    # Exibir os gráficos
    st.subheader("Gráficos de Séries Temporais")

    
    # Seção 4: Download de resultados


    st.sidebar.header("4. Baixar Resultados")
    csv = converter_para_csv(df)
    st.sidebar.download_button(label="Baixar Dados Processados", data=csv, file_name='serie_temporal.csv', mime='text/csv')

else:
    st.subheader("Para Iniciar, Selecione uma base de dados")