import streamlit as st
import plotly.express as px
import pandas as pd
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import warnings
import xlsxwriter 
import subprocess
import numpy as np
import openpyxl as op
import plotly.figure_factory as ff
import pyarrow as pa
import time
import datetime
from scipy import stats
import seaborn as sns
import matplotlib
import matplotlib_inline
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans


st.set_page_config(page_title="Exponento", layout="wide")
st.title("BUSINESS INTELLIGENCE")

def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.close()
    processed_data = output.getvalue()
    return processed_data

@st.cache_resource
def load_data():
    model=pd.read_excel('SOBI_TRAVELS.xlsx')
    return model

df=load_data()


startDate = df["date1"].min()
endDate = df["date1"].max()
col1, col2 = st.columns((2))
with col1:
    date1 = st.date_input("Start Date", startDate)

with col2:
    date2 = st.date_input("End date", endDate)

df = df[(df["date1"].dt.date >= date1) & (df["date1"].dt.date <= date2)].copy() 


##################################################################################################
#FILTRI A SINISTRA ################################################################################

st.sidebar.header("Choose your filter: ")

#lascio company per non incasinare

company = st.sidebar.multiselect("Pick Client name", df["thename"].unique())
if not company:
    df2 = df.copy()
else:
    df2 = df[df["thename"].isin(company)]

fromacc = st.sidebar.multiselect("From account", df2["fromaccount"].unique())
if not fromacc:
    df3 = df2.copy()
else:
    df3 = df2[df2["fromaccount"].isin(fromacc)]


toacc = st.sidebar.multiselect("To account", df3["toaccount"].unique())
if not toacc:
    df4 = df3.copy()
else:
    df4 = df3[df3["toaccount"].isin(toacc)]

transaction = st.sidebar.multiselect("Pick the transaction Type", df4["transactiontype"].unique())

#filter by intersection
if not company and not fromacc and not toacc and not transaction:
    filtered_df = df
elif not fromacc and not toacc and not transaction and company:
    filtered_df = df[df["thename"].isin(company)]
elif not company and not toacc and not transaction and fromacc:
    filtered_df = df[df["fromaccount"].isin(fromacc)]
elif not fromacc and not company and not transaction and toacc:
    filtered_df = df[df["toaccount"].isin(toacc)]
elif not toacc and not fromacc and not company and transaction:
    filtered_df = df[df["transactiontype"].isin(transaction)]
elif fromacc and toacc and company and not transaction:
    filtered_df = df3[df3["toaccount"].isin(toacc)& df3["fromaccount"].isin(fromacc) & df3["thename"].isin(company)]
elif fromacc and company and transaction and not toacc:
    filtered_df = df3[df3["fromaccount"].isin(fromacc) & df3["thename"].isin(company) & df3["transactiontype"].isin(transaction)]
elif fromacc and toacc and transaction and not company:
    filtered_df = df3[df3["fromaccount"].isin(fromacc) & df3["toaccount"].isin(toacc) & df3["transactiontype"].isin(transaction)]
elif company and toacc and transaction and not fromacc:
    filtered_df = df3[df3["transactiontype"].isin(transaction) & df3["thename"].isin(company) & df3["toaccount"].isin(toacc)]
elif fromacc and toacc and not transaction and not company:
    filtered_df = df2[df2["fromaccount"].isin(fromacc) & df2["toaccount"].isin(toacc)]
elif fromacc and transaction and not toacc and not company:
    filtered_df = df2[df2["fromaccount"].isin(fromacc) & df2["transactiontype"].isin(transaction)]
elif fromacc and company and not transaction and not toacc:
    filtered_df = df2[df2["fromaccount"].isin(fromacc) & df2["thename"].isin(company)]
elif company and transaction and not fromacc and not toacc:
    filtered_df = df2[df2["thename"].isin(company) & df2["transactiontype"].isin(transaction)]
elif company and toacc and not transaction and not fromacc:
    filtered_df = df2[df2["thename"].isin(company) & df2["toaccount"].isin(toacc)]
elif toacc and transaction and not fromacc and not company:
    filtered_df = df2[df2["transactiontype"].isin(transaction) & df2["toaccount"].isin(toacc)]
else:
    filtered_df= df4[df4["thename"].isin(company) & df4["fromaccount"].isin(fromacc) & df4["toaccount"].isin(toacc)& df4["transactiontype"].isin(transaction)]

#ffiltered_df2=filtered_df.fillna(0)
filtered_df2 = filtered_df#[~filtered_df['companyname'].isnull() & ~filtered_df['quantity'].isnull()]



