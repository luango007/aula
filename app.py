import streamlit as st

st.title("primeiro app")

st.header("vamos fazer algo")
n = st.number_input('escolhar um numero')
st.write(f'o numero que voce escolheu ao quadrado e (n**2)')