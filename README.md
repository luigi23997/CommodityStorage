# Storage
A Python library for modeling and analyzing commodity storage operations with cost tracking and profit prediction capabilities.
The Storage class provides a framework for simulating commodity storage facilities (such as gas storage, oil tanks, or grain silos) with realistic operational constraints and cost structures.
The required inputs are:
- max_vol: the maximum volume that can be stored
- rate: the maximum daily volume that can be injected or withdrawn
- inj_cost: the cost of injection per unit of volume 
- wit_cost: the cost of withdrawn per unit of volume
- cost_per_day_per_unit: the storing cost per unit of volume per day 

## Installation
```bash
pip install pandas numpy 
```

## Quick start
```python
from storage import Storage
# Create storage facility
storage = Storage(
    max_vol=1000,           # Max capacity
    rate=50,                # Max daily rate
    inj_cost=2.0,          # Injection cost per unit
    wit_cost=1.5,          # Withdrawal cost per unit
    cost_per_day_per_unit=0.1,  # Daily storage cost
    start_day='2024-01-01'
)
# Process operations
injection_dates = ['2024-01-15', '2024-02-01']
withdrawal_dates = ['2024-03-15', '2024-04-01']
injection_volumes = [40, 30]
withdrawal_volumes = [35, 35]

storage.process(injection_dates, withdrawal_dates, injection_volumes, withdrawal_volumes)
storage.cost_overview()
```


## Test.ipyn
In test.ipynb there an example with the analysis of natural gas storage, with price prediction using Fourier series and linear regression. Data from JPMorgan Chase & Co. Quantitative Research Job Simulation - Forage