company_df3 = filtered_df2.groupby(by = ["thename"], as_index = False)["quantity"].sum()
with col1:
    st.subheader("Total quantity  of transaction by Client")
    fig = px.pie(company_df3, values = "quantity", names = "thename", hole = 0.5)
    fig.update_traces(text = company_df3["thename"], textposition = "outside") 
    st.plotly_chart(fig, use_container_width = True)





#WE HAVE THE PROBLEM THAT AMOUNT IS AN OBJECT, BUT WE NEED A FLOAT64
companydf2=filtered_df2[pd.to_numeric(filtered_df['amount'], errors='coerce').notnull()]
#filtered_df["amount"] = pd.to_numeric(filtered_df["amount"])
companydf2["amount"] = companydf2["amount"].astype(float)
#print (companydf2.dtypes)

company_df27 = companydf2[companydf2["transactiontype"]=="Payment"]
#fil_data = fil_data[fil_data["transactiontype"] == "Receipt"]

company_df4 = company_df27.groupby(by = ["thename"], as_index = False)["amount"].sum()
company_df5= company_df4.sort_values(by=['amount'],ascending=True )

with col2:
    st.subheader("Total Payments by Client")
    #fig = px.bar(company_df5, x = "thename", y = "amount", text= ['R{:,.2f}'.format(x) for x in company_df3["quantity"]]) #, template = "seaborn"
    fig = px.bar(company_df5, x = "thename", y = "amount", text= ['R{:,.2f}'.format(x) for x in company_df5["amount"]]) #, template = "seaborn"
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_traces(marker_color='tomato', marker_line_color='tomato', marker_line_width=1.5, opacity=0.6)
    st.plotly_chart(fig, use_container_width = True, height = 200) 
    
    


#GRAPH FOR NUMBER TRANSACTION TYPE
my_list=['Receipt']

filtered_df["Receipt/payment"] = np.where(filtered_df.transactiontype.isin(my_list), 1, 0)
status_df = filtered_df.groupby(by = ["transactiontype"], as_index = False)
#st.subheader("Number Receipt/payment")


#fig = px.bar(filtered_df, x = "transactiontype")  #,template = "seaborn"
#fig.update_traces(marker_color='mediumpurple', marker_line_color='mediumpurple', marker_line_width=1.5, opacity=0.6)
#st.plotly_chart(fig, use_container_width = True, height = 200) 

#AGGIUNTA 23.11

company_df54 = companydf2[companydf2["transactiontype"]=="Receipt"]
#fil_data = fil_data[fil_data["transactiontype"] == "Receipt"]

company_df41 = company_df54.groupby(by = ["thename"], as_index = False)["amount"].sum()
company_df51= company_df41.sort_values(by=['amount'],ascending=False )

with col1:
    st.subheader("Total Receipt by Client")
    #fig = px.bar(company_df5, x = "thename", y = "amount", text= ['R{:,.2f}'.format(x) for x in company_df3["quantity"]]) #, template = "seaborn"
    fig = px.bar(company_df51, x = "thename", y = "amount", text= ['R{:,.2f}'.format(x) for x in company_df51["amount"]]) #, template = "seaborn"
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_traces(marker_color='skyblue', marker_line_color='skyblue', marker_line_width=1.5, opacity=0.6)
    st.plotly_chart(fig, use_container_width = True, height = 200) 


#AGGIUNTA category

category_df = company_df54.groupby(by = ["category"], as_index = False)["amount"].sum()
with col2:
    st.subheader("Total Receipt by Category")
    fig = px.pie(category_df, values = "amount", names = "category", hole = 0.5)
    #fig.update_traces(text = category_df["amount"], textposition = "outside") 
    st.plotly_chart(fig, use_container_width = True)





#AMOUNT BY RECEIPT/PAYMENT

filtered_df=companydf2
trpay_df = filtered_df.groupby(by = ["transactiontype"], as_index = False)["amount"].sum()
with col1:
    st.subheader("Total amount by receipt and payment")
    fig = px.bar(trpay_df, x = "transactiontype", y = "amount", text= ['R{:,.2f}'.format(x) for x in trpay_df["amount"]]) #,  template = "seaborn"
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_traces(marker_color='turquoise', marker_line_color='turquoise', marker_line_width=1.5, opacity=0.6)
    st.plotly_chart(fig, use_container_width = True, height = 200) 



consu_df = company_df54.groupby(by = ["postedby"], as_index = False)["amount"].sum()
consu_df = consu_df.sort_values(by=['amount'],ascending=False )
with col2:
    st.subheader("Total Receipt by Consultant")
    fig = px.bar(consu_df, x = "postedby", y = "amount", text= ['R{:,.2f}'.format(x) for x in consu_df["amount"]]) #,  template = "seaborn"
    fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_traces(marker_color='violet', marker_line_color='violet', marker_line_width=1.5, opacity=0.6)
    st.plotly_chart(fig, use_container_width = True, height = 200) 




    



