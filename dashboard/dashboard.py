import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# === Setup Global ===
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
sns.set_theme(style='dark')
plt.rcParams["axes.spines.top"] = True
plt.rcParams["axes.spines.right"] = True

df = pd.read_csv("main_data.csv", parse_dates=["datetime"])
df['month'] = df['datetime'].dt.month
df['year'] = df['datetime'].dt.year
df['date'] = df['datetime'].dt.date
df['day_of_week'] = df['datetime'].dt.dayofweek
df['day_type'] = df['day_of_week'].apply(lambda x: 'Weekend' if x >= 5 else 'Weekday')
df['hour'] = df['datetime'].dt.hour
df['time_period'] = df['hour'].apply(lambda h: 'Rush Hour' if (7 <= h <= 10 or 17 <= h <= 20) else 'Non Rush Hour')

# === Sidebar ===
with st.sidebar:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("logo/dashboard.png", width=200)

    st.markdown("## Filter Data")
    
    # Rentang Tanggal
    min_date = df['datetime'].min().date()
    max_date = df['datetime'].max().date()

    selected_date_range = st.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Tahun
    selected_years = st.multiselect(
        "Pilih Tahun:",
        options=sorted(df['year'].unique()),
        default=sorted(df['year'].unique())
    )

    # Stasiun
    selected_stations = st.multiselect(
        "Pilih Stasiun:",
        options=sorted(df['station'].unique()),
        default=sorted(df['station'].unique())
    )

    # Rentang Jam
    selected_hour_range = st.slider(
        "Pilih Rentang Jam (24-jam):",
        min_value=0, max_value=23,
        value=(0, 23)
    )

    # PM2.5 Range
    min_pm25 = float(df['PM2.5'].min())
    max_pm25 = float(df['PM2.5'].max())
    selected_pm25_range = st.slider(
        "Rentang PM2.5 (µg/m³):",
        min_value=min_pm25,
        max_value=max_pm25,
        value=(min_pm25, max_pm25)
    )

    # Tipe Hari
    selected_day_type = st.multiselect(
        "Tipe Hari:",
        options=df['day_type'].unique(),
        default=list(df['day_type'].unique())
    )

    # Musim
    selected_seasons = st.multiselect(
        "Musim:",
        options=df['season'].unique(),
        default=list(df['season'].unique())
    )

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
            border: 2px solid red;
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
        "Hari Paling Bersih",
        cleanest_day['date'].strftime('%Y-%m-%d'),
        f"PM2.5: {cleanest_day['PM2.5']:.2f} µg/m³"
    )

with col2:
    styled_box(
        "Hari Paling Kotor",
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

# === 1. Tren Bulanan PM2.5 ===
monthly_pm25 = df.groupby('month')['PM2.5'].mean().reset_index()
month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des']

fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.lineplot(data=monthly_pm25, x='month', y='PM2.5', marker='o', ax=ax1, color='#90CAF9')
ax1.set_title('Rata-rata PM2.5 Bulanan', fontsize=16)
ax1.set_xlabel('Bulan')
ax1.set_ylabel('PM2.5 (µg/m³)')
ax1.set_xticks(range(1, 13))
ax1.set_xticklabels(month_labels)

# === 2. Korelasi Antar Polutan ===
pollutants = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
corr_matrix = df[pollutants].corr()

fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', vmin=-1, vmax=1,
            linewidths=0.5, square=True, cbar_kws={"shrink": .8}, ax=ax2)
ax2.set_title('Matriks Korelasi Polutan', fontsize=16)

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Tren Bulanan PM2.5")
    st.pyplot(fig1)

with col2:
    st.subheader("Korelasi Antar Polutan")
    st.pyplot(fig2)

# === 3. Rata-rata PM2.5 dan PM10 per Stasiun ===
avg_pm_station = df.groupby('station')[['PM2.5', 'PM10']].mean().reset_index()
avg_pm_station = avg_pm_station.sort_values('PM2.5', ascending=False)

fig3, ax3 = plt.subplots(figsize=(12, 8))
sns.barplot(data=avg_pm_station, x='PM2.5', y='station', color='#90CAF9', label='PM2.5', ax=ax3)
sns.barplot(data=avg_pm_station, x='PM10', y='station', color='lightcoral', alpha=0.5, label='PM10', ax=ax3)
ax3.set_title('Rata-rata PM2.5 dan PM10 per Stasiun', fontsize=16)
ax3.set_xlabel('Konsentrasi Rata-rata (µg/m³)')
ax3.set_ylabel('Stasiun')
ax3.legend()

