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

1. Garante que a variável 'regiao' existe (caso você esteja usando 'região' com til)
if 'região' in locals() and 'regiao' not in locals():
    regiao = região

# 2. Garante que os dicionários de tradução existam
regiosemsigla = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia',
    'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás',
    'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais',
    'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí',
    'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul',
    'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo',
    'SE': 'Sergipe', 'TO': 'Tocantins'
}

traducao_pagamento = {
    'credit_card': 'Cartão de Crédito', 'boleto': 'Boleto', 'voucher': 'Voucher',
    'debit_card': 'Cartão de Débito', 'not_defined': 'Não Definido'
}

# 3. Cria as colunas que faltam dentro do DataFrame 'regiao'
# Usamos .copy() para evitar o erro de "SettingWithCopyWarning"
regiao = regiao.copy() 
if 'customer_state_full' not in regiao.columns:
    regiao['customer_state_full'] = regiao['customer_state'].map(regiosemsigla)

if 'payment_type_portugues' not in regiao.columns:
    regiao['payment_type_portugues'] = regiao['payment_type'].map(traducao_pagamento)
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


#histogram
# 3. Seletor de Estado
st.title("Análise de Frete por Estado")

# Obtém lista única de estados ordenada
lista_estados = sorted(teste3_copy['customer_state'].unique())
estado_selecionado = st.selectbox("Selecione o Estado para visualizar o histograma:", lista_estados)

# 4. Filtragem dos Dados
# Filtra o DataFrame apenas para o estado escolhido
dados_estado = teste3_copy[teste3_copy['customer_state'] == estado_selecionado]

# Identifica a região do estado selecionado (para usar no título)
nome_da_regiao = "Desconhecida"
for regiao, estados in regioes_map.items():
    if estado_selecionado in estados:
        nome_da_regiao = regiao
        break

# 5. Criação do Gráfico
if not dados_estado.empty:
    # Cria a figura e o eixo explicitamente para o Streamlit
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Gera o histograma usando os dados filtrados
    sns.histplot(dados_estado['freight_value'], bins=50, kde=True, color='salmon', ax=ax)
    
    # Título dinâmico
    ax.set_title(f'Distribuição do Valor do Frete - Estado {estado_selecionado} (Região {nome_da_regiao})')
    ax.set_xlabel('Valor do Frete')
    ax.set_ylabel('Frequência')
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Exibe no Streamlit
    st.pyplot(fig)
    
    # (Opcional) Mostra estatísticas básicas abaixo do gráfico
    st.write(f"**Estatísticas de Frete para {estado_selecionado}:**")
    st.write(dados_estado['freight_value'].describe())
else:
    st.warning("Não há dados de frete para o estado selecionado.")

# GRÁFICO 1: Distribuição de Tipos de Pagamento
st.subheader(f"1. Tipos de Pagamento por Estado ({nome_da_regiao})")

# Group by logic
payment_distribution = regiao.groupby(['customer_state_full', 'payment_type_portugues']).size().reset_index(name='count')

fig1, ax1 = plt.subplots(figsize=(12, 8))
sns.barplot(
    x='count', 
    y='customer_state_full', 
    hue='payment_type_portugues', 
    data=payment_distribution, 
    orient='h', 
    palette='viridis',
    ax=ax1
)
ax1.set_title(f'Distribuição de Tipos de Pagamento - Região {nome_da_regiao}')
ax1.set_xlabel('Número de Pagamentos')
ax1.set_ylabel('Estado')
ax1.legend(title='Tipo de Pagamento')
st.pyplot(fig1)

# GRÁFICO 2: Boxplot do Frete
st.subheader(f"2. Distribuição do Valor do Frete ({nome_da_regiao})")

fig2, ax2 = plt.subplots(figsize=(12, 8))
sns.boxplot(
    x='customer_state_full',
    y='freight_value', 
    data=regiao, 
    orient='v',
    palette='crest',
    ax=ax2
)
ax2.set_title(f'Distribuição do Valor do Frete - Região {nome_da_regiao}')
ax2.set_xlabel('Estado')
ax2.set_ylabel('Valor do Frete')
st.pyplot(fig2)

# GRÁFICO 3: Histograma de Parcelas
st.subheader(f"3. Frequência do Número de Parcelas ({nome_da_regiao})")

fig3, ax3 = plt.subplots(figsize=(12, 8))
# Nota: Adicionei hue='customer_state' para o 'multiple=stack' fazer sentido visualmente
sns.histplot(
    data=regiao, 
    x='payment_installments', 
    hue='customer_state', # Adicionado para melhor visualização empilhada
    multiple='stack', 
    bins=range(1, int(regiao['payment_installments'].max()) + 2),
    palette='viridis',
    ax=ax3
)
ax3.set_title(f'Frequência do Número de Parcelas - Região {nome_da_regiao}')
ax3.set_xlabel('Número de Parcelas')
ax3.set_ylabel('Frequência')
# Ajuste dos ticks do eixo X
ax3.set_xticks(range(1, int(regiao['payment_installments'].max()) + 1))
st.pyplot(fig3)

# GRÁFICO 4: Média de Frete
st.subheader(f"4. Média do Valor do Frete por Estado ({nome_da_regiao})")

# Calculate average
average_freight = regiao.groupby('customer_state_full')['freight_value'].mean().reset_index()
average_freight = average_freight.sort_values(by='freight_value', ascending=False)

fig4, ax4 = plt.subplots(figsize=(14, 8))
sns.barplot(
    x='freight_value', 
    y='customer_state_full', 
    data=average_freight, 
    palette='Greens', 
    hue='customer_state_full', 
    legend=False,
    ax=ax4
)
ax4.set_title(f'Valor Médio do Frete - Região {nome_da_regiao}')
ax4.set_xlabel('Valor Médio do Frete (R$)')
ax4.set_ylabel('Estado')
st.pyplot(fig4)
