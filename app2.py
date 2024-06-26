import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
        col1, col2, col3, col4, col5 = st.columns(5)
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
        with col5:
            st.write('Tipo de Sazo')
            tipo_sazo = st.selectbox('Selecione uma oção', ['PORCENTAGEM', 'FLAT'])


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
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write('Máx. Var. Consumo (%)')
            max_varaiçãop = round(max_varaição * 100, 2)
            st.markdown(f"<h4 style='text-align; color: white;'> {max_varaiçãop}% </h4>", unsafe_allow_html=True)
        with col2:
            st.write('Méd . Consumo (MWh)')
            st.markdown(f"<h4 style='text-align; color: white;'> {total_MWh} MWh </h4>", unsafe_allow_html=True)
        with col3:
            st.write('Méd . Consumo (MWm)')
            total_MWmr = round(total_MWm,5)
            st.markdown(f"<h4 style='text-align; color: white;'> {total_MWmr} MWm </h4>", unsafe_allow_html=True)

    with st.container():
        st.title('Dados de Consumo')
        #st.dataframe(df, width=1500)         
        st.dataframe(data_transpose, width=1500)

    with st.container():
        st.title('Balanço Energetico') 
        
        balanco1 = pd.DataFrame({'Flex Máx. [MWh]':df.iloc[12]*(1+flex_max),'Sazo Sugerida [MWh]':df.loc['Contrato Ajustado [MWh]:'], 'Flex Min. [MWh]':df.iloc[12]*(1-flex_min), 
        'Sazo Sugerida [MWm]:':df.iloc[11], 'Necessidade [MWh]:':df.iloc[5]*(1+0.03)})

        balanco = balanco1.T

    def take1():
        result = pd.Series(index=balanco.index)  # Criar uma série para armazenar os resultados

        for coluna in balanco.columns:
            necessidade = balanco.loc['Necessidade [MWh]:', coluna]
            flex_max = balanco.loc['Flex Máx. [MWh]', coluna]
            flex_min = balanco.loc['Flex Min. [MWh]', coluna]

            if (necessidade >= flex_max).all():
                result[coluna] = flex_max
            elif (necessidade <= flex_min).all():
                result[coluna] = flex_min
            elif (necessidade > flex_min).all() and (necessidade < flex_max).all():
                result[coluna] = necessidade
            else:
                result[coluna] = None
        
        return result

    take = take1()

    balanco.loc['Take [MWh]',:] = take
    balanco.loc['Exposição [MWh]',:] = balanco.loc['Take [MWh]',:] - balanco.loc['Necessidade [MWh]:']
    balanco.loc['Variação Exposição / Take',:] = balanco.loc['Exposição [MWh]',:] / balanco.loc['Take [MWh]']
    
    max_exposicao = balanco.loc['Variação Exposição / Take'].max()

    balanco_t = balanco.transpose()

    st.dataframe(balanco, width=1500)

    with st.container():
        fig = go.Figure(layout=dict(width=1500, height=500))

        #grafico de barras
        fig.add_trace(go.Bar(x=data1['Meses'], y=balanco1['Necessidade [MWh]:'], name='Necessidade [MWh]', marker_color='orange'))

        #grafico de barras
        fig.add_trace(go.Bar(x=data1['Meses'], y=balanco_t['Take [MWh]'], name='Take [MWh]', marker_color='blue'))

        #grafico de linhas flex max
        fig.add_trace(go.Scatter(x=data1['Meses'], y=balanco1['Flex Máx. [MWh]'], mode='lines+markers', name='Flex Máx. [MWh]', line=dict(color='red', width=2)))

        #grafico de linhas flex min
        fig.add_trace(go.Scatter(x=data1['Meses'], y=balanco1['Flex Min. [MWh]'], mode='lines+markers', name='Flex Min. [MWh]', line=dict(color='red', width=2)))

        #grafico de linhas sazo 
        fig.add_trace(go.Scatter(x=data1['Meses'], y=balanco1['Sazo Sugerida [MWh]'], mode='lines+markers', name='Sazo Sugerida [MWh]', line=dict(color='green', width=2)))

        # Atualizando layout do gráfico
        fig.update_layout(title='Contrato Ajustado de Eneriga por Mês', xaxis_title='Meses', yaxis_title='Contrato Ajustado [MWh]')
        
        # Exibindo o gráfico no Streamlit
        st.plotly_chart(fig)

        with col4:
            st.write('Máx. Variação Take (%)')
            max_exposicaop = round(max_exposicao, 5)
            st.markdown(f"<h4 style='text-align; color: white;'> {max_exposicaop}% </h4>", unsafe_allow_html=True)   


def renderizar_pagina():
    imagem_url = 'https://www.americaenergia.com.br/assets/public/america-logo.png'
    pagina = st.sidebar.image(imagem_url)

    opcao_selecionada = st.sidebar.selectbox('Selecione a opção desejada:', ['Definir Produto Ótimo'])
    # Renderizando a página selecionada
    if opcao_selecionada == 'Definir Produto Ótimo':
        produto_definir()

renderizar_pagina()
