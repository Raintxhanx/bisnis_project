import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import requests
import json
import os
from dotenv import load_dotenv


# Load file .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
url = "https://api.openai.com/v1/chat/completions"

def promp_gpt():
        
    # Konversi pivot ke JSON string (Heatmap)
    pivot_json = pivot.reset_index().to_json(orient="records")

    # Konversi tabel kategori penjualan ke JSON string (Bar & Pie)
    cat_sales_json = cat_sales.to_json(orient="records")

    # Konversi rata-rata penjualan per usia ke JSON string
    avg_sales_age_json = avg_sales_age.to_json(orient="records")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Anda adalah analis bisnis. "
                    "Di bawah ini ada data-data penjualan yang sudah difilter berdasarkan bulan. "
                    "Analisislah data ini dengan cermat."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Bulan yang dianalisis: {selected}\n\n"
                    "Berikut insight ringkas:\n"
                    f"{string_1}\n{string_2}\n{string_3}\n\n"
                    "Data penjualan per kategori:\n"
                    f"{daily_sales}\n\n"
                    "Data penjualan per hari:\n"
                    f"{cat_sales_json}\n\n"
                    "Rata-rata penjualan per usia:\n"
                    f"{avg_sales_age_json}\n\n"
                    "Heatmap Kategori x Usia:\n"
                    f"{pivot_json}\n\n"
                    "Tolong analisis:\n"
                    "Tolong anda analisis dengan data di atas, bagaimana prospek penjualan bisnis saya dalam sebulan, apakah ada tren atau pola tertentu yang terlihat"
                    "kategori produk apa yang harus saya prioritaskan, tren atau pola tersebut populer di kalangan usia berapa, target pemasaran seperti apa yang harus saya siapkan untuk produksi iklan"
                )
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

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

    # --- HEATMAP: KATEGORI X USIA (versi rapih & kustom) ---
    st.markdown("### Heatmap Penjualan per Kategori dan Usia")

    pivot = monthly_data.pivot_table(index='age', columns='category', values='sales', aggfunc='sum', fill_value=0)

    fig6 = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale=[
                [0, "black"],   # Nilai minimum = hitam
                [1, "red"]      # Nilai maksimum = merah
            ],
            hovertemplate="Kategori: %{x}<br>Usia: %{y}<br>Jumlah Terjual: %{z}<extra></extra>",
            colorbar=dict(title="Jumlah Terjual")
        )
    )

    fig6.update_layout(
        title="Heatmap Penjualan: Kategori vs Usia",
        xaxis_title="Kategori",
        yaxis_title="Usia",
        autosize=True,
        width=800,   # Lebih lebar
        height=600,  # Lebih tinggi
    )

    st.plotly_chart(fig6, use_container_width=True)

    # Cari (usia, kategori) dengan penjualan tertinggi
    max_value = pivot.values.max()
    max_idx = np.unravel_index(pivot.values.argmax(), pivot.shape)
    max_age = pivot.index[max_idx[0]]
    max_category = pivot.columns[max_idx[1]]

    st.info(f"💡 Penjualan tertinggi ada pada usia **{max_age}** untuk kategori **{max_category}**, dengan jumlah: **{max_value}**.")
    string_1 = f"💡 Penjualan tertinggi ada pada usia **{max_age}** untuk kategori **{max_category}**, dengan jumlah: **{max_value}**."

    # Kategori dengan total penjualan tertinggi di semua usia
    total_per_category = pivot.sum(axis=0)
    top_category = total_per_category.idxmax()
    st.info(f"🏆 Kategori dengan penjualan tertinggi di semua usia: **{top_category}** ({total_per_category.max()}).")
    string_2 = f"🏆 Kategori dengan penjualan tertinggi di semua usia: **{top_category}** ({total_per_category.max()})."

    # Usia dengan total penjualan tertinggi di semua kategori
    total_per_age = pivot.sum(axis=1)
    top_age = total_per_age.idxmax()
    st.info(f"👥 Usia dengan penjualan tertinggi di semua kategori: **{top_age}** ({total_per_age.max()}).")
    string_3 = "👥 Usia dengan penjualan tertinggi di semua kategori: **{top_age}** ({total_per_age.max()})."

    with st.spinner("Menunggu respon dari GPT..."):
        result = promp_gpt()
        answer = result["choices"][0]["message"]["content"]
        st.success("Berikut hasil analisis dari GPT:")
        st.write(answer)

elif analyze:
    st.warning("Mohon upload file CSV terlebih dahulu.")