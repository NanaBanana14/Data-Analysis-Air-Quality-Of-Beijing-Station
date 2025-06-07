import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import numpy as np
import folium
from streamlit_folium import st_folium

# === Setup Global ===
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
sns.set_theme(style='dark')
plt.rcParams["axes.spines.top"] = True
plt.rcParams["axes.spines.right"] = True

df = pd.read_csv("dashboard/main_data.csv", parse_dates=["datetime"])
df['month'] = df['datetime'].dt.month
df['year'] = df['datetime'].dt.year
df['date'] = df['datetime'].dt.date
df['day_of_week'] = df['datetime'].dt.dayofweek
df['day_type'] = df['day_of_week'].apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
df['hour'] = df['datetime'].dt.hour
df['time_period'] = df['hour'].apply(lambda h: 'Rush Hour' if (7 <= h <= 10 or 17 <= h <= 20) else 'Non Rush Hour')

winter_months = [12, 1, 2]
summer_months = [6, 7, 8]

df['season'] = df['month'].apply(
    lambda m: 'Winter' if m in winter_months else ('Summer' if m in summer_months else 'Other')
)

# === Sidebar ===
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("dashboard/logo/dashboard.png", width=200)

    st.markdown("## Filter Data")
    
    min_date = df['datetime'].min().date()
    max_date = df['datetime'].max().date()

    selected_date_range = st.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    selected_years = st.multiselect(
        "Pilih Tahun:",
        options=sorted(df['year'].unique()),
        default=sorted(df['year'].unique())
    )

    selected_stations = st.multiselect(
        "Pilih Stasiun:",
        options=sorted(df['station'].unique()),
        default=sorted(df['station'].unique())
    )

    selected_hour_range = st.slider(
        "Pilih Rentang Jam (24-jam):",
        min_value=0, max_value=23,
        value=(0, 23)
    )

    min_pm25 = float(df['PM2.5'].min())
    max_pm25 = float(df['PM2.5'].max())
    selected_pm25_range = st.slider(
        "Rentang PM2.5 (µg/m³):",
        min_value=min_pm25,
        max_value=max_pm25,
        value=(min_pm25, max_pm25)
    )

    selected_day_type = st.multiselect(
        "Tipe Hari:",
        options=df['day_type'].unique(),
        default=list(df['day_type'].unique())
    )

    selected_seasons = st.multiselect(
        "Musim:",
        options=df['season'].unique(),
        default=list(df['season'].unique())
    )

# === Filter Data ===
df = df[
    df['year'].isin(selected_years) &
    df['station'].isin(selected_stations) &
    (df['datetime'].dt.date >= selected_date_range[0]) &
    (df['datetime'].dt.date <= selected_date_range[1]) &
    (df['hour'] >= selected_hour_range[0]) &
    (df['hour'] <= selected_hour_range[1]) &
    (df['PM2.5'] >= selected_pm25_range[0]) &
    (df['PM2.5'] <= selected_pm25_range[1]) &
    df['day_type'].isin(selected_day_type) &
    df['season'].isin(selected_seasons)
]

st.title("Dashboard Kualitas Udara")
st.write("Analisis Data Kualitas Udara Beijing (2013–2017)")
st.markdown("---")

# === METRICS ===
col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_pm25 = df['PM2.5'].mean()
    st.metric("Rata-rata PM2.5", f"{avg_pm25:.2f} µg/m³")

with col2:
    avg_pm10 = df['PM10'].mean()
    st.metric("Rata-rata PM10", f"{avg_pm10:.2f} µg/m³")

with col3:
    total_stations = df['station'].nunique()
    st.metric("Jumlah Stasiun Terpilih", total_stations)

with col4:
    total_records = len(df)
    st.metric("Jumlah Data", total_records)

# --- Data PM2.5 harian ---
daily_pm25 = df.groupby('date')['PM2.5'].mean().reset_index()
cleanest_day = daily_pm25.loc[daily_pm25['PM2.5'].idxmin()]
dirtiest_day = daily_pm25.loc[daily_pm25['PM2.5'].idxmax()]

# --- Data suhu ekstrem ---
if 'TEMP' in df.columns:
    temp_low_threshold = df['TEMP'].quantile(0.05)
    temp_high_threshold = df['TEMP'].quantile(0.95)

    low_temp_days = df[df['TEMP'] <= temp_low_threshold]
    high_temp_days = df[df['TEMP'] >= temp_high_threshold]

    pm25_low_temp = low_temp_days['PM2.5'].mean()
    pm25_high_temp = high_temp_days['PM2.5'].mean()
else:
    temp_low_threshold = temp_high_threshold = pm25_low_temp = pm25_high_temp = None

col1, col2, col3, col4 = st.columns(4)

