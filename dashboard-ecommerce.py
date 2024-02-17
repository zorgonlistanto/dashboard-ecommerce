# Import the library
import streamlit as st
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.io as pio
pio.renderers.default = "iframe"
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
import os
warnings.filterwarnings('ignore')

st.set_page_config(layout="wide")
config = {'responsive': False}

file_path1 = os.path.abspath("datatransaksi2023.csv")
file_path2 = os.path.abspath("datauser2023.csv")
file_path3 = os.path.abspath("dataproduk2023.csv")

# Prepare the dataset
df1 = pd.read_csv(file_path1, sep=';')
df2 = pd.read_csv(file_path2)
df3 = pd.read_csv(file_path3, sep=';')

# Data cleaning and preprocessing
df2['Status'] = df2['Status'].str.capitalize()
df3['PRODUCT_ID'] = df3['PRODUCT_ID'].str.upper()
df3 = df3.rename(columns={'PRODUCT_ID':'Product_ID'})
df1 = df1.dropna(subset=['Quantity'])
df1['Quantity'] = df1['Quantity'].astype(int)
# Menghitung total penjualan per produk
product_sales = df1.groupby('Product_ID')['Quantity'].sum().reset_index()
# Gabungkan data penjualan dengan data produk berdasarkan Product_ID
merges = pd.merge(product_sales, df3, on='Product_ID', how='left')
# Hitung total penjualan berdasarkan nilai total penjualan dan harga satuan produk
merges['Total_Sales'] = merges['Quantity'] * merges['HARGA_SATUAN']

# Streamlit app
st.header(' Dashboard Monitoring dan Analisis E-Commerce :sparkles:')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_customer = df2['User_ID'].count()
    st.metric("Total Customer", value=total_customer)

with col2:
    total_item = df1['Quantity'].sum()
    st.metric("Total Produk yang Terjual", value=total_item)

with col3:
    total_sales_sum = "Rp{:,.0f}".format(merges['Total_Sales'].sum())
    st.metric("Total Seluruh Penjualan", value=total_sales_sum)

with col4:
    basic_customers = df2[df2['Status'] == 'Basic']['User_ID'].nunique()
    st.metric("Jumlah Pelanggan Basic", value=basic_customers)


with col5:
    premium_customers = df2[df2['Status'] == 'Premium']['User_ID'].nunique()
    st.metric("Jumlah Pelanggan Premium", value=premium_customers)

# Visual 1
st.subheader('Produk yang Terjual')

col1, col2 = st.columns(2)

