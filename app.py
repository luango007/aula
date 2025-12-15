import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

# --- 2. CARREGAMENTO DOS DADOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('teste3_filtered.csv')
        return df
    except FileNotFoundError:
        return None

teste3_copy = load_data()

if teste3_copy is None:
    st.error("Arquivo 'teste3_filtered.csv' não encontrado.")
    st.stop()

# --- 3. DEFINIÇÕES E MAPEAMENTOS ---
# Definição das Regiões
regioes_dict = {
    'Nordeste': ['MA', 'PI', 'CE', 'RN', 'PB', 'PE', 'AL', 'SE', 'BA'],
    'Sudeste': ['SP', 'RJ', 'MG', 'ES'],
    'Sul': ['PR', 'RS', 'SC'],
    'Norte': ['AM', 'RR', 'AP', 'PA', 'TO', 'RO', 'AC'],
    'Centro-Oeste': ['MT', 'MS', 'GO', 'DF']
}

# Inverter dicionário para mapear Estado -> Região
estado_para_regiao = {est: reg for reg, estados in regioes_dict.items() for est in estados}

# Nomes completos dos estados
regiosemsigla = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia',
    'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás',
    'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
    'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
    'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo',
    'SE': 'Sergipe', 'TO': 'Tocantins'
}

# Tradução de pagamentos
traducao_pagamento = {
    'credit_card': 'Cartão de Crédito', 'boleto': 'Boleto', 'voucher': 'Voucher',
    'debit_card': 'Cartão de Débito', 'not_defined': 'Não Definido'
}

# --- 4. PREPARAÇÃO DO DATAFRAME ---
# Cria as colunas necessárias
teste3_copy['region_name'] = teste3_copy['customer_state'].map(estado_para_regiao)
teste3_copy['customer_state_full'] = teste3_copy['customer_state'].map(regiosemsigla)
teste3_copy['payment_type_portugues'] = teste3_copy['payment_type'].map(traducao_pagamento)

# --- 5. BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros")

# Filtro 1: Região
lista_regioes = list(regioes_dict.keys())
regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", lista_regioes)

# Filtrar dados da Região
dados_regiao = teste3_copy[teste3_copy['region_name'] == regiao_selecionada]

# Filtro 2: Estado (Baseado na região selecionada)
estados_disponiveis = sorted(dados_regiao['customer_state'].unique())
estado_selecionado = st.sidebar.selectbox("Selecione o Estado:", estados_disponiveis)

# Filtrar dados do Estado
dados_estado = dados_regiao[dados_regiao['customer_state'] == estado_selecionado]
nome_completo_estado = regiosemsigla.get(estado_selecionado, estado_selecionado)

# --- 6. VISUALIZAÇÕES ---

st.title(f"Análise Regional: {regiao_selecionada}")

# 6.1 Gráfico de Barras - Tipos de Pagamento
st.subheader("1. Tipos de Pagamento por Estado")
pagamento_distribuicao = dados_regiao.groupby(['customer_state_full', 'payment_type_portugues']).size().reset_index(name='count')

fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(
    x='count', y='customer_state_full', hue='payment_type_portugues', 
    data=pagamento_distribuicao, orient='h', palette='viridis', ax=ax1
)
ax1.set_title(f'Distribuição de Tipos de Pagamento ({regiao_selecionada})')
ax1.set_xlabel('Quantidade de Pagamentos')
ax1.set_ylabel('Estado')
ax1.legend(title='Tipo de Pagamento')
st.pyplot(fig1)

col1, col2 = st.columns(2)

with col1:
    # 6.2 Violin Plot - Preço
    st.subheader("2. Distribuição de Preços (Violin Plot)")
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.violinplot(
        x='customer_state_full', y='price', data=dados_regiao, 
        orient='v', palette='coolwarm', ax=ax2
    )
    ax2.set_title(f'Distribuição do Valor de Pagamento ({regiao_selecionada})')
    ax2.set_xlabel('Estado')
    ax2.set_ylabel('Preço')
    st.pyplot(fig2)

with col2:
    # 6.3 Box Plot - Frete
    st.subheader("3. Distribuição de Fretes (Box Plot)")
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        x='customer_state_full', y='freight_value', data=dados_regiao, 
        orient='v', palette='crest', ax=ax3
    )
    ax3.set_title(f'Distribuição do Valor do Frete ({regiao_selecionada})')
    ax3.set_xlabel('Estado')
    ax3.set_ylabel('Valor do Frete')
    st.pyplot(fig3)

# 6.4 Histograma - Frete da Região
st.subheader("4. Histograma de Fretes da Região")
fig4, ax4 = plt.subplots(figsize=(12, 5))
sns.histplot(dados_regiao['freight_value'], bins=50, kde=True, color='salmon', ax=ax4)
ax4.set_title(f'Distribuição do Valor do Frete na Região {regiao_selecionada}')
ax4.set_xlabel('Valor do Frete')
ax4.set_ylabel('Frequência')
ax4.grid(True, linestyle='--', alpha=0.7)
st.pyplot(fig4)

# 6.5 Histograma - Parcelas (Região)
st.subheader("5. Histograma de Parcelas (Comparativo Regional)")
fig5, ax5 = plt.subplots(figsize=(12, 6))
max_parcelas_reg = int(dados_regiao['payment_installments'].max())
sns.histplot(
    data=dados_regiao, x='payment_installments', multiple='stack', 
    hue='customer_state', # Adicionei hue para diferenciar os estados
    bins=range(1, max_parcelas_reg + 2), palette='viridis', ax=ax5
)
ax5.set_title(f'Frequência de Parcelas ({regiao_selecionada})')
ax5.set_xlabel('Número de Parcelas')
ax5.set_xticks(range(1, max_parcelas_reg + 1))
st.pyplot(fig5)

# --- 7. ANÁLISE ESPECÍFICA DO ESTADO ---
st.divider()
st.header(f"Foco no Estado: {nome_completo_estado} ({estado_selecionado})")

# 6.6 Histograma - Parcelas (Apenas Estado Selecionado)
st.subheader(f"Parcelamento em {nome_completo_estado}")

if not dados_estado.empty:
    fig6, ax6 = plt.subplots(figsize=(12, 6))
    max_parcelas_est = int(dados_estado['payment_installments'].max())
    
    sns.histplot(
        data=dados_estado, x='payment_installments', multiple='stack',
        bins=range(1, max_parcelas_est + 2), color='seagreen', ax=ax6
    )
    ax6.set_title(f'Frequência do Número de Parcelas - {nome_completo_estado}')
    ax6.set_xlabel('Número de Parcelas')
    ax6.set_ylabel('Frequência')
    ax6.set_xticks(range(1, max_parcelas_est + 1))
    st.pyplot(fig6)
else:
    st.warning(f"Sem dados disponíveis para {nome_completo_estado}.")
