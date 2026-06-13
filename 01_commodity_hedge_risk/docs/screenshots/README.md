# Power BI Screenshot Placeholders

After building the `.pbix` in Power BI Desktop, export one screenshot for each report page and save it in this folder.

Use these exact filenames:

| File | Dashboard page | What it should show |
|---|---|---|
| `executive_summary.png` | Executive Summary | KPI cards, P&L trend, net open exposure, risk flags |
| `exposure_hedge_ratio.png` | Exposure & Hedge Ratio | Physical vs futures exposure, net exposure, hedge ratio |
| `pnl_margin.png` | P&L and Margin | Daily P&L, running P&L, margin requirement |
| `basis_risk.png` | Basis Risk | Cash vs futures prices, basis, basis risk |
| `stress_testing.png` | Stress Testing | Scenario impact by commodity and scenario |
| `counterparty_region.png` | Counterparty / Region View | Counterparty exposure, credit utilization, region view |

Recommended export approach:

1. Open the `.pbix` in Power BI Desktop.
2. Set each page to 16:9 view.
3. Use **File > Export > Export to PDF** or use a screenshot tool.
4. Save each page as a PNG with the exact filename above.
5. Re-open the Project 1 README and add image links when the files exist.

Do not use real employer screenshots or confidential data. The dashboard should be built only from the synthetic CSV files in this repository.
