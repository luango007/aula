import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Configuração e Carregamento de Dados
st.set_page_config(page_title="Análise de Vendas", layout="wide")

@st.cache_data
def load_data():
    # Carrega o arquivo enviado
    df = pd.read_csv('teste3_filtered.csv')
    return df

try:
    teste3_copy = load_data()
except FileNotFoundError:
    st.error("Arquivo 'teste3_filtered.csv' não encontrado. Certifique-se de que ele está na mesma pasta.")
    st.stop()

# 2. Definição dos Dicionários (Regiões e Nomes Completos)
# Mapeamento de Estados para Regiões
regioes_map = {
    'Norte': ['AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC'],
    'Nordeste': ['MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA'],
    'Centro-Oeste': ['MT', 'MS', 'GO', 'DF'],
    'Sudeste': ['SP', 'RJ', 'MG', 'ES'],
    'Sul': ['PR', 'RS', 'SC']
}

# Mapeamento de Sigla para Nome Completo (regiãosemsigla)
regiosemsigla = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia',
    'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás',
    'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
    'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
    'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo',
    'SE': 'Sergipe', 'TO': 'Tocantins'
}

# 3. Pré-processamento dos Dados
# Cria uma função inversa para mapear cada linha do DF à sua região
estado_para_regiao = {estado: regiao for regiao, estados in regioes_map.items() for estado in estados}

# Cria as colunas necessárias no DataFrame
teste3_copy['region'] = teste3_copy['customer_state'].map(estado_para_regiao)
teste3_copy['customer_state_full'] = teste3_copy['customer_state'].map(regiosemsigla)

# 4. Interface do Streamlit (Filtros)
st.title("Análise de Distribuição de Preços")

col1, col2 = st.columns(2)

with col1:
    # Filtro de Região
    lista_regioes = list(regioes_map.keys())
    regiao_selecionada = st.selectbox("Selecione a Região:", lista_regioes)

with col2:
    # Filtro de Estado (Dinâmico com base na região selecionada)
    estados_disponiveis = regioes_map[regiao_selecionada]
    # Filtra apenas estados que realmente existem no dataset para evitar erros
    estados_presentes = teste3_copy[teste3_copy['customer_state'].isin(estados_disponiveis)]['customer_state'].unique()
    estado_selecionado = st.selectbox("Selecione o Estado (Opcional):", sorted(estados_presentes))

# 5. Lógica de Filtragem
# Filtra o DataFrame para a Região selecionada (para o gráfico geral)
regiao_para_boxplot = teste3_copy[teste3_copy['region'] == regiao_selecionada]

# Filtra dados específicos do estado (caso queira exibir dados pontuais)
dados_estado = teste3_copy[teste3_copy['customer_state'] == estado_selecionado]
nome_completo_estado = regiosemsigla.get(estado_selecionado, estado_selecionado)

# 6. Visualização
if not regiao_para_boxplot.empty:
    st.subheader(f"Distribuição do Valor de Pagamento - Região {regiao_selecionada}")
    
    # Criar o gráfico
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Nota: Palette 'coolwarm' funciona melhor com dados numéricos ou sequenciais, 
    # mas mantive conforme seu código original.
    sns.violinplot(
        x='customer_state_full', 
        y='price', 
        data=regiao_para_boxplot, 
        orient='v', 
        palette='coolwarm',
        ax=ax
    )
    
    ax.set_title(f'Distribuição do Valor de Pagamento por Estado ({regiao_selecionada})')
    ax.set_xlabel('Estado do Cliente')
    ax.set_ylabel('Valor de Pagamento')
    
    st.pyplot(fig)

    # Exibe métricas rápidas do Estado Selecionado abaixo do gráfico
    st.divider()
    st.metric(label=f"Média de Preço em {nome_completo_estado}", value=f"R$ {dados_estado['price'].mean():.2f}")

else:
    st.warning("Não há dados disponíveis para a região selecionada.")
