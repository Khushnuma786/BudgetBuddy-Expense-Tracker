import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date','Category','Amount','Description'])


def add_expense(date,category,amount,description):
    new_expense= pd.DataFrame([[date,category,amount,description]], columns = st.session_state.expenses.columns)
    st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index = True)


def load_expenses():
    uploaded_file = st.file_uploader("choose a file",type=['csv'])
    if uploaded_file is not None:
        st.session_state.expenses = pd.read_csv(uploaded_file)


def save_expenses():
    st.session_state.expenses.to_csv('expenses.csv',index=False)
    st.success("Expenses Saved Successfully")

def visualize_expenses():
    if not st.session_state.expenses.empty:
           fig, ax = plt.subplots()
           sns.barplot(data=st.session_state.expenses, x='Category',y="Amount", ax=ax)
           plt.xticks(rotation=45)
           st.pyplot(fig)
    else:
        st.warning("No Expenses to Visulaize")





st.title("BudgetBuddy Expense Tracker")
with st.sidebar:
    st.header('Add Expense')
    date = st.date_input("Date")
    category = st.selectbox('Category',['Food','Transport','Entertainment','Utilities','Other'])
    amount = st.number_input('Amount',min_value=0.0,format="%.2f")
    description = st.text_input('Description')
    if st.button('Add'):
        add_expense(date,category,amount,description)
        st.success("Expense Added!")
    st.header('File Operations')
    if st.button('Save Expenses'):
        save_expenses()
    if st.button('Load Expenses'):
        load_expenses()

st.header('Expenses')
st.write(st.session_state.expenses)

st.header('Visualization')
if st.button('Visualize Expenses'):
    visualize_expenses()

total_budget = st.number_input('Enter your total budget:', min_value=0.0, format="%.2f")
amount_spent = st.number_input('Enter the amount spent:', min_value=0.0, format="%.2f")

# Calculate the remaining budget
remaining_budget = total_budget - amount_spent

# Display the total budget, amount spent, and remaining budget
st.write(f'**Total Budget:** ${total_budget:.2f}')
st.write(f'**Amount Spent:** ${amount_spent:.2f}')
st.write(f'**Remaining Budget:** ${remaining_budget:.2f}')

# Provide a visual indicator for the remaining budget
if remaining_budget >= 0:
    st.success(f'You are within budget! ${remaining_budget:.2f} remaining.')
else:
    st.error(f'You have exceeded your budget by ${abs(remaining_budget):.2f}.')

# Optionally, add some additional information or advice
st.write('Keep track of your expenses to stay on top of your budget!')
