def calculate_minimum_investment(A, EYR, DYR, Y, dt_per, eq_per, goal_amount):
    '''
    A = Total monthly investment value
    EYR = Interest on Equity investment in %
    DYR = Interest on Debt (long term) investment in %
    Y = Goal Maturity year
    dt_per = Share of total investment into Debt
    eq_per = Share of total investment into Equity
    goal_amount = Goal Maturity amount after inflation
    '''
    #Convert EMR and DMR into monthly interest value. Convert Maturity year to toal months to Mature
    EMR = EYR / 12 / 100
    DMR = DYR / 12 / 100
    M = Y * 12

    # Loop to find out minimum investment needed to achive goal maturity amount
    
    for i in range(1, A):
        FV = ((i * (dt_per / 100)) * ((((1 + DMR) ** (M)) - 1) * (1 + DMR)) / DMR) + (
                (i * (eq_per / 100)) * ((((1 + EMR) ** (M)) - 1) * (1 + EMR)) / EMR)
        FV = round(FV)
        if FV >= goal_amount:
            return i, FV
    return A

# Take input from user
A = int(input("Enter the monthly SIP amount: "))
EYR = float(input("Enter the Equity yearly rate of return: "))
DYR = float(input("Enter the Debt yearly rate of return: "))
dt_per = int(input("Enter the share in Debt percentage monthly: "))
eq_per = int(input("Enter the share in Equity percentage monthly: "))


# take multiple goal maturty amount and years to mature the goals
goals = []
while True:
    goal_amount = int(input("Enter the goal amount (enter 0 to finish): "))
    if goal_amount == 0:
        break
    Y = int(input("Enter the number of years for this goal: "))
    goals.append((goal_amount, Y))

# Sort goals in descending order of priority based on goal amount
goals.sort(reverse=True)

#Call class object to calculate minimum investment amount needed
for goal_amount, Y in goals:
    min_monthly_investment, future_value = calculate_minimum_investment(A, EYR, DYR, Y, dt_per, eq_per, goal_amount)
    print("Goal Amount:", goal_amount)
    print("Future value achieved:", future_value)
    print("Minimum investment amount needed:", min_monthly_investment)
    remaining_monthly_amount = A - min_monthly_investment
    A = remaining_monthly_amount
    print("Remaining monthly investment:", remaining_monthly_amount)
    
