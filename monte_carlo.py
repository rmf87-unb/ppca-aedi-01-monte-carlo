import streamlit as st
import locale
from simulate import simulate
from report import report

locale.setlocale(locale.LC_ALL, "pt_BR")

# Constants
pop_total = 210e6  # total pop
lambda_d = 1544611 / 12  # from SIRC 2022

# User inputs
st.title("Custo do Apontamento Tardio de Óbitos")
st.text(
    "Qual o custo de não se apontar tempestivamente um óbito em uma folha de pagamento? O modelo estima o potencial prejuízo a partir das variáveis a seguir:"
)
col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
inputted_simulated_years = col1.number_input("Tempo simulado (anos): ", 1, 5, value=5)
inputted_max_delay = col2.number_input(
    "Atraso máximo no apontamento do óbito (meses):", 1, 12, value=6
)
inputted_recipients = col3.number_input(
    "Beneficiários (quantidade): ", 0, 1000000, value=10000
)
inputted_salary_mean = col1.number_input("Salário Médio (R$):", 0, 50000, value=5000)
inputted_salary_std_dev = col2.number_input(
    "Desvio Padrão Salário (R$):", 0, 50000, value=2000
)
inputted_num_runs = col3.number_input("Simulações (quantidade):", 1, 500000, value=1000)
start_sim_button = st.button("Simular")

# Experiment
stats = []
if start_sim_button:
    container = st.empty()
    data = simulate(
        inputted_simulated_years,
        inputted_max_delay,
        inputted_recipients,
        inputted_salary_mean,
        inputted_salary_std_dev,
        inputted_num_runs,
        lambda_d,
        pop_total,
        stats,
    )
    report(data, container, inputted_simulated_years)
