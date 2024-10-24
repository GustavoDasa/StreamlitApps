import streamlit as st
import pandas as pd
import datetime
import numpy as np
import matplotlib.pyplot as plt


st.set_page_config(page_title="Data manager", page_icon=":material/edit:")


st.title("Escolha o Caminho a Seguir")

opcao = st.selectbox("Escolha um script para rodar:", ['Script 1: Análise Básica', 'Script 2: Análise Avançada'])



# Condicional para seguir com o fluxo escolhido
if opcao == 'Script 1: Análise Básica':
    st.subheader("Você escolheu o Script 1 - Análise Básica")


    # Título do app
    st.title("Aplicação Completa com Várias Ferramentas de Interatividade")

    # 1. Texto estático e entrada de texto
    st.header("1. Entrada de Texto")
    nome = st.text_input("Qual é o seu nome?")
    if nome:
        st.write(f"Olá, {nome}!")

    # 2. Slider para selecionar um número
    st.header("2. Slider")
    idade = st.slider('Selecione sua idade', 0, 100, 25)
    st.write(f'Sua idade é: {idade}')

    # 3. Selectbox para escolher uma fruta
    st.header("3. Selectbox")
    fruta = st.selectbox('Escolha uma fruta', ['Maçã', 'Banana', 'Laranja'])
    st.write(f'Você escolheu: {fruta}')

    # 4. Radio buttons para selecionar o sexo
    st.header("4. Botões de Rádio")
    sexo = st.radio("Selecione o sexo", ['Masculino', 'Feminino'])
    st.write(f'Você escolheu: {sexo}')

    # 5. Checkbox para saber se gosta de programar
    st.header("5. Checkbox")
    gosta_programar = st.checkbox('Você gosta de programar?')
    if gosta_programar:
        st.write("Que ótimo! Programar é divertido.")
    else:
        st.write("Tudo bem, cada um tem suas preferências.")

    # 6. File Uploader para upload de arquivo
    st.header("6. Upload de Arquivo")
    uploaded_file = st.file_uploader("Escolha um arquivo", type=["csv", "txt"])
    if uploaded_file is not None:
        st.write(f'Você carregou o arquivo: {uploaded_file.name}')

    # 7. Date input para selecionar uma data
    st.header("7. Seletor de Data")
    data = st.date_input("Escolha uma data", datetime.date.today())
    st.write(f'Data selecionada: {data}')

    # 8. Exibição condicional de dados fictícios
    st.header("8. Exibir Dados Fictícios")
    exibir_dados = st.checkbox('Exibir dados exemplo')
    if exibir_dados:
        dados = {'Nome': ['A', 'B', 'C'], 'Idade': [25, 30, 35]}
        df = pd.DataFrame(dados)
        st.write(df)


    def plot_grafico(x):
        y = np.sin(x)  # Função seno
        fig, ax = plt.subplots()  # Criando a figura e o eixo
        ax.plot(x, y, label='Seno(x)')
        
        ax.set_xlabel('X')
        ax.set_ylabel('Seno(X)')
        ax.set_title('Gráfico da Função Seno')
        ax.legend()
        
        # Mostrar o gráfico no Streamlit
        st.pyplot(fig)

    plot_grafico([i for i in range(1,idade*5)])


    # 9. Resumo
    st.header("9. Resumo Final")
    st.write(f"Você escolheu: nome: {nome}, idade: {idade}, fruta: {fruta}, sexo: {sexo}, data: {data}")




elif opcao == 'Script 2: Análise Avançada':
    st.subheader("Você escolheu o Script 2 - Análise Avançada")
    
    # Aqui você pode colocar o conteúdo ou lógica do Script 2
    st.write("Este é um exemplo de análise avançada, com mais funcionalidades.\n Sugestão: https://raw.githubusercontent.com/GustavoDasa/Atividades/refs/heads/main/Modelos_de_Regress%C3%A3o/SENIC.csv\n ID e idade")

    # Seção 1: Ingestão de dados
    st.title("Análise de Séries Temporais")

    st.sidebar.header("1. Ingestão de Dados")

    # Opção para inserir URL ou API
    data_source = st.sidebar.radio("Escolha a fonte de dados", ('Upload de CSV', 'URL de Dados (CSV ou API)'))

    if data_source == 'Upload de CSV':
        uploaded_file = st.sidebar.file_uploader("Carregar arquivo CSV", type=["csv"])
        if uploaded_file is not None:
            data = pd.read_csv(uploaded_file)
            st.write("Dados carregados com sucesso!")
            st.write(data.head())
    else:
        url = st.sidebar.text_input("Insira a URL de um CSV ou API de dados")
        if url:
            try:
                data = pd.read_csv(url)
                st.write("Dados carregados da URL com sucesso!")
                st.write(data.head())
            except Exception as e:
                st.error(f"Erro ao carregar dados: {e}")

    # Se os dados forem carregados, prosseguir para a análise
    if 'data' in locals():
        st.sidebar.header("2. Configuração da Análise")
        
        # Seção 2: Escolha das colunas de interesse
        st.subheader("Configurar Série Temporal")
        
        # Selecionar a coluna de datas e a coluna de valores
        coluna_data = st.sidebar.selectbox("Selecione a coluna de data", data.columns)
        coluna_valores = st.sidebar.selectbox("Selecione a coluna de valores", data.columns)
        
        # Converter a coluna de data para datetime
        data[coluna_data] = pd.to_datetime(data[coluna_data], errors='coerce')
        data = data.dropna(subset=[coluna_data])  # Remover linhas com datas inválidas
        
        # Exibir os dados filtrados
        st.write(f"Visualizando os dados de {coluna_data} e {coluna_valores}")
        st.write(data[[coluna_data, coluna_valores]].head())
        
        # Seção 3: Opções de análise
        st.sidebar.header("3. Análise de Séries Temporais")
        
        # Opção de análise: Média Móvel
        window_size = st.sidebar.slider("Selecione o tamanho da janela para a média móvel", 1, 30, 7)
        
        # Gerar a média móvel
        data['Média Móvel'] = data[coluna_valores].rolling(window=window_size).mean()
        
        # Exibir os gráficos
        st.subheader("Gráficos de Séries Temporais")
        
        # Função para plotar o gráfico
        def plot_series(data, coluna_data, coluna_valores):
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(data[coluna_data], data[coluna_valores], label="Dados Originais", color='blue')
            ax.plot(data[coluna_data], data['Média Móvel'], label=f"Média Móvel ({window_size} dias)", color='orange')
            ax.set_xlabel('Data')
            ax.set_ylabel(coluna_valores)
            ax.set_title("Análise de Série Temporal")
            ax.legend()
            st.pyplot(fig)
        
        plot_series(data, coluna_data, coluna_valores)
        
        # Seção 4: Download de resultados
        st.sidebar.header("4. Baixar Resultados")
        
        def converter_para_csv(df):
            return df.to_csv(index=False).encode('utf-8')
        
        csv = converter_para_csv(data)
        
        st.sidebar.download_button(label="Baixar Dados Processados", data=csv, file_name='serie_temporal.csv', mime='text/csv')

