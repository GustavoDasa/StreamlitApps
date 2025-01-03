############################   READ

# PAST - Plataforma de Análise de Séries Temporais

#   -------------------------------
#   Execute no prompt (CMD):
#   pip install streamlit
#   streamlit run PAST.py

#   Caso ainda não tenha instalado as bibliotecas:
#   pip install statsmodels
####################################

import streamlit as st
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.tsa.arima.model import ARIMA


url_padrao = 'https://raw.githubusercontent.com/GustavoDasa/StreamlitApps/refs/heads/main/Back/base_inmet_08_24_new.csv'

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


def decomposicao_serie_temporal(dados, df_data, variavel_y, freq=365, modelo='additive'):
    import pandas as pd
    from statsmodels.tsa.seasonal import seasonal_decompose
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    # Cria uma cópia do DataFrame com as colunas 'Data' e 'variavel_y'
    dados_copia = dados[[df_data, variavel_y]].copy()

    # Converte a coluna 'Data' para o tipo datetime, se ainda não estiver nesse formato
    dados_copia[df_data] = pd.to_datetime(dados_copia[df_data])

    # Extrai o dia e adiciona a coluna 'dia'
    dados_copia['dia'] = dados_copia[df_data].dt.to_period('D')

    # Calcula a média diária de 'variavel_y'
    dados_diario = dados_copia.groupby('dia')[variavel_y].mean().reset_index()
    dados_diario['dia'] = dados_diario['dia'].dt.to_timestamp()  # Converte 'dia' para datetime

    # Preenche valores nulos com o valor anterior
    if dados_diario[variavel_y].isnull().sum() > 0:
        dados_diario[variavel_y].fillna(method='ffill', inplace=True)

    # Realiza a decomposição da série temporal
    decomposicao = seasonal_decompose(dados_diario[variavel_y], model=modelo, period=int(freq))

    # Define um intervalo de tempo para visualização mais compacta
    intervalo_visao = 365  # Número de dias a serem exibidos
    dados_filtrados = dados_diario.iloc[-intervalo_visao:]  # Filtra os últimos 'intervalo_visao' dias

    # Cria subplots com 4 gráficos, um abaixo do outro
    subplot_fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                                subplot_titles=["Observado", "Tendência", "Sazonalidade", "Ruído"])

    # Observado
    subplot_fig.add_trace(go.Scatter(x=dados_filtrados['dia'], y=decomposicao.observed[-intervalo_visao:], mode='lines', name='Observado', line=dict(color='blue')),
                          row=1, col=1)

    # Tendência
    subplot_fig.add_trace(go.Scatter(x=dados_filtrados['dia'], y=decomposicao.trend[-intervalo_visao:], mode='lines', name='Tendência', line=dict(color='orange')),
                          row=2, col=1)

    # Sazonalidade
    subplot_fig.add_trace(go.Scatter(x=dados_filtrados['dia'], y=decomposicao.seasonal[-intervalo_visao:], mode='lines', name='Sazonalidade', line=dict(color='green')),
                          row=3, col=1)

    # Ruído
    subplot_fig.add_trace(go.Scatter(x=dados_filtrados['dia'], y=decomposicao.resid[-intervalo_visao:], mode='lines', name='Ruído', line=dict(color='red')),
                          row=4, col=1)

    # Layout do gráfico
    subplot_fig.update_layout(
        title=f'Decomposição da Série Temporal ({modelo})',
        yaxis_title='Valores',
        height=800,
        template='plotly_white'
    )

    # Ajuste no título e labels
    subplot_fig.update_layout(
        showlegend=False,
        title_text=f"Decomposição da Série Temporal ({modelo})",
        height=1000
    )

    return subplot_fig