with col1:
	plt.subplots(figsize=(20, 10))
	# Konversi kolom 'Date' menjadi datetime
	df1['Date'] = pd.to_datetime(df1['Date'], format='%d/%m/%Y')
	# Tambah kolom baru 'Month'
	df1['Month'] = df1['Date'].dt.month_name()
	# Hitung total penjualan per bulan
	sales_per_product_month = df1.groupby(['Product_ID', 'Month'])['Quantity'].sum().reset_index()
	months_order = ['January', 'February', 'March', 'April']
	sales_per_product_month['Month'] = pd.Categorical(sales_per_product_month['Month'], categories=months_order, ordered=True)
	colors = ['rgb(31, 119, 180)', 'rgb(255, 127, 14)', 'rgb(44, 160, 44)', 'rgb(214, 39, 40)', 'rgb(148, 103, 189)']
	# Visualisasi
	fig1 = make_subplots(rows=1, cols=1, shared_xaxes=True, shared_yaxes=True)
	# Buat bar plot
	for i, product_id in enumerate(sales_per_product_month['Product_ID'].unique()):
	    sales_data = sales_per_product_month[sales_per_product_month['Product_ID'] == product_id]
	    fig1.add_trace(go.Bar(x=sales_data['Month'], y=sales_data['Quantity'], name=f'Product {product_id}', marker_color=colors[i]))
	# Tambahhkan garis tren
	for i, product_id in enumerate(sales_per_product_month['Product_ID'].unique()):
	    # Filter data penjualan untuk produk tertentu
	    sales_data = sales_per_product_month[sales_per_product_month['Product_ID'] == product_id]  
	    # Hitung jumlah produk yang terjual secara bulanan
	    monthly_quantity = sales_data.groupby('Month')['Quantity'].sum()   
	    x = np.arange(len(monthly_quantity))
	    y = monthly_quantity.values
	    z = np.polyfit(x, y, 1)
	    p = np.poly1d(z)    
	    fig1.add_trace(go.Scatter(
	        x=['January', 'February', 'March', 'April'],
	        y=p(x),
	        mode='lines',
	        line=dict(color='black', dash='dash'),
	        name=f'Trend - Product {product_id}',
	        showlegend=True
	    ))
	fig1.update_layout(
	    title='Jumlah Produk yang Terjual Bulanan',
	    xaxis_title='Bulan',
	    yaxis_title='Jumlah',
	    showlegend=True,
	    bargap=0.2,
	    xaxis={'categoryorder': 'array', 'categoryarray': months_order},
	    yaxis=dict(range=[0, 60]),
	    width=510)
	# Tambahkan dropdown
	buttons = [
	    {'label': 'Semua Produk', 'method': 'update', 'args': [{'visible': [True] * len(fig1.data)}]}
	]
	for product_id, color in zip(sales_per_product_month['Product_ID'].unique(), colors):
	    visible = [True if product_id == p_id else False for p_id in sales_per_product_month['Product_ID'].unique()]
	    buttons.append(
	        {'label': f'Produk {product_id}', 'method': 'update', 'args': [{'visible': visible}]}
	    )
	fig1.update_layout(
	    updatemenus=[
	        {'buttons': buttons,
	         'direction': 'down',
	         'pad': {'r': 10, 't': 10},
	         'showactive': True,
	         'x': 0.1,
	         'xanchor': 'left',
	         'y': 1.12,
	         'yanchor': 'top'}
	    ]
	)
	st.plotly_chart(fig1, config=config)

with col2:
	plt.subplots(figsize=(20, 10))
	# Ubah 'Date' menjadi datetime
	df1['Date'] = pd.to_datetime(df1['Date'])
	monthly_quantity = df1.groupby(df1['Date'].dt.strftime('%B'))['Quantity'].sum().reindex(['January', 'February', 'March', 'April'])
	# Buat bar plot
	max_quantity = max(monthly_quantity)
	colors2 = ['lightgrey'] * len(monthly_quantity)
	max_index = monthly_quantity[monthly_quantity == max_quantity].index[0]
	colors2[list(monthly_quantity.index).index(max_index)] = '#636EFA'

	fig2 = go.Figure()
	fig2.add_trace(go.Bar(
	    x=['Januari', 'Februari', 'Maret', 'April'],
	    y=monthly_quantity,
	    marker=dict(color=colors2),
	    showlegend=False
	))

	# Tambah garis tren
	x = np.arange(len(monthly_quantity))
	y = monthly_quantity.values
	z = np.polyfit(x, y, 1)
	p = np.poly1d(z)
	fig2.add_trace(go.Scatter(
	    x=['Januari', 'Februari', 'Maret', 'April'],
	    y=p(x),
	    mode='lines',
	    line=dict(color='red', dash='dash'),
	    name='Tren',
	    showlegend=False
	))

	fig2.update_layout(
	    title='Jumlah Semua Produk yang Terjual Bulanan',
	    xaxis=dict(title='Bulan'),
	    yaxis=dict(title='Jumlah'), width=510
	)
	st.plotly_chart(fig2, config=config)

# Visual 2
st.subheader('Distribusi Pelanggan')

col1, col2 = st.columns(2)

with col1:
	plt.subplots(figsize=(20, 10))
	# Buat histogram
	fig3 = go.Figure(data=[go.Histogram(x=df2['Age'])])
	fig3.update_layout(
	    title='Distribusi Usia Pelanggan',
	    xaxis=dict(title='Usia'),
	    yaxis=dict(title='Jumlah'), width=400)
	# Plot
	st.plotly_chart(fig3, config=config)

