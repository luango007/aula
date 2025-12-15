import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Dashboard Estadual", layout="wide")

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
teste3_copy['region_name'] = teste3_copy['customer_state'].map(estado_para_regiao)
teste3_copy['customer_state_full'] = teste3_copy['customer_state'].map(regiosemsigla)
teste3_copy['payment_type_portugues'] = teste3_copy['payment_type'].map(traducao_pagamento)

# --- 5. BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros")

# Filtro 1: Região (apenas para facilitar encontrar o estado)
lista_regioes = list(regioes_dict.keys())
regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", lista_regioes)

# Filtrar lista de estados baseada na região
estados_da_regiao = [est for est in regioes_dict[regiao_selecionada] if est in teste3_copy['customer_state'].unique()]
estados_da_regiao = sorted(estados_da_regiao)

# Filtro 2: Estado
estado_selecionado = st.sidebar.selectbox("Selecione o Estado:", estados_da_regiao)

# FILTRO PRINCIPAL: Cria o DataFrame apenas com o estado escolhido
dados_estado = teste3_copy[teste3_copy['customer_state'] == estado_selecionado]
nome_completo_estado = regiosemsigla.get(estado_selecionado, estado_selecionado)

# --- 6. INDICADORES DO ESTADO (KPIs) ---
st.title(f"Análise: {nome_completo_estado} ({estado_selecionado})")

if not dados_estado.empty:
    # Cálculo das Métricas
    frete_medio = dados_estado['freight_value'].mean()
    preco_medio = dados_estado['price'].mean()
    parcelas_media = dados_estado['payment_installments'].mean()
    
    # Moda (forma de pagamento mais comum)
    pagamento_top_series = dados_estado['payment_type_portugues'].mode()
    pagamento_top = pagamento_top_series[0] if not pagamento_top_series.empty else "N/A"

    # Exibição no Topo
    st.markdown("### Indicadores Chave")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("Frete Médio", f"R$ {frete_medio:.2f}")
    kpi2.metric("Pagamento Principal", f"{pagamento_top}")
    kpi3.metric("Preço Médio", f"R$ {preco_medio:.2f}")
    kpi4.metric("Média de Parcelas", f"{parcelas_media:.1f}x")
    
    st.divider()

    # --- 7. GRÁFICOS DO ESTADO ---
    
    # 7.1 Distribuição dos Tipos de Pagamento
    st.subheader("1. Preferência de Pagamento")
    
    # Contagem simples por tipo de pagamento
    pagamento_contagem = dados_estado['payment_type_portugues'].value_counts().reset_index()
    pagamento_contagem.columns = ['Tipo de Pagamento', 'Quantidade']
    
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(
        x='Quantidade', y='Tipo de Pagamento', 
        data=pagamento_contagem, palette='viridis', ax=ax1
    )
    ax1.set_title(f'Métodos de Pagamento em {estado_selecionado}')
    ax1.grid(axis='x', linestyle='--', alpha=0.5)
    st.pyplot(fig1)

    col1, col2 = st.columns(2)

    with col1:
        # 7.2 Distribuição de Preços (Violin Plot)
        st.subheader("2. Distribuição de Preços")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        
        # Plot apenas com o eixo Y (preço)
        sns.violinplot(
            y='price', data=dados_estado, 
            palette='coolwarm', ax=ax2
        )
        ax2.set_title(f'Variação dos Preços ({estado_selecionado})')
        ax2.set_ylabel('Preço (R$)')
        st.pyplot(fig2)

    with col2:
        # 7.3 Distribuição de Fretes (Box Plot)
        st.subheader("3. Distribuição de Fretes")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        
        # Plot apenas com o eixo Y (frete)
        sns.boxplot(
            y='freight_value', data=dados_estado, 
            palette='crest', ax=ax3
        )
        ax3.set_title(f'Variação do Frete ({estado_selecionado})')
        ax3.set_ylabel('Valor do Frete (R$)')
        st.pyplot(fig3)

    # 7.4 Histograma de Parcelas
    st.subheader("4. Comportamento de Parcelamento")
    fig4, ax4 = plt.subplots(figsize=(12, 6))
    max_parcelas = int(dados_estado['payment_installments'].max())
    
    sns.histplot(
        data=dados_estado, x='payment_installments', 
        bins=range(1, max_parcelas + 2), color='seagreen', ax=ax4
    )
    ax4.set_title(f'Frequência de Parcelas em {nome_completo_estado}')
    ax4.set_xlabel('Número de Parcelas')
    ax4.set_ylabel('Quantidade de Pedidos')
    ax4.set_xticks(range(1, max_parcelas + 1))
    ax4.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig4)

else:
    st.warning(f"Sem dados disponíveis para {nome_completo_estado}.")
