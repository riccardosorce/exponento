import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
import plotly.express as px
import streamlit as st


data=pd.read_excel('SOBI_TRAVELS.xlsx')


data1 = st.sidebar.multiselect("Pick a Category", data["category"].unique())
if not data1:
    dff2 = data.copy()
else:
    dff2 = data[data["category"].isin(data1)]



fil_data = dff2[dff2["transactiontype"] == "Receipt"]



fil_data=fil_data[pd.to_numeric(fil_data['amount'], errors='coerce').notnull()]

fil_data["amount"] = fil_data["amount"].astype(float)


kmeans = KMeans(init="random",
                 n_clusters=3,
                 n_init=20,
                 max_iter=500,
                 random_state=42
                 )


d = {'col1': fil_data["amount"], 'col2': fil_data["quantity"]}
fd = pd.DataFrame(data=d)



z=fd[np.abs(stats.zscore(fd['col1']))<2]
z1=z[np.abs(stats.zscore(z['col2']))<2]

#z1=fd

kmeans.fit(z1)


cluster = kmeans.labels_

fd2 = {'Amount': z1['col1'], 'Quantity': z1['col2'], 'Cluster': cluster }
fd2 = pd.DataFrame(data=fd2)


col1, col2 = st.columns((2))

with col1:
    st.subheader("Clustering")
    fig = px.scatter(fd2, x="Amount", y="Quantity", color="Cluster")
    fig['layout'].update(title="Clustering for Amount and Quantity",
                        titlefont = dict(size=20), xaxis = dict(title = "Amount", titlefont = dict(size=19)),
                        yaxis =dict(title = "Quantity", titlefont = dict(size=19)))
    st.plotly_chart(fig, use_container_width=True)



amount = fil_data.groupby('theadd').sum('amount')
amount['iso_code'] = amount.index

mappa = px.choropleth(amount, locations="iso_code",
                    color= 'amount',
                    hover_name="iso_code",
                    color_continuous_scale=px.colors.sequential.Darkmint)





with col2:
    st.subheader("Geo Visualization")

    st.plotly_chart(mappa, use_container_wodth=True)