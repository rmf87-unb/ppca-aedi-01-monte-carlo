import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import plotly.express as px
import locale
from stqdm import stqdm

locale.setlocale(locale.LC_ALL, "pt_BR")

st.title("Custo do Apontamento Tardio de Óbitos")
st.text(
    "Qual o custo de não se apontar tempestivamente um óbito em uma folha de pagamento? O modelo estima o potencial prejuízo a partir das variáveis a seguir:"
)
# Define parameters
col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
inputted_simulated_years = col1.number_input("Tempo simulado (anos): ", 1, 5, value=5)
inputted_max_delay = col2.number_input(
    "Atraso médio no apontamento do óbito (meses):", 1, 12, value=6
)
inputted_recipients = col3.number_input(
    "Beneficiários (quantidade): ", 0, 1000000, value=10000
)
inputted_salary_mean = col1.number_input("Salário Médio (R$):", 0, 50000, value=5000)
inputted_salary_std_dev = col2.number_input(
    "Desvio Padrão Salário (R$):", 0, 50000, value=2000
)
inputted_num_runs = col3.number_input("Simulações (quantidade):", 1, 500000, value=1000)

# Constants
pop_total = 210e6  # total pop
lambda_d = 1544611 / 12  # SIRC 2022 monthly deaths

start_sim_button = st.button("Simular")
stats = []


def simulate(
    simulated_years: int,
    max_delay: int,
    recipients: int,
    salary_mean: int,
    salary_std_dev: int,
    num_runs: int,
    runs_stats,
):

    bar = stqdm(total=num_runs)
    for run in range(num_runs):
        recipients_sampled = np.ones(recipients, int).tolist()  # monthly payments

        # Poisson distribution for total month deaths
        total_deaths_sampled = np.random.poisson(lambda_d, 12 * simulated_years)

        # Lognormal for salaries
        sigma = np.sqrt(np.log(1 + (salary_std_dev / salary_mean) ** 2))
        mean = np.log(salary_mean) - sigma**2 / 2
        salaries_sampled = np.random.lognormal(mean, sigma, recipients).tolist()

        # Losses calculation for each month
        losses = []
        for i, month_deaths in enumerate(total_deaths_sampled):
            death_ratio = month_deaths / pop_total
            ## prob deaths per month
            deaths_sampled = np.random.binomial(1, death_ratio, len(recipients_sampled))
            dead_indexes = np.nonzero(deaths_sampled)[0]
            ## reducing remaining sample
            for j in reversed(dead_indexes):
                losses.append({"id": j, "month": i + 1, "salary": salaries_sampled[j]})
                recipients_sampled.pop(j)
                salaries_sampled.pop(j)

        # Sum total losses
        total_loss = 0
        for loss in losses:
            delay = 12 * simulated_years - loss["month"]
            delay = delay if delay <= max_delay else max_delay
            total_loss += delay * loss["salary"]
        runs_stats.append(
            {
                "run": run,
                "Perdas Acumuladas": total_loss,
                "Mortes": recipients - len(recipients_sampled),
            }
        )
        bar.update(1)

    return pd.DataFrame(
        data=runs_stats,
        columns=[
            "Perdas Acumuladas",
            "Mortes",
            "Salários na Folha (LogNormal)",
            "Mortes Mensal (Poisson)",
        ],
    )


def report(run_df: pd.DataFrame, container, simulated_years: int):
    tab1, tab2, tab3, tab4, tab5 = container.tabs(
        ["Métricas", "Histograma", "Boxplot", "Dispersão", "Metodologia"]
    )
    mean_value = run_df["Perdas Acumuladas"].mean()
    std_dev = run_df["Perdas Acumuladas"].std()
    median = run_df["Perdas Acumuladas"].median()
    medianDeaths = run_df["Mortes"].median()
    minimum = run_df["Perdas Acumuladas"].min()
    maximum = run_df["Perdas Acumuladas"].max()
    iqr = run_df["Perdas Acumuladas"].quantile(0.75) - run_df[
        "Perdas Acumuladas"
    ].quantile(0.25)

    tab1.subheader("Métricas")
    col1, col2 = tab1.columns(2, vertical_alignment="bottom")
    col1.text(f"Prejuízo Estimado: {locale.currency(mean_value, grouping=True)}")
    col2.text(f"Mediana de Mortes em {simulated_years} anos: {medianDeaths}")
    col1.text(f"Desvio Padrão do Prejuízo: {locale.currency(std_dev, grouping=True)}")
    col2.text(f"Mediana do Prejuízo: R$ {locale.currency(median, grouping=True)}")
    col4, col5, col6 = tab1.columns(3, vertical_alignment="bottom")
    col4.text(f"Distância Interquartílica: R$ {locale.currency(iqr, grouping=True)}")
    col5.text(f"Menor Prejuízo Simulado: R$ {locale.currency(minimum, grouping=True)}")
    col6.text(f"Máximo Prejuízo Simulado: R$ {locale.currency(maximum, grouping=True)}")

    tab2.subheader("Histograma")
    fig2 = px.histogram(run_df, x="Perdas Acumuladas")
    tab2.plotly_chart(fig2)

    tab3.subheader("Boxplot")
    fig = px.box(run_df, y="Perdas Acumuladas")
    tab3.plotly_chart(fig)

    tab4.subheader("Gráfico de Dispersão")
    tab4.scatter_chart(data=run_df, x="Perdas Acumuladas", y="Mortes")

    tab5.subheader("Metodologia")
    tab5.markdown(
        """
        Há três distribuições principais no [código](https://github.com/rmf87-unb/ppca-aedi-01-monte-carlo).
        """
    )
    tab5.markdown(
        """
        A primeira é uma distribuição de Poisson para estimar, mês a mês, a quantidade de mortes no brasil:
        """
    )
    tab5.code(
        """
        # Poisson distribution for total month deaths
        total_deaths_sampled = np.random.poisson(lambda_d, 12 * simulated_years)
        """
    )
    tab5.markdown(
        """
        A segunda é o uso da LogNormal para a distribuição de salários:
        """
    )
    tab5.code(
        """
        # Lognormal for salaries
        sigma = np.sqrt(np.log(1 + (salary_std_dev / salary_mean) ** 2))
        mean = np.log(salary_mean) - sigma**2 / 2
        salaries_sampled = np.random.lognormal(mean, sigma, recipients).tolist()
        """
    )
    tab5.markdown(
        """
        A última utilizada é a binomial para se sortear as fatalidades na folha:
        """
    )
    tab5.code(
        """
        for i, month_deaths in enumerate(total_deaths_sampled):
            death_ratio = month_deaths / pop_total
            ## prob deaths per month
            deaths_sampled = np.random.binomial(1, death_ratio, len(recipients_sampled))
            dead_indexes = np.nonzero(deaths_sampled)[0]
        """
    )
    tab5.markdown(
        """
        A distribuição resultante para o prejuízo estimado, apesar de não demonstrado, aparenta ser gaussiana.
        Seu histograma e seu boxplot, para experimento com mais de 1000 simulações, tendem ao centro como observamos nas abas ao lado.
        """
    )


if start_sim_button:
    container = st.empty()
    data = simulate(
        inputted_simulated_years,
        inputted_max_delay,
        inputted_recipients,
        inputted_salary_mean,
        inputted_salary_std_dev,
        inputted_num_runs,
        stats,
    )
    report(data, container, inputted_simulated_years)