def styled_box(title, value, subtitle=None):
    """Kotak persegi dengan border merah, background transparan, dan teks putih"""
    st.markdown(f"""
        <div style="
            width: 200px;
            height: 200px;
            padding: 20px;
            border: 2px solid #b22222;
            border-radius: 10px;
            background-color: transparent;
            text-align: center;
            margin-bottom: 10px;
            color: white;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        ">
            <h4 style="margin-bottom: 10px; color: white;">{title}</h4>
            <p style="font-size: 22px; font-weight: bold; margin: 0; color: white;">{value}</p>
            <p style="margin: 0; color: white;">{subtitle if subtitle else ''}</p>
        </div>
    """, unsafe_allow_html=True)

with col1:
    styled_box(
        "Udara Paling Bersih",
        cleanest_day['date'].strftime('%Y-%m-%d'),
        f"PM2.5: {cleanest_day['PM2.5']:.2f} µg/m³"
    )

with col2:
    styled_box(
        "Udara Paling Kotor",
        dirtiest_day['date'].strftime('%Y-%m-%d'),
        f"PM2.5: {dirtiest_day['PM2.5']:.2f} µg/m³"
    )

with col3:
    if pm25_low_temp is not None:
        styled_box(
            f"PM2.5 Rata-rata Suhu Terendah ≤ {temp_low_threshold:.1f}°C",
            f"{pm25_low_temp:.2f} µg/m³"
        )
    else:
        styled_box("PM2.5 Rata-rata Suhu Terendah", "Data tidak tersedia")

with col4:
    if pm25_high_temp is not None:
        styled_box(
            f"PM2.5 Rata-rata Suhu Tertinggi ≥ {temp_high_threshold:.1f}°C",
            f"{pm25_high_temp:.2f} µg/m³"
        )
    else:
        styled_box("PM2.5 Rata-rata Suhu Tertinggi", "Data tidak tersedia")

st.markdown("---")

# Filter untuk tahun 2013 sampai 2017
df_2013_2017 = df[(df['year'] >= 2013) & (df['year'] <= 2017)].copy()

# Hitung rata-rata PM2.5 per bulan
monthly_pm25 = df_2013_2017.groupby('month')['PM2.5'].mean().reset_index()

month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

plt.figure(figsize=(10, 5))
sns.lineplot(data=monthly_pm25, x='month', y='PM2.5', marker='o', color='steelblue', linewidth=2)

plt.title('Tren Bulanan Rata-rata PM2.5 (2013–2017)', fontsize=14, weight='bold')
plt.xlabel('Bulan', fontsize=12)
plt.ylabel('Konsentrasi PM2.5 (µg/m³)', fontsize=12)
plt.xticks(ticks=range(1, 13), labels=month_labels)

plt.ylim(0, monthly_pm25['PM2.5'].max() * 1.1)

for idx, row in monthly_pm25.iterrows():
    plt.text(row['month'], row['PM2.5'] + (monthly_pm25['PM2.5'].max() * 0.03), 
             f"{row['PM2.5']:.1f}", ha='center', va='bottom', fontsize=9, color='black')

