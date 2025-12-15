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

# Filtro 1: Região
lista_regioes = list(regioes_dict.keys())
regiao_selecionada = st.sidebar.selectbox("Selecione a Região:", lista_regioes)

# Filtrar dados da Região
dados_regiao = teste3_copy[teste3_copy['region_name'] == regiao_selecionada]

# Filtro 2: Estado (Com opção "Nenhum")
estados_da_regiao = sorted([est for est in regioes_dict[regiao_selecionada] if est in teste3_copy['customer_state'].unique()])
opcoes_estado = ["Nenhum"] + estados_da_regiao
estado_selecionado = st.sidebar.selectbox("Selecione o Estado:", opcoes_estado)

# --- LÓGICA DE EXIBIÇÃO ---

# SE FOR ESTADO "NENHUM" -> MOSTRAR VISÃO REGIONAL
if estado_selecionado == "Nenhum":
    st.title(f"Panorama Regional: {regiao_selecionada}")
    
    # KPIs da Região
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Frete Médio (Região)", f"R$ {dados_regiao['freight_value'].mean():.2f}")
    kpi2.metric("Pagamento Principal", f"{dados_regiao['payment_type_portugues'].mode()[0]}")
    kpi3.metric("Preço Médio", f"R$ {dados_regiao['price'].mean():.2f}")
    kpi4.metric("Total de Pedidos", f"{len(dados_regiao)}")
    
    st.divider()
    
    # GRÁFICOS REGIONAIS (Comparativos)
    st.subheader(f"Comparativo entre Estados do {regiao_selecionada}")

    # 1. Tipos de Pagamento por Estado
    st.markdown("**1. Distribuição de Pagamentos por Estado**")
    pagamento_dist = dados_regiao.groupby(['customer_state_full', 'payment_type_portugues']).size().reset_index(name='count')
    
    fig1, ax1 = plt.subplots(figsize=(12, 6))
    sns.barplot(x='count', y='customer_state_full', hue='payment_type_portugues', data=pagamento_dist, orient='h', palette='viridis', ax=ax1)
    ax1.set_xlabel('Quantidade')
    ax1.set_ylabel('Estado')
    st.pyplot(fig1)

    col1, col2 = st.columns(2)
    with col1:
        # 2. Preços por Estado
        st.markdown("**2. Distribuição de Preços**")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        sns.violinplot(x='customer_state_full', y='price', data=dados_regiao, palette='coolwarm', ax=ax2)
        ax2.set_xlabel('Estado')
        ax2.set_ylabel('Preço')
        st.pyplot(fig2)
        
    with col2:
        # 3. Frete por Estado
        st.markdown("**3. Distribuição de Frete**")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        sns.boxplot(x='customer_state_full', y='freight_value', data=dados_regiao, palette='crest', ax=ax3)
        ax3.set_xlabel('Estado')
        ax3.set_ylabel('Frete')
        st.pyplot(fig3)

# SE FOR UM ESTADO ESPECÍFICO -> MOSTRAR VISÃO DO ESTADO
else:
    dados_estado = dados_regiao[dados_regiao['customer_state'] == estado_selecionado]
    nome_completo_estado = regiosemsigla.get(estado_selecionado, estado_selecionado)
    
    st.title(f"Análise Detalhada: {nome_completo_estado} ({estado_selecionado})")
    
    if not dados_estado.empty:
        # KPIs do Estado
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Frete Médio", f"R$ {dados_estado['freight_value'].mean():.2f}")
        kpi2.metric("Pagamento Principal", f"{dados_estado['payment_type_portugues'].mode()[0]}")
        kpi3.metric("Preço Médio", f"R$ {dados_estado['price'].mean():.2f}")
        kpi4.metric("Média Parcelas", f"{dados_estado['payment_installments'].mean():.1f}x")
        
        st.divider()

        # GRÁFICOS DO ESTADO
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("1. Formas de Pagamento")
            pag_contagem = dados_estado['payment_type_portugues'].value_counts().reset_index()
            pag_contagem.columns = ['Tipo', 'Qtd']
            
            fig_st1, ax_st1 = plt.subplots(figsize=(8, 5))
            sns.barplot(x='Qtd', y='Tipo', data=pag_contagem, palette='viridis', ax=ax_st1)
            ax_st1.set_title(f'Pagamentos em {estado_selecionado}')
            st.pyplot(fig_st1)
            
        with col_graf2:
            st.subheader("2. Histograma de Parcelas")
            max_parc = int(dados_estado['payment_installments'].max())
            fig_st2, ax_st2 = plt.subplots(figsize=(8, 5))
            sns.histplot(dados_estado['payment_installments'], bins=range(1, max_parc+2), color='seagreen', ax=ax_st2)
            ax_st2.set_title(f'Parcelamento em {estado_selecionado}')
            ax_st2.set_xticks(range(1, max_parc+1))
            st.pyplot(fig_st2)
            
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
             st.subheader("3. Preços (Violin Plot)")
             fig_st3, ax_st3 = plt.subplots(figsize=(8, 5))
             sns.violinplot(y='price', data=dados_estado, palette='coolwarm', ax=ax_st3)
             st.pyplot(fig_st3)
             
        with col_graf4:
             st.subheader("4. Frete (Box Plot)")
             fig_st4, ax_st4 = plt.subplots(figsize=(8, 5))
             sns.boxplot(y='freight_value', data=dados_estado, palette='crest', ax=ax_st4)
             st.pyplot(fig_st4)

    else:
        st.warning("Sem dados para este estado.")

