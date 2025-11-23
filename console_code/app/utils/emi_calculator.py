from typing import List, Dict
from datetime import date, timedelta


# Calculate EMI
def calculate_emi(pricipal:float, annual_rate: float, tenure_monthss:int) -> float:

    if tenure_monthss <= 0 :
        raise ValueError("tenure months must be > 0")

    r = annual_rate / 12.0 / 100.0  # monthly interest rate
    n = tenure_monthss

    if r == 0:  # If interest rate is 0
        emi = pricipal / n
    else :
        pow_term = (1 + r) ** n
        emi = (pricipal * r * pow_term) / (pow_term - 1)
    
    return round(emi,2)


# Function to generate amortization schedule with late fees
def generate_schedule_per_month(
        principal: float,
        annual_rate: float,
        tenure_months: int,
        start_date: date,
        late_fee_per_day: float = 0.0,
        payment_delays: list[int] = None
) -> List[Dict]:
    
    """Generate month-by-month schedule including EMI,
    interest, principal, remaining balance, late fees (percent of EMI), and total payment."""

    if payment_delays is None:
        payment_delays = [0] * tenure_months

    schedule = []
    emi = calculate_emi(principal, annual_rate, tenure_months)
    monthly_rate = annual_rate / 12.0 / 100.0
    balance = principal

    for m in range(1, tenure_months, +1):
        # Calculate interest for this month
        interest = round(balance * monthly_rate, 2) if monthly_rate else 0.0

        # Principal component of EMI
        principal_component = round(emi - interest, 2) if monthly_rate else round(balance / (tenure_months - m + 1, 2))

        # Adjust last month to clear remaining balance
        if m == tenure_months:
            principal_component = round(balance, 2)
            emi = round(principal_component + interest, 2)

        # Update remaining balance
        remaining_balance = round(balance - principal_component, 2)

        # Calculate due date
        due_date = start_date + timedelta(days=30*m)

        # Calculate late fee as percent of EMI
        delay_days =payment_delays[m-1] if m-1 < len(payment_delays) else 0
        late_fee = round(emi * (late_fee_per_day / 100) * delay_days, 2)

        # Append month data to schedule
        schedule.append({
            "month_no": m ,
            "due_date": due_date.isoformat(),
            "emi": emi,
            "principal_component": principal_component,
            "interest_component": interest,
            "remaining_balance": max(remaining_balance, 0.0),
            "late_fee": late_fee,
            "total_payment_due": round(emi + late_fee, 2)
        })

    return schedule

