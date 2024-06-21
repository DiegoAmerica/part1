import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

def produto_definir():
    with st.container(): 
        st.title('Definição do Produto Ótimo')
        arquivo_excel = st.file_uploader('Faça o upload de um arquivo Excel com os dados de consumo', type=['xlsx'])

    with st.container():
     
        if arquivo_excel is not None:
            dados = pd.read_excel(arquivo_excel)
    
    with st.container():
        st.title('Caracteristicas do Produto Sugerido')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write('Previsão de Incremento (%)')
            incremento = st.number_input('', min_value=0, value=5, max_value=100, step=1) 
            incremento = np.multiply(incremento, 0.01)       
        with col2:
            st.write('Flexbilidade Mínima (%)')
            flex_min = st.number_input('', min_value=0, max_value=100, step=2)     
            flex_min = np.multiply(flex_min, 0.01) 
        with col3:
            st.write('Flexbilidade Máxima (%)')
            flex_max = st.number_input('', min_value=0, max_value=100, step=3)
            flex_max = np.multiply(flex_max,0.01) 
        with col4:
            st.write('Sazo (%)')
            sazo_input = st.number_input('', min_value=0, max_value=100, step=4)
            sazo_input = np.multiply(sazo_input, 0.01)

    with st.container():        
            df = pd.DataFrame(dados)
            linhas_media = pd.DataFrame(df.loc[[0,1,2,3]])
            linhas_horas = pd.DataFrame(df.loc[[4]])
            media = df.loc['Média [MWh]',:] = linhas_media.max(axis=0) * (1+incremento)
            media = media.astype(float)
            linhas_horas = linhas_horas.astype(float)
            linhas_horas1 = df.iloc[4].to_numpy()

            #inclusão do montante em MWm mês a M~es
            resultado_divisao = media.div(linhas_horas)
            volume_MWm = df.loc['Volume [MWm]',:] = resultado_divisao.values
            volume_MWm = volume_MWm.astype(float)

            #Inclusão do desvio de consumo mês a Mês
            total_MWh = round(np.sum(media),3)
            total_horas1 = np.sum(linhas_horas1)
            total_MWm = np.divide(total_MWh, total_horas1)
            resultado_divisao1 = np.divide(volume_MWm, total_MWm)-1
            desvio = df.loc['Desvio Consumo (% Variação)',:] = resultado_divisao1
            desvio = desvio.astype(float)

            #input pencetual de sazo
            #sazo = np.multiply(25,0.01)
            sazo = sazo_input

            #inclusão da maxima variação (%)
            max_varaição = df.loc['Máxima Variação (%)',:] = df.loc['Desvio Consumo (% Variação)'].max()

            #Relação com a sazo
            ralacao_sazo = df.loc['Relação Sazo (%)',:] = np.divide(max_varaição, sazo)
            ralacao_sazo = ralacao_sazo.astype(float)

            #Consumo normalizado
            normal = df.loc['Desvio Consumo Normalizado (% Variação)',:] = np.divide(desvio, ralacao_sazo)
            normal = normal.astype(float)

            #Contrato ajustado MWm
            contrato_ajustado_MWm = df.loc['Contrato Ajustado [MWm]:', :] = total_MWm * (1+normal)
            contrato_ajustado_MWm = pd.DataFrame(contrato_ajustado_MWm)
            contrato_ajustado_MWm =  contrato_ajustado_MWm.astype(float)
            contrato_ajustado_MWm1  =  df.iloc[11].to_numpy()

            #Contrato ajustado MWh
            contrato_ajustado_MWh = df.loc['Contrato Ajustado [MWh]:', :] = np.multiply(contrato_ajustado_MWm1, linhas_horas1)
            contrato_ajustado_MWh = pd.DataFrame(contrato_ajustado_MWh)
            contrato_ajustado_MWh =  contrato_ajustado_MWm.astype(float)



            #df = pd.DataFrame(df)
            data1 = ({'Meses':['Janeiro','Fevereiro','Março','Abril','Maio','Junho','Julho','Agosto','Setembro','Outubro','Novembro','Dezembro'], 'Contrato Ajustado [MWh]:':df.iloc[12]})
            data = pd.DataFrame({'Máxima [MWh]':df.iloc[5], 'Horas [h]:':df.iloc[4], 'Contrato Ajustado [MWm]:':df.iloc[11],'Contrato Ajustado [MWh]:':df.iloc[12]})
            #data1_transpose = data1.T
            data_transpose = data.T

            
   
    with st.container():
        st.title('Caracteristicas do Consumo')   
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write('Máx. Var. Consumo (%)')
            st.write(max_varaição)           
        with col2:
            st.write('Méd . Consumo (MWh)')
            st.write(total_MWh)
        with col3:
            st.write('Méd . Consumo (MWm)')
            st.write(total_MWm)         

    with st.container():
        st.title('Dados de Consumo')
        #st.dataframe(df, width=1500)         
        st.dataframe(data_transpose, width=1500)

    with st.container():
        st.title('Balanço Energetico') 
        
        def take():
            if df.iloc[5]*(1+0.03)<=df.iloc[12]*(1-flex_min):
                return df.iloc[12]*(1-flex_min)
            
            elif df.iloc[5]*(1+0.03)>=df.iloc[12]*(1+flex_max):
                return df.iloc[12]*(1+flex_max)

            elif df.iloc[5]*(1+0.03)<df.iloc[12]*(1+flex_max) and df.iloc[5]*(1+0.03)>df.iloc[12]*(1-flex_min):
                return df.iloc[5]*(1+0.03)

        balanco1 = pd.DataFrame({'Flex Máx. [MWh]':df.iloc[12]*(1+flex_max),'Sazo Sugerida [MWh]':df.iloc[12], 'Flex Min. [MWh]':df.iloc[12]*(1-flex_min), 
        'Sazo Sugerida [MWm]:':df.iloc[11], 'Necessidade [MWh]:':df.iloc[5]*(1+0.03),'Take [MWh]': take})

        balanco = balanco1.T
        st.dataframe(balanco, width=1500)

def renderizar_pagina():
    imagem_url = 'https://www.americaenergia.com.br/assets/public/america-logo.png'
    pagina = st.sidebar.image(imagem_url)

    opcao_selecionada = st.sidebar.selectbox('Selecione a opção desejada:', ['Definir Produto Ótimo'])
    # Renderizando a página selecionada
    if opcao_selecionada == 'Definir Produto Ótimo':
        produto_definir()

renderizar_pagina()




