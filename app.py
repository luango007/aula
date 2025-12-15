import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. CONFIGURAÇÃO E DADOS ---
st.set_page_config(page_title="Dashboard de Vendas", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv('teste3_filtered.csv')

try:
    teste3_copy = load_data()
except FileNotFoundError:
    st.error("Arquivo 'teste3_filtered.csv' não encontrado.")
    st.stop()

# --- 2. MAPEAMENTOS ---
# Mapeamento Estado -> Região
mapa_regioes = {
    'AC': 'Norte', 'AL': 'Nordeste', 'AP': 'Norte', 'AM': 'Norte', 'BA': 'Nordeste',
    'CE': 'Nordeste', 'DF': 'Centro-Oeste', 'ES': 'Sudeste', 'GO': 'Centro-Oeste',
    'MA': 'Nordeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MG': 'Sudeste',
    'PA': 'Norte', 'PB': 'Nordeste', 'PR': 'Sul', 'PE': 'Nordeste', 'PI': 'Nordeste',
    'RJ': 'Sudeste', 'RN': 'Nordeste', 'RS': 'Sul', 'RO': 'Norte', 'RR': 'Norte',
    'SC': 'Sul', 'SP': 'Sudeste', 'SE': 'Nordeste', 'TO': 'Norte'
}

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

# Tradução de tipos de pagamento
traducao_pagamento = {
    'credit_card': 'Cartão de Crédito', 'boleto': 'Boleto', 'voucher': 'Voucher',
    'debit_card': 'Cartão de Débito', 'not_defined': 'Não Definido'
}

# --- 3. PRÉ-PROCESSAMENTO ---
# Criar colunas auxiliares no DataFrame principal
teste3_copy['customer_state_full'] = teste3_copy['customer_state'].map(regiosemsigla)
teste3_copy['payment_type_portugues'] = teste3_copy['payment_type'].map(traducao_pagamento)
teste3_copy['region_name'] = teste3_copy['customer_state'].map(mapa_regioes)

# --- 4. INTERFACE ---
st.title("Análise de Pagamentos e Fretes")

# Seletor de Estado
estados_disponiveis = sorted(teste3_copy['customer_state'].unique())
estado_selecionado = st.selectbox("Selecione o Estado:", estados_disponiveis)

# Filtros automáticos
nome_da_regiao = mapa_regioes.get(estado_selecionado, 'Indefinida')
nome_completo_estado = regiosemsigla.get(estado_selecionado, estado_selecionado)

# Cria DataFrames filtrados
# 1. DataFrame da Região (para comparação)
regiao = teste3_copy[teste3_copy['region_name'] == nome_da_regiao].copy()
# 2. DataFrame do Estado (para foco)
estado_filtrado = teste3_copy[teste3_copy['customer_state'] == estado_selecionado].copy()

st.info(f"Visualizando dados de **{nome_completo_estado}** no contexto da região **{nome_da_regiao}**.")

# --- 5. GRÁFICOS ---

# Gráfico 1: Barras de Tipos de Pagamento (Comparativo Regional)
st.subheader(f"1. Distribuição de Tipos de Pagamento ({nome_da_regiao})")
pag_distribuicao = regiao.groupby(['customer_state_full', 'payment_type_portugues']).size().reset_index(name='count')

fig1, ax1 = plt.subplots(figsize=(12, 8))
sns.barplot(x='count', y='customer_state_full', hue='payment_type_portugues', data=pag_distribuicao, orient='h', palette='viridis', ax=ax1)
ax1.set_title(f'Distribuição de Tipos de Pagamento - Região {nome_da_regiao}')
ax1.set_xlabel('Número de Pagamentos')
ax1.set_ylabel('Estado')
ax1.legend(title='Tipo de Pagamento')
st.pyplot(fig1)

# Gráfico 2: Violin Plot de Preço (Comparativo Regional)
st.subheader(f"2. Distribuição do Valor de Pagamento ({nome_da_regiao})")
fig2, ax2 = plt.subplots(figsize=(12, 8))
sns.violinplot(x='customer_state_full', y='price', data=regiao, orient='v', palette='coolwarm', ax=ax2)
ax2.set_title(f'Distribuição do Valor de Pagamento por Estado ({nome_da_regiao})')
ax2.set_xlabel('Estado')
ax2.set_ylabel('Valor (R$)')
st.pyplot(fig2)

# Gráfico 3: Histograma de Frete (Foco Regional)
st.subheader(f"3. Distribuição Geral do Frete ({nome_da_regiao})")
fig3, ax3 = plt.subplots(figsize=(12, 6))
sns.histplot(regiao['freight_value'], bins=50, kde=True, color='salmon', ax=ax3)
ax3.set_title(f'Distribuição do Valor do Frete na Região {nome_da_regiao}')
ax3.set_xlabel('Valor do Frete')
ax3.set_ylabel('Frequência')
ax3.grid(True, linestyle='--', alpha=0.7)
st.pyplot(fig3)

# Gráfico 4: Boxplot de Frete (Comparativo Regional)
st.subheader(f"4. Comparativo de Frete por Estado ({nome_da_regiao})")
fig4, ax4 = plt.subplots(figsize=(12, 8))
sns.boxplot(x='customer_state_full', y='freight_value', data=regiao, orient='v', palette='crest', ax=ax4)
ax4.set_title(f'Distribuição do Valor do Frete por Estado ({nome_da_regiao})')
ax4.set_xlabel('Estado')
ax4.set_ylabel('Valor do Frete')
st.pyplot(fig4)

# Gráfico 5: Parcelas (Região vs Estado)
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"**Parcelas na Região {nome_da_regiao}**")
    fig5, ax5 = plt.subplots(figsize=(10, 6))
    max_parcelas_regiao = int(regiao['payment_installments'].max())
    sns.histplot(data=regiao, x='payment_installments', multiple='stack', bins=range(1, max_parcelas_regiao + 2), ax=ax5)
    ax5.set_title(f'Parcelas - Região {nome_da_regiao}')
    ax5.set_xticks(range(1, max_parcelas_regiao + 1))
    st.pyplot(fig5)

with col2:
    st.markdown(f"**Parcelas em {nome_completo_estado}**")
    if not estado_filtrado.empty:
        fig6, ax6 = plt.subplots(figsize=(10, 6))
        max_parcelas_estado = int(estado_filtrado['payment_installments'].max())
        sns.histplot(data=estado_filtrado, x='payment_installments', bins=range(1, max_parcelas_estado + 2), color='seagreen', ax=ax6)
        ax6.set_title(f'Parcelas - {nome_completo_estado}')
        ax6.set_xticks(range(1, max_parcelas_estado + 1))
        st.pyplot(fig6)
    else:
        st.warning("Sem dados para este estado.")

# Gráfico 7: Valor Médio do Frete
st.subheader(f"5. Valor Médio do Frete ({nome_da_regiao})")
avg_freight = regiao.groupby('customer_state_full')['freight_value'].mean().reset_index().sort_values(by='freight_value', ascending=False)
fig7, ax7 = plt.subplots(figsize=(14, 8))
sns.barplot(x='freight_value', y='customer_state_full', data=avg_freight, palette='Greens', hue='customer_state_full', legend=False, ax=ax7)
ax7.set_title(f'Valor Médio do Frete por Estado ({nome_da_regiao})')
ax7.set_xlabel('Média de Frete (R$)')
st.pyplot(fig7)
