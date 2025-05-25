
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from preprocessing import preprocess_faktur_data, preprocess_numerik
import numpy as np

st.set_page_config(page_title="Dashboard Apotek", layout="wide")
st.title("💊 Pharmacy Purchase Analysis Dashboard")

@st.cache_data
def load_data():
    df = pd.read_csv("Data_Pembelian_Obat.csv")
    df = preprocess_faktur_data(df)
    df = preprocess_numerik(df)
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
    df['Deadline'] = pd.to_datetime(df['Deadline'], errors='coerce')
    return df

df = load_data()

# Sidebar Menu
menu = st.sidebar.selectbox("Pilih Analisis", [
    "Analisis Supplier",
    "Umur Hutang",
    "Laporan Pengeluaran Bulanan",
    "Proporsi Tunai vs Hutang",
    "Transaksi Tidak Wajar",
    "Analisis Diskon & Pajak",
    "Tren Pembelian per Bulan"
])

# 1. Analisis Supplier
if menu == "Analisis Supplier":
    st.header("📦 Analisis Keuangan per Supplier")

    df['Umur Hutang'] = (df['Deadline'] - df['Tanggal']).dt.days
    grouped = df.groupby('Nama Supplier').agg({
        'Nilai Total': 'sum',
        'Umur Hutang': 'mean',
        'Diskon': 'mean',
        'Jumlah': 'count'
    }).rename(columns={
        'Nilai Total': 'Total Pembelian (Rp)',
        'Umur Hutang': 'Rata-rata Umur Hutang (hari)',
        'Diskon': 'Rata-rata Diskon (%)',
        'Jumlah': 'Jumlah Transaksi'
    }).sort_values(by='Total Pembelian (Rp)', ascending=False).round(2)

    st.subheader("📊 Tabel Ringkasan Supplier")
    # Format angka rupiah
   # Simpan salinan terformat hanya untuk tampilan tabel
    grouped_display = grouped.copy()
    grouped_display['Total Pembelian (Rp)'] = grouped_display['Total Pembelian (Rp)'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))

    st.dataframe(grouped_display, use_container_width=True)

    st.subheader("📈 Grafik Analisis Supplier")
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    # Grafik 1: Total Pembelian per Supplier
    grouped['Total Pembelian (Rp)'].sort_values().plot(kind='barh', color='skyblue', ax=axs[0, 0])
    axs[0, 0].set_title('Total Pembelian per Supplier (Rp)')
    axs[0, 0].set_xlabel('Total Pembelian (Rp)')

    # Grafik 2: Rata-rata Umur Hutang
    grouped['Rata-rata Umur Hutang (hari)'].sort_values().plot(kind='barh', color='salmon', ax=axs[0, 1])
    axs[0, 1].set_title('Rata-rata Umur Hutang (hari)')
    axs[0, 1].set_xlabel('Hari')

    # Grafik 3: Rata-rata Diskon
    grouped['Rata-rata Diskon (%)'].sort_values().plot(kind='barh', color='lightgreen', ax=axs[1, 0])
    axs[1, 0].set_title('Rata-rata Diskon (%)')
    axs[1, 0].set_xlabel('Persentase')

    # Grafik 4: Jumlah Transaksi
    grouped['Jumlah Transaksi'].sort_values().plot(kind='barh', color='gold', ax=axs[1, 1])
    axs[1, 1].set_title('Jumlah Transaksi per Supplier')
    axs[1, 1].set_xlabel('Jumlah Transaksi')

    plt.tight_layout()
    plt.suptitle('Analisis Kinerja Supplier', y=1.02, fontsize=18)
    st.pyplot(fig)


# 2. Umur Hutang
elif menu == "Umur Hutang":
    st.header("📅 Distribusi Umur Hutang (Hari)")
    df['Umur Hutang (hari)'] = (df['Deadline'] - df['Tanggal']).dt.days
    st.write(f"Rata-rata umur hutang: **{df['Umur Hutang (hari)'].mean():.2f} hari**")
    fig, ax = plt.subplots(figsize=(10, 4))
    df['Umur Hutang (hari)'].hist(bins=20, color='lightgreen', edgecolor='black', ax=ax)
    ax.set_title('Distribusi Umur Hutang')
    st.pyplot(fig)

