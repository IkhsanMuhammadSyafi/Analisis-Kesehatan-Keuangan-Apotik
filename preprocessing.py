
import pandas as pd

def preprocess_faktur_data(df):
    """Mengisi kembali kolom deskriptif faktur yang kosong dengan nilai sebelumnya."""
    kolom_faktur = ['Tanggal', 'No Faktur', 'Nama Supplier', 'Jenis Pembelian', 'Deadline']
    df[kolom_faktur] = df[kolom_faktur].ffill()
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], dayfirst=True, errors='coerce')
    df['Deadline'] = pd.to_datetime(df['Deadline'], dayfirst=True, errors='coerce')
    return df

def clean_numerik_koma_titik(val):
    """Membersihkan angka dari format ribuan (titik) dan koma desimal, jadi float bersih."""
    if pd.isna(val) or val == '':
        return None
    
    val = str(val).strip()
    
    # Remove currency symbols and percentage signs if any
    val = val.replace('Rp', '').replace(' ', '').replace('%', '')
    
    # Handle cases where both . and , are present (Indonesian format)
    if '.' in val and ',' in val:
        # Remove thousand separators (dots) and replace comma with decimal point
        val = val.replace('.', '').replace(',', '.')
    elif ',' in val:
        # If only comma exists, check if it's acting as decimal separator
        if val.endswith(',00'):
            val = val.replace(',00', '')  # Remove ,00 completely
        else:
            val = val.replace(',', '.')  # Replace other commas with decimal point
    
    try:
        # Convert to float (handles cases where val is now "18767" or "18767.50")
        return float(val) if val else None
    except:
        return None

def preprocess_numerik(df):
    """Membersihkan dan mengonversi kolom numerik agar bisa diproses Python."""
    kolom_angka_bulat = ['Jumlah']
    kolom_rupiah = ['Harga Beli', 'Nilai Total', 'Total Transaksi']
    kolom_persen = ['Diskon', 'Pajak']

    for kolom in kolom_angka_bulat:
        df[kolom] = df[kolom].apply(clean_numerik_koma_titik).fillna(0).astype('Int64')

    for kolom in kolom_rupiah:
        df[kolom] = df[kolom].apply(clean_numerik_koma_titik)

    for kolom in kolom_persen:
        df[kolom] = df[kolom].astype(str).str.replace('%', '').str.replace('.', '').str.replace(',', '.').astype(float)

    return df
