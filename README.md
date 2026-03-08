# SPG Performance Evaluator API 🚀

API *backend* yang dirancang untuk mengevaluasi kinerja Sales Promotion Girl (SPG) secara otomatis berdasarkan transkrip percakapan mereka dengan pelanggan. Proyek ini menggunakan arsitektur **FastAPI** dan **Supabase**, serta ditenagai oleh *Custom Rule-Based NLP Engine* untuk melakukan ekstraksi informasi, penilaian (*scoring*), dan pemberian alasan (*reasoning*) secara *real-time*.

## ✨ Fitur Utama
* **Custom NLP Evaluator:** Menilai transkrip percakapan berdasarkan 5 metrik utama (Salam, Perkenalan, Detail Produk, *Cross-selling*, dan Penutup) tanpa bergantung pada *Large Language Model* eksternal.
* **Profanity Filter:** Deteksi dan penalti otomatis untuk penggunaan kata-kata tidak pantas/kasar.
* **Role-Based Access Control (RBAC):** Hierarki akses yang aman untuk `spg`, `admin` (Supervisor), dan `superadmin`.
* **Task & Recording Management:** Mengelola penugasan harian SPG dan menyimpan riwayat rekaman/transkrip beserta detail nilai NLP-nya.
* **Soft Deletes:** Fitur penghapusan data secara aman untuk menjaga integritas riwayat dan audit.
* **Bearer Token Authentication:** Seluruh rute dilindungi dengan otentikasi JWT yang terintegrasi penuh dengan Supabase Auth.

## 🛠️ Tech Stack
* **Programming Language:** Python 3.9+
* **Web Framework:** FastAPI
* **Database & Auth:** Supabase (PostgreSQL)
* **Data Validation:** Pydantic

## 📂 Struktur Direktori
```text
/project_folder
├── routers/            # Endpoint API terpisah berdasarkan entitas
│   ├── auth.py         # Login
│   ├── users.py        # CRUD Users (RBAC & Soft Delete)
│   ├── tasks.py        # CRUD Tasks
│   └── recordings.py   # Submit transkrip & Auto-NLP
├── .env                # Environment variable (Supabase config)
├── database.py         # Inisialisasi Supabase client
├── dependencies.py     # Middleware otorisasi (verify_token, verify_admin, dll)
├── nlp_engine.py       # Logika Rule-Based NLP & Sistem Skoring
├── schemas.py          # Pydantic models untuk request body
└── main.py             # Entry point utama aplikasi
```

## 🚀 Instalasi & Persiapan
1. Clone repositori ini:
```bash
git clone <repo-url>
cd <repo-folder>
```
2. Instal dependensi:
```bash
pip install fastapi uvicorn pydantic supabase python-dotenv
```
3. Konfigurasi Environment:
Buat file .env di root direktori dan masukkan kredensial Supabase Anda:
```
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_KEY=<your-anon-or-service-role-key>
```
4. Jalankan Server API:
```bash
uvicorn main:app --reload
```
API akan berjalan di http://127.0.0.1:8000. Buka http://127.0.0.1:8000/docs untuk melihat dokumentasi interaktif (Swagger UI).

---

`Author:` Dhiaulhaq Muhammad Naufal