def plot_autocorrelacao(dados, df_data, variavel_y, lags=24):
    import pandas as pd
    from statsmodels.tsa.stattools import acf
    import plotly.graph_objects as go

    # Cria uma cópia do DataFrame com as colunas 'Data' e 'variavel_y'
    dados_copia = dados[[df_data, variavel_y]].copy()

    # Converte a coluna 'Data' para o tipo datetime, se ainda não estiver nesse formato
    dados_copia[df_data] = pd.to_datetime(dados_copia[df_data])

    # Extrai o dia e adiciona a coluna 'dia'
    dados_copia['dia'] = dados_copia[df_data].dt.to_period('D')

    # Calcula a média diária de 'variavel_y'
    dados_diario = dados_copia.groupby('dia')[variavel_y].mean().reset_index()
    dados_diario['dia'] = dados_diario['dia'].dt.to_timestamp()  # Converte 'dia' para datetime

    # Preenche valores nulos com o valor anterior
    if dados_diario[variavel_y].isnull().sum() > 0:
        dados_diario[variavel_y].fillna(method='ffill', inplace=True)

    # Calcula a autocorrelação
    acf_vals = acf(dados_diario[variavel_y], nlags=lags)

    # Cria o gráfico de autocorrelação com Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(len(acf_vals))), y=acf_vals, name="Autocorrelação"))
    fig.update_layout(
        title="Função de Autocorrelação (ACF)",
        xaxis_title="Defasagens",
        yaxis_title="Autocorrelação",
        template="plotly_white"
    )

    return fig


def plot_autocorrelacao_parcial(dados, df_data, variavel_y, lags=24):


    # Cria uma cópia do DataFrame com as colunas 'Data' e 'variavel_y'
    dados_copia = dados[[df_data, variavel_y]].copy()

    # Converte a coluna 'Data' para o tipo datetime, se ainda não estiver nesse formato
    dados_copia[df_data] = pd.to_datetime(dados_copia[df_data])

    # Extrai o dia e adiciona a coluna 'dia'
    dados_copia['dia'] = dados_copia[df_data].dt.to_period('D')

    # Calcula a média diária de 'variavel_y'
    dados_diario = dados_copia.groupby('dia')[variavel_y].mean().reset_index()
    dados_diario['dia'] = dados_diario['dia'].dt.to_timestamp()  # Converte 'dia' para datetime

    # Calcula a autocorrelação parcial
    pacf_vals = pacf(dados_diario[variavel_y], nlags=lags)

    # Cria o gráfico de autocorrelação parcial com Plotly
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(len(pacf_vals))), y=pacf_vals, name="Autocorrelação Parcial"))
    fig.update_layout(
        title="Função de Autocorrelação Parcial (PACF)",
        xaxis_title="Defasagens",
        yaxis_title="Autocorrelação Parcial",
        template="plotly_white"
    )

    return fig




def plot_utc(df,df_data, variavel1, variavel2, ano):

    xlabel = df_data
    df = df[pd.to_datetime(df[df_data]).dt.year == ano]

    # Criando subplots com 2 axes
    subplot_fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig1 = px.line(df, x= xlabel, y=df[variavel1].groupby(df[xlabel]).transform('mean'))
    fig2 = px.line(df, x= xlabel, y=df[variavel2].groupby(df[xlabel]).transform('mean'))

    # Configurando as cores
    color_fig1, color_fig2 = 'red', 'darkorange'
    fig1.update_traces(line=dict(color=color_fig1))
    fig2.update_traces(line=dict(color=color_fig2))

    # Modifica/Ajusta o yaxis para fig2
    fig2.update_traces(yaxis="y2")

    # Configuração dos subplots
    subplot_fig.add_traces(fig1.data + fig2.data)
    subplot_fig.update_layout(yaxis=dict(title=variavel1 + ' MÉDIA'), yaxis2=dict(title=variavel2 + ' MÉDIA'))

    subplot_fig.update_layout(
        yaxis=dict(
            title=dict(text=variavel1, font=dict(color=color_fig1)),
            tickfont=dict(color=color_fig1)
        ),
        yaxis2=dict(
            title=dict(text=variavel2, font=dict(color=color_fig2)),
            tickfont=dict(color=color_fig2)
        ),
    )

    return subplot_fig



