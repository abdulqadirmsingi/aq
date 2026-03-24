# API Documentation

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints by Domain

### Energy
- `GET /energy/fuel` — Fuel price time-series
- `GET /energy/gas` — Gas price time-series
- `GET /energy/electricity` — Electricity price time-series

### Money
- `GET /money/exchange-rates` — Currency exchange rates
- `GET /money/inflation` — Inflation data
- `GET /money/stocks` — Stock market data

### Living Cost
- `GET /living-cost/rent` — Rent price data
- `GET /living-cost/land` — Land price data

### Medicine
- `GET /medicine/drug-prices` — Drug/pharmaceutical prices

### Human Resources
- `GET /hr/salaries` — Salary and wage data
- `GET /hr/job-trends` — Job market trends

> Full OpenAPI docs available at `/docs` when backend is running.
