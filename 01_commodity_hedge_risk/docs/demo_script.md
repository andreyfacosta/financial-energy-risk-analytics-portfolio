# 2-3 Minute Interview Demo Script

Hi, I will walk you through a commodity hedge risk dashboard project I built using synthetic data.

The business context is a Canadian grain company that buys and sells physical grain and uses futures contracts to hedge price exposure. The risk team needs to understand whether the portfolio is properly hedged, how P&L is moving, where basis risk is increasing, how much margin is required, and whether any counterparties are approaching credit limits.

I built the data pipeline in Python with pandas. The first script generates synthetic but realistic source tables: physical transactions, futures positions, cash prices, futures prices, FX rates, margin requirements, counterparties, commodities, and a calendar table. The second script creates analytical outputs for Power BI, including daily risk metrics, counterparty exposure, risk flags, stress test results, and a summary table. I also created a SQLite database and SQL views to show the same model from a database perspective.

The key metrics are physical exposure, futures exposure, net open exposure, hedge ratio, daily and cumulative P&L, basis, basis risk, margin requirement, VaR 95 and 99 approximations, stress test impact, and counterparty credit utilization.

The dashboard is designed as six Power BI pages. The Executive Summary page gives leadership the current risk snapshot. The Exposure and Hedge Ratio page shows whether futures hedges are aligned with physical exposure. The P&L and Margin page explains mark-to-market movement and collateral pressure. The Basis Risk page compares cash and futures prices. The Stress Testing page shows impacts from commodity price, basis, and FX shocks. The Counterparty page highlights credit utilization and watch list items.

In the current synthetic dataset, the portfolio appears over-hedged, with a weighted hedge ratio around 3.03. Net open exposure is about CAD negative 8.69 million, latest daily P&L is about CAD negative 52.6 thousand, and margin requirement is about CAD 5.37 million. The counterparty table also shows one synthetic limit-pressure case above 100 percent utilization, which would require review.

What I would improve next is adding more detailed hedge effectiveness logic, contract roll analysis, historical backtesting, and a Power BI `.pbix` file with final screenshots. This project demonstrates how I connect financial risk concepts, Python and SQL data preparation, and executive reporting for practical business decisions.