with col2:
	plt.subplots(figsize=(20, 10))
	# Gabungkan data yang diperlukan
	merged_data = pd.merge(df1, df2, on='User_ID', how='left')
	products = ['Semua Produk', 'A', 'B', 'C', 'D', 'E']
	dropdown_options = []
	for product in products:
	    dropdown_options.append({'label': f'Produk {product}', 'method': 'update', 'args': [{'visible': [product == p for p in products]}, {'title': f'Distribusi Pelanggan untuk Produk "{product}"'}]})
	# Buat fungsi pie chart untuk tiap produkk
	def generate_pie_chart(product):
	    data = []
	    for prod in products:
	        merged_data_product = merged_data if prod == 'Semua Produk' else merged_data[merged_data['Product_ID'] == prod]
	        premium_transactions_product = merged_data_product[merged_data_product['Status'] == 'Premium'].shape[0]
	        basic_transactions_product = merged_data_product[merged_data_product['Status'] == 'Basic'].shape[0]
	        labels = ['Premium', 'Basic']
	        values = [premium_transactions_product, basic_transactions_product]
	        trace = go.Pie(labels=labels, values=values, name=prod, visible=(product == prod))
	        data.append(trace)
	    fig4 = go.Figure(data=data)
	    fig4.update_layout(title=f'Distribusi Pelanggan untuk "{product}" ', showlegend=True, updatemenus=[{'buttons': dropdown_options,
	                                'direction': 'down',
	                                'showactive': True,
	                                'x': 0.1,
	                                'xanchor': 'left',
	                                'y': 1.1,
	                                'yanchor': 'top',
	                                'type': 'dropdown'}], width=400)

	    return fig4
	fig4 = generate_pie_chart('Semua Produk')
	st.plotly_chart(fig4, config=config)

#Visual 3
st.subheader('Kondisi dan Penjualan Produk')

col1, col2 = st.columns(2)

with col1:
	plt.subplots(figsize=(20, 10))
	# Menambahkan status Restock atau Terpenuhi Aman
	merges['Sisa'] = merges['JUMLAH_DIGUDANG'] - merges['Quantity']
	merges['Status'] = np.where(merges['JUMLAH_DIGUDANG'] - merges['Quantity'] < merges['HARUS_RESTOCK_BILA_JUMLAH_GUDANG_TERSISA'], 'Restock', 'Terpenuhi Aman')
	colors3 = {'Restock': 'red', 'Terpenuhi Aman': 'green'}

	fig5 = go.Figure()
	for index, row in merges.iterrows():
	    status = row['Status']
	    if status in ["Restock", "Terpenuhi Aman"]:
	        fig5.add_trace(go.Bar(
	            x=[row['Product_ID']],
	            y=[row['Sisa']],
	            name=status, 
	            marker=dict(color=colors3[status]),
	            showlegend=False
	        ))

	# Tambahkan legend manual
	legend_entries = [
	    dict(x=1, y=1, xref="paper", yref="paper", text="Restock", showarrow=False, bgcolor="red", font=dict(color="white")),
	    dict(x=1, y=0.95, xref="paper", yref="paper", text="Terpenuhi Aman", showarrow=False, bgcolor="green", font=dict(color="white"))
	]

	fig5.update_layout(
	    title='Kondisi Ketersediaan Produk',
	    xaxis=dict(title='Produk'),
	    yaxis=dict(title='Sisa'),
	    annotations=legend_entries, width=510
	)

	st.plotly_chart(fig5, config=config)

with col2:
	plt.subplots(figsize=(20, 10))
	max_sales = merges['Total_Sales'].max()
	min_sales = merges['Total_Sales'].min()

	colors4 = np.where((merges['Total_Sales'] == max_sales), 'green', 
	                  np.where((merges['Total_Sales'] == min_sales), 'red', 'lightgrey'))

	fig6 = go.Figure()

	fig6.add_trace(go.Bar(
	    x=merges['Product_ID'],
	    y=merges['Total_Sales'],
	    marker=dict(color=colors4),
	))

	fig6.update_layout(
	    title='Total Penjualan per Produk',
	    xaxis=dict(title='Produk'),
	    yaxis=dict(title='Total Penjualan'), width=510
	)

	st.plotly_chart(fig6, config=config)