# 3. Laporan Pengeluaran Bulanan
elif menu == "Laporan Pengeluaran Bulanan":
    st.header("📈 Laporan Pengeluaran Bulanan")
    df['Bulan'] = df['Tanggal'].dt.to_period('M')
    monthly = df.groupby('Bulan')['Total Transaksi'].sum().reset_index()
    monthly['Pertumbuhan (%)'] = monthly['Total Transaksi'].pct_change() * 100
    monthly['Total Transaksi (Rp)'] = monthly['Total Transaksi'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
    st.dataframe(monthly[['Bulan', 'Total Transaksi (Rp)', 'Pertumbuhan (%)']], use_container_width=True)

    fig, ax = plt.subplots(1, 2, figsize=(14, 5))
    ax[0].bar(monthly['Bulan'].astype(str), monthly['Total Transaksi'], color='skyblue')
    ax[0].set_title('Total Pembelian per Bulan')
    ax[1].plot(monthly['Bulan'].astype(str), monthly['Pertumbuhan (%)'], marker='o', color='green')
    ax[1].axhline(0, color='red', linestyle='--')
    ax[1].set_title('Pertumbuhan Pembelian (%)')
    st.pyplot(fig)

# 4. Proporsi Tunai vs Hutang
elif menu == "Proporsi Tunai vs Hutang":
    st.header("💰 Proporsi Jenis Pembayaran")
    df['Jenis Pembelian'] = df['Jenis Pembelian'].str.upper().str.strip()
    proporsi = df['Jenis Pembelian'].value_counts(normalize=True) * 100
    st.dataframe(proporsi.round(2))
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(proporsi, labels=proporsi.index, autopct='%1.1f%%', startangle=140,
           colors=['#66b3ff', '#ff9999'])
    ax.set_title('Proporsi Tunai vs Hutang')
    st.pyplot(fig)

# 5. Transaksi Tidak Wajar
elif menu == "Transaksi Tidak Wajar":
    st.header("🚨 Deteksi Transaksi Tidak Wajar")
    df[['Diskon', 'Jumlah', 'Pajak']] = df[['Diskon', 'Jumlah', 'Pajak']].fillna(0)
    df['Harga Setelah Diskon'] = df['Harga Beli'] * (1 - df['Diskon'] / 100)
    df['Harga Setelah Pajak'] = df['Harga Setelah Diskon'] * (1 + df['Pajak'] / 100)
    df['Nilai Total Hitung'] = df['Harga Setelah Pajak'] * df['Jumlah']
    df['Z-Score Harga'] = (df['Harga Beli'] - df['Harga Beli'].mean()) / df['Harga Beli'].std()
    anomali = df[
        (df['Z-Score Harga'] > 3) |
        (df['Diskon'] > 30) |
        (df['Pajak'] > 20) |
        (df['Nilai Total Hitung'] > df['Harga Beli'] * df['Jumlah'] * 1.5)
    ]

    anomali_fmt = anomali.copy()
    for col in ['Harga Beli', 'Nilai Total', 'Nilai Total Hitung']:
        anomali_fmt[col] = anomali_fmt[col].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))

    st.dataframe(anomali_fmt[['Tanggal', 'Nama Supplier', 'Nama Obat', 'Harga Beli', 'Diskon',
                            'Pajak', 'Jumlah', 'Nilai Total', 'Nilai Total Hitung', 'Z-Score Harga']], use_container_width=True)

# 6. Analisis Diskon & Pajak
elif menu == "Analisis Diskon & Pajak":
    st.header("📉 Pengaruh Diskon & Pajak terhadap Total Pembelian")
    df['Total Harga'] = df['Harga Beli'] * df['Jumlah']
    df['Potongan Diskon'] = df['Total Harga'] * (df['Diskon'] / 100)
    df['Harga Setelah Diskon'] = df['Total Harga'] - df['Potongan Diskon']
    df['Tambahan Pajak'] = df['Harga Setelah Diskon'] * (df['Pajak'] / 100)
    df['Total Setelah DiskonPajak (Hitung)'] = df['Harga Setelah Diskon'] + df['Tambahan Pajak']
    df['Selisih'] = df['Total Setelah DiskonPajak (Hitung)'] - df['Nilai Total']
    df_fmt = df.copy()
    for col in ['Harga Beli', 'Nilai Total', 'Total Setelah DiskonPajak (Hitung)', 'Selisih']:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))

    st.dataframe(df_fmt[['Nama Obat', 'Harga Beli', 'Jumlah', 'Diskon', 'Pajak', 'Nilai Total',
                        'Total Setelah DiskonPajak (Hitung)', 'Selisih']].head(), use_container_width=True)
    st.metric("Total Selisih", f"Rp {df['Selisih'].sum():,.2f}")
    st.metric("Rata-rata Selisih", f"Rp {df['Selisih'].mean():,.2f}")

# 7. Tren Pembelian per Bulan
elif menu == "Tren Pembelian per Bulan":
    st.header("📊 Tren Pembelian Obat per Bulan")
    df['Bulan'] = df['Tanggal'].dt.to_period('M').astype(str)
    tren = df.groupby('Bulan')['Total Transaksi'].sum().sort_index()
    tren_fmt = tren.reset_index()
    tren_fmt['Total Pembelian (Rp)'] = tren_fmt['Total Transaksi'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
    st.dataframe(tren_fmt[['Bulan', 'Total Pembelian (Rp)']], use_container_width=True)

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(tren.index, tren.values, marker='o', color='royalblue', linewidth=2)
    ax.set_title('Tren Pembelian Obat per Bulan')
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Total Pembelian (Rp)')
    ax.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    st.pyplot(fig)
