import streamlit as st
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots

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


def plot_utc(df, variavel1, variavel2, ano):

        xlabel = 'Data'
        df = df[pd.to_datetime(df['Data']).dt.year == ano]

        # Criando subplots com 2 axes
        subplot_fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig1 = px.line(df, x= xlabel, y=df[variavel1].groupby(df[xlabel]).transform('mean'))
        fig2 = px.line(df, x= xlabel, y=df[variavel2].groupby(df[xlabel]).transform('mean'))

        # Configurando as cores
        color_fig1, color_fig2 = 'red', 'darkorange'
        fig1.update_traces(line=dict(color=color_fig1))
        fig2.update_traces(line=dict(color=color_fig2))
        subplot_fig.update_layout(
            yaxis=dict(title=variavel1, color=color_fig1),
            yaxis2=dict(title=variavel2, color=color_fig2),
        )

        # Modifica/Ajusta o yaxis para fig2
        fig2.update_traces(yaxis="y2")

        # Configuração dos subplots
        subplot_fig.add_traces(fig1.data + fig2.data)
        subplot_fig.update_layout(yaxis=dict(title=variavel1 + ' MÉDIA'), yaxis2=dict(title=variavel2 + ' MÉDIA'))

        return subplot_fig


########################################################################################
#######################         CÓDIGO         #########################################


logo1 = 'https://github.com/GustavoDasa/StreamlitApps/blob/main/Back/LogoPASTw.png?raw=true'
with st.sidebar:
    st.image(logo1, width=200, use_column_width="always")


st.title("PA:red[S]T - Plataforma de Análise de Séries Temporais")
st.write("Nesta plataforma você poderá analisar o comportamento da Série Temporal que desejar, de forma rápida e intuitiva. Aproveite!")




st.sidebar.header("1. Base de Dados")
# Opção para inserir URL ou API
data_source = st.sidebar.radio("Escolha a fonte de dados", ('Base Padrão','Upload de CSV', 'URL de Dados (CSV ou API)'))




if data_source == 'Base Padrão':
    df = load_files(url_padrao)
    with st.expander(":clipboard: Sobre a Base Padrão"):
        st.write('''
A base de dados padrão é o conjunto disponibilizado pelo INMET, no período de 2008 à 2024 da região de São Carlos - SP.

\
Descubra mais em nosso relatório através do link: 
    ''')

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


    st.title("Análise exploratória dos dados")
    st.write("Como primeiro passo, indicamos uma análise breve análise para conhecer um pouco melhor o comportamento dos dados")

    # Seção 2: Escolha das colunas de interesse
    st.subheader("Configuração do Conjunto de dados")

    # Selecionar a coluna de datas e a coluna de valores
    
    
    
    
    # Converter a coluna de df para datetime
#    df = df.dropna(subset=[coluna_data])  # Remover linhas com datas inválidas
    
    # Seção 3: Opções de análise
    st.sidebar.header("3. Análise de Séries Temporais")
    
    # Opção de análise: Média Móvel
    
    # Gerar a média móvel
    #df['Média Móvel'] = df[coluna_valores].rolling(window=window_size).mean()




    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Gráfico de Linhas", "Gráfico de Pontos", "Gráfico de Barras", "Gráfico de Caixa", "Base de dados"])
    with tab1:
        popover = st.popover("Filter items")
        with popover:
            f1, f2, f3 = st.columns(3)
            with f1:
                teste = st.toggle("Toggle de ativação")
            with f2:
                red = st.checkbox("Show red items.", True)
            with f3:
                blue = st.checkbox("Show blue items.", True)
            other = st.checkbox("other", True)

        col1, col2, col3 = st.columns(3)
        with col1:
            coluna_data = st.selectbox("Selecione o eixo X", list(df.columns))
            df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
        colunas.remove(str(coluna_data))
        with col2:
            coluna_valores = st.selectbox("Selecione o eixo Y", colunas,index=2)
        with col3:
            window_size = st.slider("Slider para seleção", 1, 360, 7)

        fig = px.line(df, x=coluna_data, y=coluna_valores)

        fig.update_traces(line_color='#e34444', line_width=1)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with tab2:
        fig = px.scatter(
            df,
            x=coluna_data,
            y=coluna_valores,
            color=coluna_valores,
            color_continuous_scale='reds'
        )

        # fig.update_traces(line_color='#e34444', line_width=1)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with tab3:
        fig = px.bar(
            df,
            x=coluna_data,
            y=coluna_valores,
            color=coluna_valores,
            color_continuous_scale='reds'
        )

        # fig.update_traces(line_color='#e34444', line_width=1)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
   
    with tab4:

        fig = px.box(df, y=coluna_valores)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with tab5:
        st.table(df.head(20))




    # Exibir os gráficos
    st.subheader("Gráficos de Séries Temporais")

    
    # Seção 4: Download de resultados


    st.sidebar.header("4. Baixar Resultados")
    csv = converter_para_csv(df)
    st.sidebar.download_button(label="Baixar Dados Processados", data=csv, file_name='serie_temporal.csv', mime='text/csv')



    

    variavel1 = 'TEMPERATURA DO AR - BULBO SECO, HORARIA (°C)'
    variavel2 = 'UMIDADE RELATIVA DO AR, HORARIA (%)'
    ano = 2023

    
    st.plotly_chart(plot_utc(df, variavel1, variavel2, ano), theme="streamlit", use_container_width=True)

else:
    st.subheader(''':sun_small_cloud:
:barely_sunny:
:sun_behind_cloud:
:partly_sunny_rain:
:sun_behind_rain_cloud:
:rain_cloud:
:snow_cloud:
:lightning:
:lightning_cloud:
Para Iniciar, insira uma base de dados...''')