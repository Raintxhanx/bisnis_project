import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# --- BANNER ---
st.image("banner.png", use_column_width=True)  # Ganti dengan nama file banner brand Anda

# --- INPUT FILE DAN TOMBOL ---
st.markdown("## Upload File Penjualan")
col1, col2 = st.columns([4, 1])
with col1:
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
with col2:
    analyze = st.button("Analyze")

# --- SESSION STATE UNTUK MENYIMPAN STATUS ---
if 'analyze_clicked' not in st.session_state:
    st.session_state.analyze_clicked = False
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = None

if analyze and uploaded_file is not None:
    st.session_state.analyze_clicked = True

if st.session_state.analyze_clicked and uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)

    # --- PILIH BULAN ---
    if st.session_state.selected_month is None:
        st.session_state.selected_month = sorted(df['month'].unique())[0]
    st.markdown("### Penjualan Bulanan")
    selected = st.selectbox("Pilih Bulan", sorted(df['month'].unique()), index=sorted(df['month'].unique()).index(st.session_state.selected_month))
    st.session_state.selected_month = selected

    monthly_data = df[df['month'] == st.session_state.selected_month]

    # --- LINE PLOT: PENJUALAN HARIAN ---
    st.markdown("### Tren Penjualan Harian")
    daily_sales = monthly_data.groupby('date')['sales'].sum().reset_index()
    fig1 = px.line(daily_sales, x='date', y='sales', title="Penjualan Harian", markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    # --- BAR DAN PIE ---
    col3, col4 = st.columns(2)
    with col3:
        st.markdown("### Jumlah Penjualan per Kategori")
        cat_sales = monthly_data.groupby('category')['sales'].sum().reset_index()
        fig2 = px.bar(cat_sales, x='category', y='sales', title="Penjualan per Kategori")
        st.plotly_chart(fig2, use_container_width=True)

    with col4:
        st.markdown("### Komposisi Kategori Produk")
        fig3 = px.pie(cat_sales, names='category', values='sales', title="Komposisi Kategori")
        st.plotly_chart(fig3, use_container_width=True)

    # --- DISTRIBUSI USIA DAN KORELASI ---
    col5, col6 = st.columns(2)
    with col5:
        st.markdown("### Distribusi Usia Pelanggan")
        fig4 = px.histogram(df, x='age', nbins=15, title="Distribusi Usia", marginal="rug")
        st.plotly_chart(fig4, use_container_width=True)

    with col6:
        st.markdown("### Korelasi Usia dan Jumlah Pembelian")
        fig5 = px.scatter(df, x='age', y='sales', title="Korelasi Usia dan Penjualan", opacity=0.5)
        st.plotly_chart(fig5, use_container_width=True)

    # --- TABEL RATA-RATA PENJUALAN PER USIA ---
    st.markdown("### Rata-rata Penjualan per Usia")
    avg_sales_age = df.groupby('age')['sales'].mean().reset_index().sort_values(by='age')
    st.dataframe(avg_sales_age)

elif analyze:
    st.warning("Mohon upload file CSV terlebih dahulu.")
