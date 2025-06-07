# Beijing Air Quality Dashboard

Dashboard interaktif yang dikembangkan menggunakan **Streamlit** untuk menganalisis kualitas udara di Beijing dari tahun **2013 hingga 2017**.

Visualisasi data dikembangkan untuk menjawab beberapa pertanyaan bisnis yang relevan terhadap pemantauan kualitas udara.

---

## Pertanyaan Bisnis

1. **Apa tren bulanan polusi PM2.5 sepanjang tahun, dan apakah polusi lebih tinggi di bulan-bulan tertentu?**  
2. **Bagaimana korelasi antar berbagai polutan (PM2.5, PM10, SO2, NO2, CO, O3)?**  
3. **Bagaimana rata-rata tingkat PM2.5 dan PM10 di setiap stasiun dari 2013–2017?**  
4. **Apakah terdapat perbedaan signifikan tingkat polusi PM2.5 antara hari kerja dan akhir pekan selama 2013–2017?**  
5. **Bagaimana distribusi level PM2.5 dan PM10 selama jam sibuk (07:00–10:00 dan 17:00–20:00) dibandingkan dengan jam lainnya?**

---

## Struktur Direktori

```

submission
├───dashboard
│   ├───logo                   # logo
│   │   ├───dashboard.png
│   ├───main\_data.csv          # Dataset hasil preprocessing
│   └───dashboard.py           # Streamlit app
├───data
│   ├───data\_1.csv             # Raw data bagian 1
│   ├───data\_2.csv             # Raw data bagian 2
│   └───combined\_data.csv      # Gabungan data\_1 dan data\_2 (sebelum cleaning)
├───notebook.ipynb             # Notebook EDA dan preprocessing
├───README.md                  # File ini
├───requirements.txt           # Dependensi proyek
└───url.txt                    # URL visualisasi

````

---

## Teknologi & Library

- Python 3.12.0
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)
- [Folium](https://python-visualization.github.io/folium/)
- [Streamlit](https://streamlit.io/)
- [streamlit-folium](https://github.com/randyzwitch/streamlit-folium)

---

## Menjalankan Aplikasi

### 1. Clone Repository
```bash
git clone https://github.com/username/repo-name.git
cd submission/dashboard
````

### 2. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 3. Jalankan Streamlit

```bash
streamlit run dashboard.py
```

---

## Catatan

* Data yang digunakan merupakan gabungan dan pembersihan dari **data\_1.csv** dan **data\_2.csv**.
* `main_data.csv` adalah dataset yang telah diproses untuk kebutuhan visualisasi di dashboard.