#--- 8. ANÁLISE AVANÇADA E DADOS (NOVO BLOCO) ---
st.divider()
st.header("Análise Avançada e Dados")

col_adv1, col_adv2 = st.columns(2)

with col_adv1:
    st.subheader("5. Relação Preço x Frete")
    st.markdown("Identifique se produtos caros pagam mais frete.")
    
    # Gráfico de Dispersão (Scatter Plot)
    fig_scat, ax_scat = plt.subplots(figsize=(10, 6))
    
    # Usamos scatterplot. O 'hue' colore pelo tipo de pagamento para dar mais contexto
    sns.scatterplot(
        data=dados_estado if 'dados_estado' in locals() and not dados_estado.empty else dados_regiao,
        x='price', 
        y='freight_value', 
        hue='payment_type_portugues',
        alpha=0.6, # Transparência para ver sobreposição
        palette='viridis',
        ax=ax_scat
    )
    
    ax_scat.set_title("Dispersão: Preço do Produto vs Valor do Frete")
    ax_scat.set_xlabel("Preço do Produto (R$)")
    ax_scat.set_ylabel("Valor do Frete (R$)")
    
    # Escala logarítmica ajuda se houver preços muito díspares (opcional, pode remover se quiser)
    ax_scat.set_xscale('log')
    ax_scat.set_yscale('log')
    
    st.pyplot(fig_scat)
    st.caption("Nota: Eixos em escala logarítmica para melhor visualização.")

with col_adv2:
    st.subheader("6. Faixas de Preço")
    st.markdown("Como as vendas se dividem por valor?")
    
    # Define os dados a serem usados (Estado ou Região)
    df_analise = dados_estado if 'dados_estado' in locals() and not dados_estado.empty else dados_regiao
    
    # Criar faixas de preço (Buckets)
    bins = [0, 50, 100, 250, 500, float('inf')]
    labels = ['Até R$50', 'R$50-100', 'R$100-250', 'R$250-500', 'Acima de R$500']
    
    # .copy() para evitar avisos do pandas
    df_analise = df_analise.copy()
    df_analise['faixa_preco'] = pd.cut(df_analise['price'], bins=bins, labels=labels)
    
    # Contagem
    faixa_counts = df_analise['faixa_preco'].value_counts().sort_index()
    
    fig_bar, ax_bar = plt.subplots(figsize=(10, 6))
    sns.barplot(x=faixa_counts.index, y=faixa_counts.values, palette='magma', ax=ax_bar)
    
    ax_bar.set_title("Quantidade de Vendas por Faixa de Preço")
    ax_bar.set_ylabel("Quantidade de Pedidos")
    ax_bar.set_xlabel("Faixa de Preço")
    
    # Adicionar rótulos nas barras
    for i, v in enumerate(faixa_counts.values):
        ax_bar.text(i, v + (v*0.01), str(v), ha='center', fontweight='bold')
        
    st.pyplot(fig_bar)

# --- 9. EXIBIÇÃO DE DADOS BRUTOS ---
st.divider()
st.subheader("Base de Dados Filtrada")

# Escolhe qual DF mostrar
df_final = dados_estado if 'dados_estado' in locals() and not dados_estado.empty else dados_regiao

# Mostra as primeiras linhas interativas
st.dataframe(df_final.head(100), use_container_width=True)

# Botão de Download CSV
csv = df_final.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Baixar Dados Filtrados (CSV)",
    data=csv,
    file_name=f"dados_vendas_{estado_selecionado if estado_selecionado != 'Nenhum' else regiao_selecionada}.csv",
    mime="text/csv",
)