# === 4. PM2.5: Hari Kerja vs Akhir Pekan ===
fig4, ax4 = plt.subplots(figsize=(6, 5))
pm25_daytype = df.groupby('day_type')['PM2.5'].mean().reset_index()
sns.barplot(data=pm25_daytype, x='day_type', y='PM2.5', palette=['#90CAF9', '#F48FB1'], ax=ax4)
ax4.set_title('Rata-rata PM2.5: Weekday vs Weekend', fontsize=16)
ax4.set_xlabel('Tipe Hari')
ax4.set_ylabel('PM2.5 (µg/m³)')

col3, col4 = st.columns([2, 2])
with col3:
    st.subheader("Rata-rata PM2.5 dan PM10 per Stasiun")
    st.pyplot(fig3)
with col4:
    st.subheader("PM2.5: Hari Kerja vs Akhir Pekan")
    st.pyplot(fig4)

# === 5. Distribusi PM2.5 dan PM10 Saat Jam Sibuk ===
st.subheader("Distribusi PM2.5 dan PM10: Jam Sibuk vs Non-Sibuk")
fig5, (ax5a, ax5b) = plt.subplots(1, 2, figsize=(12, 6))
sns.boxplot(data=df, x='time_period', y='PM2.5', palette='Blues', ax=ax5a)
ax5a.set_title('Distribusi PM2.5', fontsize=16)
ax5a.set_xlabel('Periode Waktu')
ax5a.set_ylabel('PM2.5 (µg/m³)')
sns.boxplot(data=df, x='time_period', y='PM10', palette='Oranges', ax=ax5b)
ax5b.set_title('Distribusi PM10', fontsize=16)
ax5b.set_xlabel('Periode Waktu')
ax5b.set_ylabel('PM10 (µg/m³)')
plt.tight_layout()

st.pyplot(fig5)

df['month'] = df['datetime'].dt.month
df['year'] = df['datetime'].dt.year
df['date'] = df['datetime'].dt.date
df['hour'] = df['datetime'].dt.hour

# Tentukan musim
winter_months = [12, 1, 2]
summer_months = [6, 7, 8]

df['season'] = df['month'].apply(
    lambda m: 'Winter' if m in winter_months else ('Summer' if m in summer_months else 'Other')
)

# --- Rata-rata PM2.5 per Musim ---
st.subheader("Rata-rata PM2.5 per Musim (2013-2017)")
seasonal_pm25 = df.groupby('season')['PM2.5'].mean().reset_index()

fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(data=seasonal_pm25, x='season', y='PM2.5', color='steelblue', ax=ax)
ax.set_ylabel('Rata-rata PM2.5 (µg/m³)')
ax.set_title('Rata-rata PM2.5 per Musim (2013-2017)')
st.pyplot(fig)

# --- PM2.5 maksimum tiap tahun ---
st.subheader("PM2.5 Maksimum per Tahun (2013-2017)")
max_pm25_per_year = df.groupby('year')['PM2.5'].max().reset_index()

fig, ax = plt.subplots(figsize=(6, 4))
sns.lineplot(data=max_pm25_per_year, x='year', y='PM2.5', marker='o', ax=ax)
ax.set_ylabel('PM2.5 Maksimum (µg/m³)')
ax.set_title('PM2.5 Maksimum per Tahun (2013-2017)')
st.pyplot(fig)

# --- Tren tahunan PM2.5 rata-rata ---
st.subheader("Tren Rata-rata PM2.5 Tahunan (2013-2017)")
annual_pm25 = df.groupby('year')['PM2.5'].mean().reset_index()

fig, ax = plt.subplots(figsize=(6, 4))
sns.lineplot(data=annual_pm25, x='year', y='PM2.5', marker='o', ax=ax)
ax.set_ylabel('Rata-rata PM2.5 (µg/m³)')
ax.set_title('Rata-rata PM2.5 Tahunan (2013-2017)')
st.pyplot(fig)

# === Footer ===
st.markdown("---")
st.caption("Data: Beijing Air Quality (2013–2017)")