###########TIME SERIES

#TIME SERIES ANALYSIS

#st.subheader("Time Series Analysis")
#filtered_df2 = filtered_df[~filtered_df['companyname'].isnull() & ~filtered_df['quantity'].isnull()]
filtered_df20= companydf2
filtered_df20["receivedamount"] = filtered_df20["amount"]
filtered_df20["payedamount"] = filtered_df20["amount"]
#df['c1'].loc[df['c1'] == 'Value'] = 10
filtered_df20.loc[filtered_df20['transactiontype'] == 'Payment', 'receivedamount'] = 0
filtered_df20["day"] = filtered_df["date1"].dt.to_period("M")





linechart = pd.DataFrame(filtered_df20.groupby(filtered_df20["date1"].dt.strftime("%m : %d :%y"))["receivedamount"].sum()).reset_index()
fig2 = px.line(linechart, x = "date1", y="receivedamount", labels = {"Retail":"Amount"}, height=500, width=1000, template = "gridon")
#figura = px.line(linechart, x = "date1", y="receivedamount", labels = {"Retail":"Amount"}, height=500, width=1000, template = "gridon")
#st.plotly_chart(fig2, use_container_wodth=True)





#df['c1'].loc[df['c1'] == 'Value'] = 10
filtered_df20.loc[filtered_df20['transactiontype'] == 'Receipt', 'payedamount'] = 0
#filtered_df2["day"] = filtered_df["date1"].dt.to_period("D")

linechart2 = pd.DataFrame(filtered_df20.groupby(filtered_df20["date1"].dt.strftime("%m : %d : %y"))["payedamount"].sum()).reset_index()
fig3 = px.line(linechart2, x = "date1", y="payedamount", labels = {"Retail":"Amount"}, height=500, width=1000, template = "gridon")
#st.plotly_chart(fig3, use_container_wodth=True)



#########################################################################
income=np.array(linechart["receivedamount"])
expenses=np.array(linechart2["payedamount"])
time=np.array(linechart2["date1"])

#frame= pd.DataFrame(income,expenses,time)

#fig27, ax = plt.subplots(figsize=(14,8))

# Plot lines
#ax.plot(time, income, color="green")
#ax.plot(time, expenses, color="red")

# Fill area when income > expenses with green
#ax.fill_between(
#    time, income, expenses, where=(income > expenses), 
#    interpolate=True, color="green", alpha=0.25, 
#    label="Payment"
#)

# Fill area when income <= expenses with red
#ax.fill_between(
#    time, income, expenses, where=(income <= expenses), 
#    interpolate=True, color="red", alpha=0.25,
#    label="Receipt"
#)

#ax.legend();
################################
#st.subheader("Time Series of compared income and expenses")
#st.plotly_chart(fig27, use_container_wodth=True)


#fig54 = px.line(frame, x = "time", y=frame.columns[1:2], labels = {"Retail":"Amount"}, height=500, width=1000, template = "gridon")
#st.plotly_chart(fig54, use_container_wodth=True)



values=np.cumsum(income)
values2=np.cumsum(expenses)

fig54, bx = plt.subplots(figsize=(14,8))

# Plot lines
#bx.plot(time, values, color="green")
#bx.plot(time, values2, color="red")



bx.plot(values, color="green")
bx.plot(values2, color="red")


bx.legend();
#########################
st.subheader("Time Series of cumulative income and expenses")
st.plotly_chart(fig54, use_container_wodth=True)




#with st.expander("View Data of TimeSeries", expanded=True):
#    st.write(linechart2.T.style.background_gradient(cmap="Blue"))
#    csv = linechart2.to_csv(index = True).encode('utf-8')
#    excel = to_excel(linechart2)
#    st.download_button("Download Data CSV", data =csv, file_name= "Time_series-payed.csv", mime = "text/cvs", help = "Click here to dowmload the data as CSV file")
#    st.download_button("Download Data XLSX", data =excel, file_name= "Time-series-payed.xlsx",  help = "Click here to dowmload the data as XLSX file")

#with st.expander("View Data of TimeSeries", expanded=True):
#    st.write(linechart.T.style.background_gradient(cmap="Blue"))
#    csv = linechart.to_csv(index = True).encode('utf-8')
#    excel = to_excel(linechart)
#    st.download_button("Download Data CSV", data =csv, file_name= "Time_series-received.csv", mime = "text/cvs", help = "Click here to dowmload the data as CSV file")
#    st.download_button("Download Data XLSX", data =excel, file_name= "Time-series-received.xlsx",  help = "Click here to dowmload the data as XLSX file")

