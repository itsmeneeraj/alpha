import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from gbwm_solver import goal_programming_solver

# Set page configuration
st.set_page_config(page_title="Goal Based Wealth Management", page_icon="💸")

# Custom CSS to enhance the style
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
    }
    .title {
        font-size: 10px; /* Adjust the font size as needed */
    }
    .block-container {
        max-width: 800px;
        margin: auto;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        transition-duration: 0.4s;
        cursor: pointer;
        border-radius: 8px;
    }
    .stButton button:hover {
        background-color: white;
        color: black;
        border: 2px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# Title and description
st.markdown("<h1 style='font-size: 35px;'>💸 Goal Based Wealth Management</h1>", unsafe_allow_html=True)
#st.title("💸 Goal Based Wealth Management")
st.markdown("""
    Welcome to the Goal Based Wealth Management tool. This application helps you plan your investments to achieve your financial goals. 
    Please provide the necessary inputs below to get started.
""")

# Function to parse uploaded Excel file
def parse_excel(file):
    df = pd.read_excel(file)
    return df

# Initialize session state attributes
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

if 'num_goals' not in st.session_state:
    st.session_state.num_goals = 1

if 'goals' not in st.session_state:
    st.session_state.goals = []

if 'recurring' not in st.session_state:
    st.session_state.recurring = [False] * st.session_state.num_goals

if 'upload_option' not in st.session_state:
    st.session_state.upload_option = "Update Details Manually"



# User inputs
upload_option = st.sidebar.radio("Choose an option:", ("Update Details Manually", "Upload Excel File"))

if upload_option == "Upload Excel File":
    uploaded_file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx", "xls"])

    if uploaded_file is not None:
        data = parse_excel(uploaded_file)
        required_columns = ['Yearly Return in Equity', 'Yearly Return in Debt', 'Equity Allocation', 
                            'Total Monthly Investment Capacity', 'Goal Amount', 'Number of Years', 'Priority']
        
        if not all(col in data.columns for col in required_columns):
            st.error("Please make sure all required columns are present in the Excel file.")
        else:
            st.session_state.data = data
            st.session_state.num_goals = len(data)
            st.session_state.submitted = True
            st.session_state.upload_option = "Upload Excel File"

if upload_option == "Update Details Manually":

     with st.sidebar.form(key='investment_parameters'):
        RE = st.number_input("Yearly Return in Equity (as a decimal, e.g., 0.07 for 7%)", value=0.11, step=0.01, format="%.2f")
        RD = st.number_input("Yearly Return in Debt (as a decimal, e.g., 0.05 for 5%)", value=0.07, step=0.01, format="%.2f")
        p_e = st.number_input("Equity Allocation (as a decimal, e.g., 0.6 for 60%)", value=0.4, step=0.01, format="%.2f")
        p_d = st.number_input("Debt Allocation (as a decimal, e.g., 0.6 for 60%)", value=1-p_e, step=0.01, format="%.2f", disabled = True)
        Total_monthly_Investment_capacity = st.number_input("Total Monthly Investment Capacity", value=1000.0, step=100.0, format="%.2f")
        num_goals = st.number_input("Number of Financial Goals", min_value=1, step=1, value=st.session_state.num_goals)
        submit_button = st.form_submit_button(label='Submit')

        if submit_button:
            st.session_state.num_goals = num_goals
            st.session_state.submitted = True
            st.session_state.upload_option = "Update Details Manually"
            if len(st.session_state.goals) != st.session_state.num_goals:
                st.session_state.goals = [(0, 0, 1)] * st.session_state.num_goals
                # Update recurring list to match the number of goals
            if len(st.session_state.recurring) != st.session_state.num_goals:
                st.session_state.recurring = [False] * st.session_state.num_goals

if st.session_state.submitted:
    if st.session_state.upload_option == "Update Details Manually":

        for i in range(st.session_state.num_goals):
            Goal = st.sidebar.number_input(f"Goal Amount for Goal {i + 1}", value=float(st.session_state.goals[i][0]), step=1000.0, key=f'goal_{i}')
            Years = st.sidebar.number_input(f"Number of Years for Goal {i + 1}", value=float(st.session_state.goals[i][1]), step=1.0, key=f'years_{i}')
            Priority = st.sidebar.number_input(f"Priority for Goal {i + 1} (1-10)", value=int(st.session_state.goals[i][2]), min_value=1, max_value=10, step=1, key=f'priority_{i}')
            Recurring = st.sidebar.checkbox(f"Recurring Goal {i + 1}", value=st.session_state.recurring[i], key=f'recurring_{i}')
            st.session_state.goals[i] = (Goal, Years, Priority)
            st.session_state.recurring[i] = Recurring

        # Sorting goals based on priority (higher priority first)
        st.session_state.goals = [(goal, year, priority, st.session_state.recurring[i]) for i, (goal, year, priority) in enumerate(st.session_state.goals)]
        st.session_state.goals.sort(reverse=True, key=lambda x: x[2])
    else:
        st.session_state.goals = [(row['Goal Amount'], row['Number of Years'], row['Priority']) for idx, row in st.session_state.data.iterrows()]
        RE = st.session_state.data['Yearly Return in Equity'].iloc[0]
        RD = st.session_state.data['Yearly Return in Debt'].iloc[0]
        p_e = st.session_state.data['Equity Allocation'].iloc[0]
        Total_monthly_Investment_capacity = st.session_state.data['Total Monthly Investment Capacity'].iloc[0]

        # Sorting goals based on priority (higher priority first)
        st.session_state.goals.sort(reverse=True, key=lambda x: x[2])

    if st.sidebar.button("Calculate Investments"):
        st.header("Investment Calculation Results")
        remaining_investment_capacity = Total_monthly_Investment_capacity
        investments = []
        annual_gains = []
        for i, (Goal, Years, Priority), Recurring in enumerate(st.session_state.goals):
            if Years == 0:
                st.error(f"Number of years for goal amount {Goal} cannot be zero.")
                continue
            if remaining_investment_capacity > 0:
                original_solution = goal_programming_solver(RE, RD, int(Years), p_e, Goal, Recurring)
                remaining_investment_capacity -= original_solution
                investments.append((Goal, Years, original_solution, Priority, Recurring))
                st.success(f"Minimum investment needed to achieve goal amount {Goal} in {int(Years)} years with priority {Priority}: \u20B9{original_solution:.2f}")
                st.info(f"Remaining investment amount: \u20B9{remaining_investment_capacity:.2f}")
                if remaining_investment_capacity <= 0:
                    st.warning('Remaining investment amount is negative; subsequent goals will not be considered for investment optimization.')
                    break
                
                # Calculate annual gains
                annual_gain = []
                for year in range(int(Years)):  # Convert Years to integer here
                    annual_return = original_solution * (p_e * RE + (1 - p_e) * RD)
                    original_solution += annual_return
                    annual_gain.append(original_solution)
                annual_gains.append((Goal, annual_gain, Priority, Recurring))
            else:
                st.warning('Remaining investment amount is negative; subsequent goals will not be considered for investment optimization.')
                break

        # Plotting annual gains for each goal
        for goal, gains, priority, recurring in annual_gains:
            years = list(range(1, len(gains) + 1))
            fig, ax = plt.subplots()
            ax.bar(years, gains, color='b')
            ax.set_title(f'Annual Gains for Goal of ₹{goal} with Priority {priority} ({"Recurring" if recurring else "Non-recurring"})')
            ax.set_xlabel('Year')
            ax.set_ylabel('Investment Value (₹)')
            ax.grid(True)
            st.pyplot(fig)
