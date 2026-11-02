# 🏛️ STRIPS Tour Planner Kota Batu (AI Automated Itinerary Planning)

![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![AI Classical Planning](https://img.shields.io/badge/AI-STRIPS%20FOL-orange?style=flat)
![Architecture](https://img.shields.io/badge/Architecture-Fullstack%20AI%20App-brightgreen?style=flat)
![Unit Testing](https://img.shields.io/badge/Tests-7%2F7%20Passing-success?style=flat)
![Zero Dependency](https://img.shields.io/badge/Dependencies-Zero%20External-blue?style=flat)

Proyek Perencanaan Otomatis Rute & Jadwal Wisata Kota Batu (*Tour Guide Itinerary Planning*) berbasis algoritma **STRIPS (Stanford Research Institute Problem Solver)** dengan penalaran logika predikat orde pertama (*First-Order Logic*).

Sistem menyelesaikan masalah penjadwalan multi-kendala secara terpadu: **jendela waktu operasional wahana**, **batas anggaran uang saku**, **biaya tiket & parkir resmi**, **durasi perjalanan**, dan **jeda kebutuhan manusiawi (makan siang/malam)**.

---

## 👥 Identitas Pengembang (Kelompok 8)
- **Mutiara Putri Faradilla** (NIM: 240605110113)
- **Vanya Nyssa Maulida** (NIM: 240605110104)

**Mata Kuliah:** Artificial Intelligence (Kelas A)  
**Dosen Pengampu:** Hani Nurhayati, M.T.  
**Program Studi:** Teknik Informatika, UIN Maulana Malik Ibrahim Malang

---

## 🚀 Fitur Utama Sistem
1. **Core AI STRIPS FOL Engine:**
   - Representasi keadaan eksplisit (*Explicit State-Space Representation*): lokasi terkini, akumulator waktu, sisa anggaran, set destinasi terkunjungi, set kepemilikan tiket, status makan.
   - Model operator PAD formal: *Precondition*, *Action*, *Delete-List*, *Add-List*.
   - Aksi terintegrasi: `TRAVEL(A, B)`, `BUY_TICKET(D)`, `VISIT(D)`, `EAT(MEAL)`.
2. **Web GUI Wizard Mandiri (Modern UI/UX):**
   - Format single-file mandiri (`tour_planner_gui.html`).
   - Peta rute interaktif terintegrasi Leaflet dengan peta topografi satelit Esri ArcGIS.
   - Estimasi biaya transparan, validasi input budget anti-minus, dan kartu rekomendasi waktu luang.
   - Generator dokumen PDF e-voucher tiket resmi siap unduh/cetak.
3. **Backend REST API (`app.py`):**
   - Berjalan pada pustaka standar Python (`http.server`) tanpa instalasi dependensi luar.
   - Endpoint `POST /api/plan` untuk perencanaan otomatis terintegrasi.
   - Endpoint `GET /api/destinations` untuk katalog data pariwisata Batu.
4. **Automated Unit Testing (`test_strips.py`):**
   - 7/7 *formal test assertions* lulus 100% (integritas basis pengetahuan, simetri matriks jarak, penolakan transaksi saat saldo kurang, dan validasi prasyarat tiket).
5. **Interactive Google Colab Notebook (`STRIPS_Tour_Planner_Batu.ipynb`):**
   - Notebook *all-in-one* mandiri dengan formulir interaktif Colab.

---

## 📂 Struktur Direktori Repositori

```text
📁 STRIPS-Tour-Planner-Batu/
├── 📄 app.py                           # Backend REST API Server & Web Server
├── 📄 strips_planner.py                # Core Engine Logika Predikat & Planner STRIPS
├── 📄 test_strips.py                   # Formal Automated Unit Testing Suite (unittest)
├── 📄 tour_planner_gui.html            # Frontend Web GUI Wizard Interaktif (Zero-Dependency)
├── 📓 STRIPS_Tour_Planner_Batu.ipynb   # Interactive Google Colab All-in-One Notebook
├── 📊 dataset_wisata_batu.csv          # Basis Data Empiris 14 Lokasi Wisata Kota Batu
├── 📊 matriks_jarak_batu.csv           # Matriks Waktu Tempuh & Jarak Fisik Kota Batu
├── 📄 requirements.txt                 # Manifest Dependensi Proyek
├── 📄 .gitignore                       # Filter Repositori Git
└── 📄 README.md                        # Dokumentasi Repositori
```

---

## ⚡ Panduan Menjalankan Sistem

### 1. Menjalankan Web GUI Secara Langsung (Paling Praktis)
Cukup buka berkas `tour_planner_gui.html` langsung di peramban Google Chrome, Edge, atau Firefox (via protokol `file:///`). Tidak memerlukan server lokal.

### 2. Menjalankan Backend REST API Server
Jalankan server bawaan Python:
```bash
python app.py
```
Akses layanan di peramban:
- **Web App GUI:** [http://localhost:8000/gui](http://localhost:8000/gui)
- **API Katalog Wisata:** [http://localhost:8000/api/destinations](http://localhost:8000/api/destinations)

### 3. Menjalankan Automated Unit Tests
Jalankan pengujian unit formal:
```bash
python test_strips.py
```
*Hasil:*
```text
Ran 7 tests in 0.025s
OK
```

### 4. Menjalankan Google Colab
Buka berkas `STRIPS_Tour_Planner_Batu.ipynb` di [Google Colab](https://colab.research.google.com), lalu pilih menu **Runtime ➔ Run all**.

---

## 📊 Basis Pengetahuan Pariwisata Kota Batu
Basis data mencakup 14 titik lokasi strategis Kota Batu:
1. Jatim Park 2 (Batu Secret Zoo & Eco Green Park)
2. Museum Angkut & Pasar Apung
3. Jatim Park 3 (Dino Park & Millennial Glow)
4. Wisata Paralayang & Omah Kayu Gunung Banyak
5. Air Terjun Coban Rondo & Taman Labirin
6. Flora Wisata San Terra de Laponte
7. Taman Rekreasi Selecta
8. Agrowisata Petik Apel Kusuma
9. Coban Rais & Batu Flower Garden
10. Batu Night Spectacular (BNS)
11. Alun-Alun Kota Batu & Pos Ketan Legenda
12. Pusat Suvenir & Oleh-Oleh Istana Brawijaya
13. Stasiun Kota Malang (Kotabaru) - *Hub Kedatangan*
14. Pusat Hotel & Penginapan Kota Batu - *Sentra Akomodasi*