sns.despine(trim=True)
plt.grid(visible=True, which='major', axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()

# Tangkap figure sekarang dan tampilkan di Streamlit
fig1 = plt.gcf()
st.pyplot(fig1)

# === 3. Rata-rata PM2.5 dan PM10 per Stasiun ===
avg_pm_station = df.groupby('station')[['PM2.5', 'PM10']].mean().reset_index()
avg_pm_station = avg_pm_station.sort_values('PM2.5', ascending=False)

plt.figure(figsize=(10, 7))
bar_width = 0.4
indices = np.arange(len(avg_pm_station))
plt.barh(indices, avg_pm_station['PM2.5'], height=bar_width, color='royalblue', label='PM2.5')
plt.barh(indices + bar_width, avg_pm_station['PM10'], height=bar_width, color='tomato', alpha=0.7, label='PM10')

plt.yticks(indices + bar_width / 2, avg_pm_station['station'])
plt.xlabel('Konsentrasi Rata-rata (µg/m³)')
plt.ylabel('Nama Stasiun')
plt.title('Rata-rata PM2.5 dan PM10 di Setiap Stasiun (2013–2017)', fontsize=14, weight='bold')
plt.legend(title='Polutan')
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()

col1, col2 = st.columns(2)

with col1:
    # === 2. Korelasi Antar Polutan ===
    pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
    corr_matrix = df[pollutants].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap='coolwarm',
        fmt='.2f',
        vmin=-1, vmax=1,
        linewidths=0.5,
        square=True,
        cbar_kws={"shrink": 0.8, "label": "Koefisien Korelasi"}
    )

    plt.title('Eksplorasi Korelasi Antar Polutan Udara', fontsize=14, weight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(rotation=0, fontsize=11)

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()
    
with col2:
    # === 4. PM2.5: Hari Kerja vs Akhir Pekan ===
    pm25_daytype = df.groupby('day_type')['PM2.5'].mean().reset_index()
    plt.figure(figsize=(6, 5))
    sns.barplot(
        data=pm25_daytype,
        x='day_type',
        y='PM2.5',
        hue='day_type',
        palette=['steelblue', 'salmon'],
        edgecolor='black',
        dodge=False,
        legend=False
    )
    plt.title('Rata-rata Tingkat PM2.5 antara Weekday dan Weekend (2013–2017)', fontsize=14, weight='bold')
    plt.xlabel('Tipe Hari')
    plt.ylabel('Rata-rata Konsentrasi PM2.5 (µg/m³)')
    plt.ylim(0, pm25_daytype['PM2.5'].max() + 10)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    for index, row in pm25_daytype.iterrows():
        plt.text(index, row['PM2.5'] + 0.5, f"{row['PM2.5']:.2f}", ha='center', fontsize=11, color='black')

    plt.tight_layout()
    st.pyplot(plt.gcf())
    plt.clf()

# === 5. Distribusi PM2.5 dan PM10 Saat Jam Sibuk ===
plt.figure(figsize=(12, 6))

# Subplot PM2.5
plt.subplot(1, 2, 1)
sns.boxplot(
    data=df,
    x='time_period',
    y='PM2.5',
    hue='time_period',
    palette=['#4A90E2', '#4A90E2'],
    legend=False
)
plt.title('Distribusi PM2.5: Jam Sibuk vs Non Jam Sibuk', fontsize=14, weight='bold')
plt.xlabel('Periode Waktu', fontsize=12)
plt.ylabel('Konsentrasi PM2.5 (µg/m³)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.ylim(0, df['PM2.5'].max() + 10)

# Subplot PM10
plt.subplot(1, 2, 2)
sns.boxplot(
    data=df,
    x='time_period',
    y='PM10',
    hue='time_period',
    palette=['#D94F4F', '#D94F4F'],
    legend=False
)
plt.title('Distribusi PM10: Jam Sibuk vs Non Jam Sibuk', fontsize=14, weight='bold')
plt.xlabel('Periode Waktu', fontsize=12)
plt.ylabel('Konsentrasi PM10 (µg/m³)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.ylim(0, df['PM10'].max() + 10)

plt.tight_layout()

st.pyplot(plt.gcf())

st.markdown("### Peta Konsentrasi Rata-rata PM2.5 per Stasiun (2013–2017)")
st.markdown("""
Peta berikut menunjukkan rata-rata konsentrasi PM2.5 pada masing-masing stasiun pemantauan udara di Beijing.
Warna lingkaran merepresentasikan tingkat kualitas udara:
- 🟢 Hijau: Baik (≤ 35 µg/m³)
- 🟠 Oranye: Sedang (≤ 75 µg/m³)
- 🔴 Merah: Buruk (> 75 µg/m³)
""")

# Tambahkan kolom time_period
df['time_period'] = df['hour'].apply(lambda h: 'Rush Hour' if 7 <= h <= 10 or 17 <= h <= 20 else 'Non Rush Hour')

# Tambahkan koordinat lokasi stasiun
station_locations = pd.DataFrame({
    'station': [
        'Aotizhongxin', 'Changping', 'Dingling', 'Dongsi', 'Guanyuan',
        'Gucheng', 'Huairou', 'Nongzhanguan', 'Shunyi', 'Tiantan',
        'Wanliu', 'Wanshouxigong'
    ],
    'latitude': [
        39.9826, 40.2181, 40.2904, 39.9289, 39.9295,
        39.9145, 40.3749, 39.9375, 40.1270, 39.8731,
        39.9996, 39.8949
    ],
    'longitude': [
        116.3970, 116.2317, 116.2302, 116.4177, 116.3393,
        116.1853, 116.6371, 116.4708, 116.6545, 116.4123,
        116.2785, 116.3466
    ]
})

df = df.merge(station_locations, on='station', how='left')

# === Peta Interaktif Rata-rata PM2.5 ===
station_avg = df.groupby('station').agg({
    'PM2.5': 'mean',
    'latitude': 'first',
    'longitude': 'first'
}).reset_index()

map_beijing = folium.Map(location=[39.9, 116.4], zoom_start=10, tiles='CartoDB positron')

def pm25_color(pm25):
    if pm25 <= 35:
        return 'green'
    elif pm25 <= 75:
        return 'orange'
    else:
        return 'red'

for _, row in station_avg.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=8,
        popup=folium.Popup(
            f"<b>{row['station']}</b><br>Rata-rata PM2.5: {row['PM2.5']:.2f} µg/m³", max_width=250
        ),
        color=pm25_color(row['PM2.5']),
        fill=True,
        fill_color=pm25_color(row['PM2.5']),
        fill_opacity=0.7
    ).add_to(map_beijing)


from streamlit_folium import st_folium
st_folium(map_beijing, width=800, height=500)


# === Footer ===
st.markdown("---")
st.caption("Data: Beijing Air Quality (2013–2017)")
