from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def calculate_minimum_investment(A, EYR, DYR, Y, dt_per, eq_per, goal_amount, reserve_bool):
    '''
    A = Total monthly investment value
    EYR = Interest on Equity investment in %
    DYR = Interest on Debt (long term) investment in %
    Y = Goal Maturity year
    dt_per = Share of total investment into Debt
    eq_per = Share of total investment into Equity
    goal_amount = Goal Maturity amount after inflation
    '''

    EMR = EYR / 12 / 100
    DMR = DYR / 12 / 100
    M = Y * 12

    if reserve_bool == False:
        for i in range(1, int(A) + 1):
                FV = ((i * (dt_per / 100)) * ((((1 + DMR) ** (M)) - 1) * (1 + DMR)) / DMR) + (
                        (i * (eq_per / 100)) * ((((1 + EMR) ** (M)) - 1) * (1 + EMR)) / EMR)
                FV = round(FV)
                if FV >= goal_amount:
                    return i, FV
        return A, None

    elif reserve_bool == True:
        FV = goal_amount
        numerator = FV * DMR * 100 * EMR
        denominator = (dt_per * ((pow(1 + DMR, M) - 1) * (1 + DMR)) * EMR) + (eq_per * ((pow(1 + EMR, M) - 1) * (1 + EMR)) * DMR * 100)
        i = numerator / denominator
        return i, FV
    

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            data = pd.read_excel(file)

            result = pd.DataFrame(columns=['Client ID', 'Goal Number', 'Goal Amount', 'Future Value Achieved', 'Minimum Investment Amount Needed', 'Monthly investment Amount'])

            for client_id, row in data.iterrows():
                A = row['Monthly SIP Amount (A)']
                EYR = row['Equity Yearly Rate of Return (EYR)']
                DYR = row['Debt Yearly Rate of Return (DYR)']
                dt_per = row['Share in Debt Percentage Monthly (dt_per)']
                eq_per = row['Share in Equity Percentage Monthly (eq_per)']
                reserve_bool = True
                client_results = []
                deficit = 0
                for i in range(1, 11):  # Loop over up to 10 goals
                    goal_amount_col = f'Goal Amount {i}'
                    years_to_goal_col = f'Years to Goal {i} (Y)'
                    if goal_amount_col in row and years_to_goal_col in row:
                        goal_amount = row[goal_amount_col]
                        Y = row[years_to_goal_col]
                        min_monthly_investment, future_value = calculate_minimum_investment(A, EYR, DYR, Y, dt_per, eq_per, goal_amount, reserve_bool)
                        client_results.append({'Client ID': client_id,
                                                'Goal Number': i,
                                                'Goal Amount': goal_amount,
                                                'Future Value Achieved': future_value,
                                                'Minimum Investment Amount Needed': min_monthly_investment,
                                                'Monthly investment Amount': A})

                # Convert the list of dictionaries to a DataFrame
                client_results_df = pd.DataFrame(client_results)

                # Calculate total minimum investment needed for all goals
                total_min_investment = client_results_df['Minimum Investment Amount Needed'].sum()

                # Add a row for total minimum investment needed
                total_row = {'Client ID': client_id,
                             'Goal Number': 'Total',
                             'Goal Amount': '',
                             'Future Value Achieved': '',
                             'Minimum Investment Amount Needed': total_min_investment,
                             'Monthly investment Amount': ''}
                client_results_df = pd.concat([client_results_df, pd.DataFrame([total_row])], ignore_index=True)

                # Concatenate the DataFrame with the result DataFrame
                result = pd.concat([result, client_results_df], ignore_index=True)

            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            output_file = f'output_{timestamp}.xlsx'
            result.to_excel(output_file, index=False)
            return send_file(output_file, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