def modelos_ARIMA(dados, df_data, variavel_y, p, d, q):

    # Cria uma cópia do DataFrame com as colunas 'Data' e 'variavel_y'
    dados_copia = dados[[df_data, variavel_y]].copy()

    # Converte a coluna 'Data' para o tipo datetime, se ainda não estiver nesse formato
    dados_copia[df_data] = pd.to_datetime(dados_copia[df_data])

    # Extrai o dia e adiciona a coluna 'dia'
    dados_copia['dia'] = dados_copia[df_data].dt.to_period('D')

    # Calcula a média diária de 'variavel_y'
    dados_diario = dados_copia.groupby('dia')[variavel_y].mean().reset_index()
    dados_diario['dia'] = dados_diario['dia'].dt.to_timestamp()  # Converte 'dia' para datetime

    modelo = ARIMA(dados_diario[variavel_y], order=(p, d, q)).fit()

    # Valores ajustados (fitted values)
    fitted_values = modelo.fittedvalues

    # Gráfico com valores reais e ajustados
    fig = go.Figure()

    # Valores reais
    fig.add_trace(go.Scatter(
        x=dados_diario['dia'],
        y=dados_diario[variavel_y],
        mode='lines',
        name='Valores Reais',
        line=dict(color='darkorange')
    ))

    # Valores ajustados
    fig.add_trace(go.Scatter(
        x=dados_diario['dia'],
        y=fitted_values,
        mode='lines',
        name='Valores Ajustados',
        line=dict(color='red')
    ))

    # Layout do gráfico
    fig.update_layout(
        title=f"Comparação entre Valores Reais e Ajustados - ARIMA({p}, {d}, {q})",
        xaxis_title="Data",
        yaxis_title=variavel_y,
        legend=dict(x=0, y=1),
        template="plotly_white"
    )

    # Exibe o sumário no Streamlit
    st.markdown("#### Sumário do Modelo")
    st.text(modelo.summary())
    
    return fig

########################################################################################
#######################         CÓDIGO         #########################################


logo1 = 'https://github.com/GustavoDasa/StreamlitApps/blob/main/Back/LogoPASTw.png?raw=true'
with st.sidebar:
    st.image(logo1, width=200,  use_container_width="always")


