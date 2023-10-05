import streamlit as st
import pandas as pd
import streamlit as st
import altair as alt

st.title('Plano de Negócios para construção civil')



st.header('Dados do empreendimento')

cub_value = st.number_input('Valor do CUB', value=2300, step=100)
sale_cub_percentage = st.number_input('Porcentagem de venda do CUB', value=0.84)
lot_quantity = st.number_input('Quantidade de lotes', value=20, step=1)
lot_size = st.number_input('Tamanho dos lotes', value=1083, step=100)
    


st.header('Insira as informacoes da obra:')
total_area = st.number_input('Área total do terreno', value=lot_quantity*lot_size, step=100)
total_area_lots = st.number_input('Área total dos lotes', value=lot_quantity*lot_size, step=100)


st.header('Informações do projeto')
total_construction_cost = st.number_input('Custo total da construção', value=12_000_000, step=100_000)
lot_selling_price = st.number_input(
    'Preço de venda dos lotes', 
    value=cub_value*lot_size*sale_cub_percentage, 
    step=1000.0
)
total_project_revenue = st.number_input('Receita total do projeto', value=lot_selling_price*lot_quantity, step=100_000.0)

st.header('Informações do financiamento')
interest_rate = st.number_input('Taxa de juros (a.m)', value=0.01)
project_time_frame = st.slider('Tempo de obra (meses)', min_value=12, max_value=36, value=24, step=1)
disbursement_time_frame = st.slider(
    'Período em que os desembolsos ocorrerão', 
    min_value=1.0, 
    max_value=float(project_time_frame), 
    value=(1.0,project_time_frame/2),
    step=1.0
)
disbursement_delta = int(disbursement_time_frame[1] - disbursement_time_frame[0]) + 1
sales_time_frame = st.slider(
    'Período em que as vendas ocorrerão (meses)', 
    min_value=1.0, 
    max_value=float(project_time_frame), 
    value=(project_time_frame/4,project_time_frame/2),
    step=1.0
)
sales_delta = int(sales_time_frame[1] - sales_time_frame[0]) + 1

business_plan = pd.DataFrame({
    'period': [i for i in range(1, project_time_frame+1)],
    'cost': [
        0 if i < disbursement_time_frame[0] or i > disbursement_time_frame[1] else total_construction_cost/disbursement_delta for i in range(1, project_time_frame+1)],
    'sales': [0 if i < sales_time_frame[0] or i > sales_time_frame[1] else total_project_revenue/sales_delta for i in range(1, project_time_frame+1)],
})

def calculate_balance(row, previous_balance=0):
    # Get the values of 'sales' and 'costs' from the current row
    sales = row['sales']
    costs = row['cost']
    
    # Calculate the change in balance (sales - costs)
    balance_change = sales - costs
    
    # Calculate the new balance by adding the balance change to the previous balance
    new_balance = previous_balance + balance_change
    
    # Calculate the amount used to cover a negative balance
    amount_used = 0
    if new_balance < 0:
        amount_used = abs(new_balance)
        new_balance = 0
    
    return new_balance, amount_used

initial_balance = 0  # Set the initial balance here
business_plan['balance'] = initial_balance  # Initialize the balance column with the initial balance

for index, row in business_plan.iterrows():
    new_balance, amount_used = calculate_balance(row, previous_balance=initial_balance)
    business_plan.at[index, 'balance'] = new_balance
    business_plan.at[index, 'amount_used'] = amount_used
    initial_balance = new_balance

def format_currency(value):
    return 'R${:,.0f}'.format(value)




st.header('Resumo do empreendimento')

st.subheader(f'Desembolso Total: R${business_plan["amount_used"].sum()-1:,.2f}')
st.subheader(f'Receita Total: R${business_plan["sales"].sum()-1:,.2f}')
st.subheader(f'ROI: {total_project_revenue/business_plan["amount_used"].sum()-1:.2%}')

df=pd.DataFrame({
    'value': [total_construction_cost, total_project_revenue, business_plan["amount_used"].sum()], 
    'label': ['Custo total', 'Receita total', 'Desembolso Total']
})
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('label', axis=alt.Axis(labelAngle=0)),
    y='value'
)
st.altair_chart(chart, use_container_width=True)

for col in ['cost', 'sales', 'balance', 'amount_used']:
    business_plan[col] = business_plan[col].apply(format_currency)


st.table(business_plan)