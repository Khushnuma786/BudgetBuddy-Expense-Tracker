mport streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Initialize session state for expenses DataFrame if it doesn't already exist
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Year', 'Month', 'Category', 'Amount', 'Description'])

# Get the current year for the year selectbox
current_year = datetime.now().year

# Function to add a new expense
def add_expense(year, month, category, amount, description):
    # Ensure the 'Year' is an integer and 'Month' is a string
    year = int(year)
    month = str(month).zfill(2)  # Ensure month is always two digits, e.g., '01' for January

    new_expense = pd.DataFrame([[year, month, category, amount, description]], columns=['Year', 'Month', 'Category', 'Amount', 'Description'])
    
    # Append the new expense to the session state expenses DataFrame
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)

# Function to load expenses from a CSV or Excel file
def load_expenses(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            # Read the CSV file
            st.session_state.expenses = pd.read_csv(uploaded_file)

            # Clean the 'Year' column - strip any unwanted characters and convert to integer
            st.session_state.expenses['Year'] = st.session_state.expenses['Year'].apply(lambda x: str(x).replace(',', '').strip())
            st.session_state.expenses['Year'] = pd.to_numeric(st.session_state.expenses['Year'], errors='coerce')

        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            st.session_state.expenses = pd.read_excel(uploaded_file)

        # Clean column names and ensure they match expected names
        st.session_state.expenses.columns = [col.strip().title() for col in st.session_state.expenses.columns]

        # Ensure Year column is in integer format
        st.session_state.expenses['Year'] = st.session_state.expenses['Year'].astype(str).str.strip()
        st.session_state.expenses['Year'] = pd.to_numeric(st.session_state.expenses['Year'], errors='coerce')

        # Ensure Month column is in string format (in case it is stored as a number)
        st.session_state.expenses['Month'] = st.session_state.expenses['Month'].astype(str).str.strip()

        # Check if required columns exist; if not, raise an error
        required_columns = ['Year', 'Month', 'Category', 'Amount', 'Description']
        for col in required_columns:
            if col not in st.session_state.expenses.columns:
                st.error(f"Missing required column: {col}")
                return
        
        # Limit to only the required columns
        st.session_state.expenses = st.session_state.expenses[['Year', 'Month', 'Category', 'Amount', 'Description']]

# Function to save expenses to a CSV file
def save_expenses():
    st.session_state.expenses.to_csv('expenses.csv', index=False)
    st.success("Expenses Saved Successfully")

# Function to visualize expenses by category
def visualize_expenses(year, month):
    if not st.session_state.expenses.empty:
        # Ensure the year and month are integers or properly formatted
        year = int(year)
        month = str(month).zfill(2)  # Ensure the month is two digits (01, 02, etc.)

        # Filter the expenses by the selected year and month
        filtered_expenses = st.session_state.expenses[
            (st.session_state.expenses['Year'] == year) & 
            (st.session_state.expenses['Month'] == month)
        ]
        
        # Check if there are any filtered expenses for the selected year and month
        if not filtered_expenses.empty:
            # Group the filtered data by category and sum the amount for each category
            expense_summary = filtered_expenses.groupby('Category')['Amount'].sum().reset_index()

            # Plot the data
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=expense_summary, x='Category', y='Amount', ax=ax, palette='viridis')
            plt.xticks(rotation=45)
            plt.title(f'Total Expenses by Category for {month} {year}')
            st.pyplot(fig)
        else:
            st.warning(f"No expenses found for {month} {year}.")
    else:
        st.warning("No expenses available to visualize.")

# Function to calculate and display the total expenses for the selected month and year
def display_monthly_summary(year, month):
    # Ensure the year and month are integers or properly formatted
    year = int(year)
    month = str(month).zfill(2)  # Ensure the month is two digits (01, 02, etc.)

    month_expenses = st.session_state.expenses[
        (st.session_state.expenses['Year'] == year) & (st.session_state.expenses['Month'] == month)
    ]
    
    total_amount_spent = month_expenses['Amount'].sum()
    return total_amount_spent

# List of months for the selectbox
months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# List of years from 2000 to the current year
years = [str(year) for year in range(2000, current_year + 1)]

# Default year set to 2024
default_year = '2024'

# Streamlit app layout
st.title("BudgetBuddy Expense Tracker")

with st.sidebar:
    st.header('Add Expense')
    year = st.selectbox('Year', years, index=years.index(default_year))  # Set default year to 2024
    month = st.selectbox('Month', months)
    category = st.selectbox('Category', ['Food', 'Transport', 'Entertainment', 'Utilities', 'Other'])
    amount = st.number_input('Amount', min_value=0.0, format="%.2f")
    description = st.text_input('Description')
    if st.button('Add'):
        add_expense(year, month, category, amount, description)
        st.success("Expense Added!")

    st.header('File Operations')
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx', 'xls'])
    if uploaded_file is not None:
        load_expenses(uploaded_file)
        st.success("Expenses Loaded Successfully")

    if st.button('Save Expenses'):
        save_expenses()

# Display the expenses DataFrame
st.header('Expenses')
st.write(st.session_state.expenses)

# Select month and year for summary
selected_month = st.selectbox('Select a Month for Summary', months)
selected_year = st.selectbox('Select a Year for Summary', years, index=years.index(default_year))  # Default year to 2024
total_amount_spent = display_monthly_summary(selected_year, selected_month)

# Total budget input
total_budget = st.number_input(f'Enter your total budget for {selected_month} {selected_year}:', min_value=0.0, format="%.2f")

# Calculate the remaining budget
remaining_budget = total_budget - total_amount_spent

# Display the budget summary
st.write(f'**Total Budget for {selected_month} {selected_year}:** ${total_budget:.2f}')
st.write(f'**Total Amount Spent in {selected_month} {selected_year}:** ${total_amount_spent:.2f}')
st.write(f'**Remaining Budget:** ${remaining_budget:.2f}')

# Provide a visual indicator for the remaining budget
if remaining_budget >= 0:
    st.success(f'You are within budget for {selected_month} {selected_year}! ${remaining_budget:.2f} remaining.')
else:
    st.error(f'You have exceeded your budget for {selected_month} {selected_year} by ${abs(remaining_budget):.2f}.')

# Button to visualize expenses
st.header('Visualization')
if st.button('Visualize Expenses'):
    visualize_expenses(selected_year, selected_month)

# Optional: Additional information or advice
st.write('Keep track of your expenses to stay on top of your budget!')