st.title("PA:red[S]T - Plataforma de Análise de Séries Temporais", anchor='PAST')
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
Descubra mais em nosso relatório através do link: https://www.overleaf.com/project/66cbfb4d17c87ff66456c075
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
    df_data = st.sidebar.selectbox("Selecione a coluna de datas", list(df.columns))


    st.divider()
    st.subheader("Análise exploratória dos dados", anchor='EDA')#, divider='red')
    st.write(":gray[Como primeiro passo, indicamos uma breve análise para conhecer um pouco melhor o comportamento dos dados.]")

    #df['Média Móvel'] = df[coluna_valores].rolling(window=window_size).mean()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Gráfico de Linhas", "Gráfico de Pontos", "Gráfico de Barras", "Gráfico de Caixa", "Base de dados"])
    with tab1:
        popover = st.popover("Opções adicionais", help='Adicione complementos')
        with popover:
            f1, f2, f3 = st.columns(3)
            with f1:
                graf_duplo_y = st.toggle("Duplo eixo y", False)
            with f2:
                mm_1 = st.checkbox("Média Móvel", False)
            with f3:
                blue = st.checkbox("outros", False)
            if mm_1:
                window_size = st.slider("Janela da Média Móvel", 1, 360, 7)

        if graf_duplo_y:
            col1, col2, col3 = st.columns(3)
            with col1:
                variavel1 = st.selectbox('Selecione o primeiro eixo Y', list(df.columns), index = 5)
            with col2:
                variavel2 = st.selectbox('Selecione o segundo eixo Y', list(df.columns), index = 13)
            with col3:
                anos = (pd.to_datetime(df[df_data]).dt.year).unique()
                ano = st.selectbox('Selecione o ano da análise', anos, index = len(anos) - 1)

            st.plotly_chart(plot_utc(df, df_data, variavel1, variavel2, ano), use_container_width=True)

        else:
            col1, col2, col3, _,_ = st.columns(5)
            with col1:
                eixo_x = st.selectbox("Selecione o eixo X", list(df.columns))
            colunas.remove(str(eixo_x))
            with col2:
                eixo_y = st.selectbox("Selecione o eixo Y", colunas,index=2)
            fig = px.line(df, x=eixo_x, y=eixo_y)

            fig.update_traces(line_color='#e34444', line_width=1)
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with tab2:
        col1, col2, col3, _,_ = st.columns(5)
        with col1:
            eixo_x = st.selectbox("Selecione o eixo X.", list(df.columns))
        with col2:
            eixo_y = st.selectbox("Selecione o eixo Y.", colunas,index=2)
        fig = px.scatter(
            df,
            x=eixo_x,
            y=eixo_y,
            color=eixo_y,
            color_continuous_scale='reds'
        )

        # fig.update_traces(line_color='#e34444', line_width=1)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with tab3:
        col1, col2, col3, _ = st.columns(4)
        with col1:
            eixo_x = st.selectbox("Selecione a barra", list(df.columns))
        with col2:
            eixo_y = st.selectbox("Selecione os valores", colunas,index=2)
        fig = px.bar(
            df,
            x=eixo_x,
            y=eixo_y,
            color=eixo_y,
            color_continuous_scale='reds'
        )

        # fig.update_traces(line_color='#e34444', line_width=1)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with tab4:

        fig = px.box(df, y=eixo_y)
        fig.update_traces(marker_color = 'indianred', line_width=2)
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    with tab5:
        st.table(df.head(20))


    # st.markdown("<h4 style='color: gray;'>Gráfico Comparativo de Séries Temporais</h4>", unsafe_allow_html=True)

    st.divider()

    st.subheader("Gráficos de Séries Temporais")
    st.write(":gray[Para ter um pouco mais conhecimento sobre os seus dados, no aspecto temporal, indicamos a análise dos seguintes gráficos.]")

    tab1, tab2, tab3 = st.tabs(["Gráfico de decomposição", "Gráfico de autocorrelação", "Gráfico de autocorrelação parcial"])
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            variavel1 = st.selectbox('Selecione o eixo Y', list(df.columns), index = 5, key="variavely_decomp")
        with col2:
            modelo = st.radio("Selecione o modelo de decomposição", ('additive', 'multiplicative'), index=0, key="modelo_decomp")

        if modelo == 'additive':
            st.plotly_chart(decomposicao_serie_temporal(df,df_data, variavel1, freq=12, modelo='additive'), use_container_width=True)
        else:
            st.plotly_chart(decomposicao_serie_temporal(df,df_data, variavel1, freq=12, modelo='multiplicative'), use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            variavel1 = st.selectbox('Selecione a variável de interesse', list(df.columns), index = 5, key="variavely_lag")

        st.plotly_chart(plot_autocorrelacao(df,df_data, variavel1, lags=24), use_container_width=True)

        
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            variavel2 = st.selectbox('Selecione a variável de interesse', list(df.columns), index = 5, key="variavely_lag_parcial")

        st.plotly_chart(plot_autocorrelacao_parcial(df,df_data, variavel2, lags=24), use_container_width=True)



    st.divider()
    st.subheader("Modelos MA, AR, ARMA e ARIMA", anchor='Modelos')#, divider='red')
    st.write(":gray[Agora, com um maior conhecimento sobre o comportamento dos dados, indicamos ajustar alguns modelos.]")
    
    tab1, = st.tabs(["Modelos"])
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            variavel_y = st.selectbox('Selecione a variável de interesse', list(df.columns), index = 5, key="variavely_mod")
            
        with col2:
            p = st.selectbox('Parâmetro p', list(range(0, 11)), index = 2, key="variavely_mod_p")

        with col3:
            d = st.selectbox('Parâmetro d', list(range(0, 11)), index = 0, key="variavely_mod_d")
            
        with col4:
            q = st.selectbox('Parâmetro q', list(range(0, 11)), index = 3, key="variavely_mod_q")
            
        st.plotly_chart(modelos_ARIMA(df, df_data, variavel_y, p, d, q), use_container_width=True)
        
        
        
        

    # Seção 4: Download de resultados

    st.sidebar.header("4. Baixar Resultados")
    csv = converter_para_csv(df)
    st.sidebar.download_button(label="Baixar Dados Processados", data=csv, file_name='serie_temporal.csv', mime='text/csv')


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
