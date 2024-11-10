import numpy as np
import pandas as pd
from stqdm import stqdm


def simulate(
    simulated_years: int,
    max_delay: int,
    recipients: int,
    salary_mean: int,
    salary_std_dev: int,
    num_runs: int,
    lambda_d: float,
    pop_total: int,
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
