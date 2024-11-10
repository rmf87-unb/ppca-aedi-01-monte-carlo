import pandas as pd
import locale
import matplotlib.pyplot as plt
import plotly.express as px


def report(run_df: pd.DataFrame, container, simulated_years: int):
    tab1, tab2, tab3, tab4, tab5 = container.tabs(
        ["Métricas", "Histograma", "Boxplot", "Dispersão", "Metodologia"]
    )
    mean_value = run_df["Perdas Acumuladas"].mean()
    std_dev = run_df["Perdas Acumuladas"].std()
    median = run_df["Perdas Acumuladas"].median()
    mean = run_df["Perdas Acumuladas"].mean()
    kurt = run_df["Perdas Acumuladas"].kurt()
    minimum = run_df["Perdas Acumuladas"].min()
    maximum = run_df["Perdas Acumuladas"].max()
    medianDeaths = run_df["Mortes"].median()
    iqr = run_df["Perdas Acumuladas"].quantile(0.75) - run_df[
        "Perdas Acumuladas"
    ].quantile(0.25)

    tab1.subheader("Métricas")
    col1, col2 = tab1.columns(2, vertical_alignment="bottom")
    col1.text(f"Prejuízo Estimado: {locale.currency(mean_value, grouping=True)}")
    col2.text(f"Mediana de Mortes em {simulated_years} anos: {medianDeaths}")
    col1.text(f"Média do Prejuízo: R$ {locale.currency(mean, grouping=True)}")
    col2.text(f"Mediana do Prejuízo: R$ {locale.currency(median, grouping=True)}")
    col1.text(f"Desvio Padrão do Prejuízo: {locale.currency(std_dev, grouping=True)}")
    col2.text(f"Curtose do Prejuízo: {locale.str(kurt)}")
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
        A primeira é uma distribuição de Poisson para estimar, mês a mês, a quantidade de mortes no Brasil.  \n
        Formalmente:
        """
    )
    tab5.latex(
        r"""
        \textbf{Poisson}(\lambda)  \newline
        \textit{fpm} \quad P(X = x \mid \lambda) = \frac{e^{-\lambda} \lambda^x}{x!}, \quad x = 0, 1, \dots; \quad 0 \leq \lambda < \infty  \newline
        \textit{média e variância} \quad \mathbb{E}X = \lambda, \quad \operatorname{Var}X = \lambda   \newline
        \textit{fgm} \quad M_X(t) = e^{\lambda (e^t - 1)}
        """
    )
    tab5.markdown(
        """
        Em CASELLA (2024), reproduzido a seguir, define-se que é possível considerar a distribuição de Poisson em processos que atendam os postulados de Poisson.  \
        No caso dos falecimentos:
        - Sem falecimentos no início da série
        - Independência de falecimentos nos períodos
        - Mortes dependem apenas do tamanho do período de tempo
        - Para períodos pequenos, probabilidade tende a lambda, ou seja, é a média e proporcional ao tamanho do período.
        - Ausência de falecimentos simultâneos

        Para os fins deste experimento, é razoável considerar que os 5 postulados são atendidos, pois há interesse apenas na compatibilidade de grandeza do fenômeno, não em suas mecânicas.  \
        Para outros fins, há metodologias mais sofisticadas acerca da modelagem de taxas de falecimento, por exemplo em Rowland (2003)
        """
    )
    tab5.markdown(
        """
        Na implementação, a média histórica foi obtida dos dados do Sistema Integrado de Registro Civil (SIRC) para 2022 disponíveis online:
        """
    )
    tab5.code(
        """
        # Constants
        pop_total = 210e6  # total pop
        lambda_d = 1544611 / 12  # from SIRC 2022
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
        A segunda distribuição utilizada foi a LogNormal para a simulação dos salários na folha de pagamento.
        Formalmente:
        """
    )
    tab5.latex(
        r"""
        \textbf{Lognormal}(\mu, \sigma^2)   \newline
        \text{fdp } f(x \mid \mu, \sigma^2) = \frac{1}{\sqrt{2 \pi \sigma} \, x} e^{-\frac{(\log x - \mu)^2}{2 \sigma^2}}, \quad 0 \leq x < \infty, \quad -\infty < \mu < \infty, \quad \sigma > 0 \newline
        \textit{média e variância } \mathbb{E}X = e^{\mu + \sigma^2 / 2}, \quad \text{Var} X = e^{2(\mu + \sigma^2)} - e^{2\mu + \sigma^2} \newline
        \textit{momentos } \mathbb{E}X^n = e^{n \mu + n^2 \sigma^2 / 2}
        """
    )

    tab5.markdown(
        """
        Segundo Casella (2024), a LogNormal é interessante quando os dados são naturalmente enviesados à direita.  \
        Heckman e Saltinger (2015) contextualizam historicamente, a partir do artigo de A.D. Roy  ‘The distribution of earnings and of individual output’ de 1950, que este é o caso da distribuição de renda na população.
        No código:
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
        A terceira distribuição utilizada é a binomial para se sortear as fatalidades na folha.
        Formalmente:
        """
    )

    tab5.latex(
        r"""
        \textbf{Binomial }(n, p) \newline
        \text{fpm } \quad P(X = x \mid n, p) = \binom{n}{x} p^x (1 - p)^{n - x}; \quad x = 0, 1, 2, \dots, n; \quad 0 \leq p \leq 1 \newline
        \textit{média e variância } \mathbb{E}X = np, \quad \text{Var} X = np(1 - p) \newline
        \textit{momentos } M_X(t) = \left[ p e^t + (1 - p) \right]^n
        """
    )

    tab5.markdown(
        """
        A aplicação da distribuição binomial se justifica por, para um indivíduo no conjunto folha de pagamento, haver apenas duas possibilidades consideradas, sob uma probabilidade p derivada do tamanho da folha de pagamento diante do tamanho da população do país.
        A premissa básica mais importante é que as mortes são eventos independentes.
        No código:
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
        Seu histograma e seu boxplot, para experimentos com mais de 1000 simulações, tendem ao centro como observamos nas abas ao lado.
        Da mesma forma, sua média e mediana se aproximam enquanto a curtose se aproxima de zero.
        """
    )

    tab5.markdown(
        """
        Referências:  \n
        CASELLA, George; BERGER, Roger L. Statistical Inference. 2nd. ed. Boca Raton: CRC Press, 2024.
        ROWLAND, Donald T. Demographic Methods and Concepts. Oxford: Oxford University Press, 2003.
        HECKMAN, James J.; SALTINGER, Michael. Introduction to the distribution of earnings and of individual output, by A.D. Roy. The Economic Journal, v. 125, n. 583, p. 378-402, mar. 2015.
        """
    )
