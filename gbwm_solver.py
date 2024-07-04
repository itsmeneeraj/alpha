# Importing required libraries
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import linprog

# Defining the objective function for optimization
def objective(x):

    '''
    Minimization of E+D: The objective function E+D is defined to be minimized. 
    By optimizing this sum, the algorithm finds the combination of E and D that 
    minimizes the total investment required to meet the financial goal.
    '''

    return x[0] + x[1]

# Defining the constraints for optimization
def constraints(x, RE_years, RD_years, p_e, p_d, Goal):
    '''
    First Constraint: This constraint ensures that the sum of the future values of equity and debt 
    investments over the specified number of years equals the financial goal. The equality sign is 
    used because we want the value of this expression to be exactly equal to the goal. If it's 
    not equal, the solver will try to find values of E and D that make it so.

    Second Constraint: This constraint ensures that the amount invested in equity (E) is equal to 
    the proportion of equity allocation (p_e) multiplied by the total investment (E+D). 
    The equality sign is used because we want the investment in equity to be precisely 
    this proportion of the total investment
    

    Third Constraint: Similar to the second constraint, this ensures that the amount invested 
    in debt (D) is equal to the proportion of debt allocation (p_d) multiplied by the 
    total investment (E+D). The equality sign is used for the same reason as in the second constraint.
    
    '''
    return [
        {'type': 'ineq', 'fun': lambda x, lb = Goal, i = 0: (RE_years*x[0]) + (RD_years*x[1]) - lb},
        {'type': 'ineq', 'fun': lambda x, lb = 0.0, i = 1: p_e * x[0] + p_e * x[1] - x[0] - lb}
        ]

# Function to solve the optimization problem
def solve(RE_years, RD_years, Years, p_e, p_d, Goal):
    x0 = np.array([Goal*p_e/12/Years, Goal*p_d/12/Years])
    bnds = ((0, None), (0, None))
    # Using scipy's minimize function for optimization
    res = minimize(objective, x0, args=(), bounds=bnds, method='SLSQP', constraints=constraints(x0, RE_years, RD_years, p_e, p_d, Goal))
    return (res.x[0]+res.x[1])

# Function to solve the goal programming problem
def goal_programming_solver(RE, RD, Years, p_e, Goal):
    p_d = 1 - p_e
    # Getting the original solution
    RE_years = 12*((((1+RE)**Years)-1)/RE)
    RD_years = 12*((((1+RD)**Years)-1)/RD)
    original_solution = solve(RE_years, RD_years, Years, p_e, p_d, Goal)
    # perturbations = [0.9, 0.95, 1.05, 1.1]
    # perturbed_solutions = []
    # # Looping through perturbations and getting perturbed solutions
    # for perturbation in perturbations:
    #     perturbed_solution = solve(RE*perturbation, RD*perturbation, Years, p_e*perturbation, p_d*perturbation, Goal*perturbation)
    #     perturbed_solutions.append(perturbed_solution)
    return original_solution
