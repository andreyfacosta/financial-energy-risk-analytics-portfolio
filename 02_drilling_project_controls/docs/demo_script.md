# 2-3 Minute Interview Demo Script

This project is a drilling project controls dashboard built with synthetic oilfield operations data.

The business problem is that a drilling team needs to monitor whether wells are staying within AFE budget, whether the schedule is slipping, which rigs and contractors are performing well, where non-productive time is occurring, and whether HSE risk needs escalation.

I built the data pipeline in Python with pandas. The first script generates synthetic wells, drilling jobs, daily operations, AFE budgets, actual cost records, rigs, contractors, NPT events, HSE events, and a calendar table. The second script calculates daily project controls metrics and summary outputs for Power BI.

The key metrics are AFE budget, actual cost, cost variance, planned versus actual days, schedule variance, drilling progress, NPT hours, NPT percent, rig utilization, cost per meter, HSE incident count, forecast final cost, and risk flags.

The Power BI dashboard is designed with six pages: Executive Summary, Budget vs Actual, Schedule and NPT, Rig and Contractor Performance, HSE and Operational Risk, and Well Detail. The Executive Summary is for management review. The detail pages help explain why a well is over budget or behind schedule.

The main insight I would look for is whether cost variance is being driven by drilling progress, NPT, contractor performance, or HSE interruptions. That distinction matters because the business response is different: renegotiate contractor performance, adjust planning assumptions, improve logistics, or escalate safety controls.

What I would improve next is adding more detailed daily drilling report text, earned value logic, and a forecast model that separates fixed rig costs from variable service costs.
