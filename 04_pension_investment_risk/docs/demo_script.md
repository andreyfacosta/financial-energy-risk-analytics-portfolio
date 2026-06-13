# 2-3 Minute Interview Demo Script

This project is a pension investment risk dashboard built with synthetic retirement portfolio data.

The business problem is that a pension or retirement analytics team needs to monitor asset allocation, returns versus benchmark, volatility, drawdown, FX exposure, contribution flows, scenario impacts, and retirement projections.

I built the pipeline in Python with pandas. The first script generates synthetic portfolios, members, asset classes, holdings, daily prices, FX rates, contributions, withdrawals, benchmarks, and a calendar table. The second script calculates daily portfolio values, returns, cumulative return, benchmark return, active return, allocation drift, drawdown, volatility, FX exposure, contribution projection, and stress scenario impact.

The Power BI dashboard is designed with six pages: Executive Summary, Asset Allocation, Returns vs Benchmark, Volatility and Drawdown, FX Exposure and Scenarios, and Retirement Projection.

The key business value is that the dashboard separates investment performance from contribution flows and connects risk metrics to member outcomes. A portfolio can show positive long-term growth but still have allocation drift, FX concentration, or drawdown pressure that requires review.

What I would improve next is more detailed performance attribution, member segmentation, contribution adequacy analysis, and scenario assumptions by age cohort.
