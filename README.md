cara Untuk setup frontend

# Frontend - Sentimen Media Analytic

Frontend aplikasi **Sentimen Media Analytic** yang dibangun menggunakan
framework **Laravel** untuk menampilkan hasil analisis sentimen media
dalam bentuk dashboard web interaktif.

---

## 📌 Deskripsi

Frontend ini berfungsi sebagai antarmuka pengguna (user interface) untuk:

- Menampilkan data hasil crawling berita
- Menyajikan visualisasi analisis sentimen
- Mengelola data pengguna
- Menyediakan dashboard monitoring opini publik

Frontend terhubung dengan backend berbasis Python melalui API.

---

## 🛠️ Teknologi yang Digunakan

- Laravel
- PHP 8+
- Tailwind CSS
- JavaScript
- Vite
- MySQL

---

## ✨ Fitur Utama

- Dashboard analisis sentimen
- Grafik dan statistik data
- Sistem autentikasi pengguna
- Manajemen data berita
- Tampilan responsif

---

## 📂 Struktur Folder

frontend-media-analytic-end/


├── app/ # Logic aplikasi

├── config/ # Konfigurasi

├── database/ # Migration & Seeder

├── public/ # Asset publik

├── resources/ # View & CSS

├── routes/ # Routing

└── tests/ # Testing

## Cara Setup Frontend
# Install Dependency
composer install
npm install

# Konfigurasi Environment
cp .env.example .env

# Generate Key
php artisan key:generate

# Migrasi Database
php artisan migrate

# Jalankan Server
php artisan serve
npm run dev









## Cara Untuk melakukan setup backendnya
# Change Directory
cd backend-media-analytic-end

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database.repository import init_db; init_db()"

# Run API server
python -m uvicorn src.api.app:app --reload

# Test API
curl http://localhost:8000/v1/articles
