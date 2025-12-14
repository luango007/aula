import streamlit as st
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
# 1. Carregar dados (sem cache, direto)
titanic = sns.load_dataset('titanic')

# 2. Criar o seletor (direto na página)
options = ['sex', 'pclass', 'embarked', 'sibsp', 'parch']
selected_var = st.selectbox('Selecione a variável de agrupamento:', options)

# 3. Calcular a taxa de sobrevivência
# Usamos .dropna() para garantir que o groupby funcione se houver NaNs na coluna selecionada
try:
    survival_rate = titanic.dropna(subset=[selected_var]) \
                           .groupby(selected_var)['survived'] \
                           .mean() \
                           .reset_index()

    # 4. Criar o gráfico
    # É necessário criar fig, ax para passar para st.pyplot()
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        x=selected_var,
        y='survived',
        data=survival_rate,
        ax=ax
    )
    ax.set_ylim(0, 1) # Define o limite do eixo Y
    ax.set_title(f'Taxa de Sobrevivência por {selected_var}') # Um título mínimo

    # 5. Exibir o gráfico
    st.pyplot(fig)
