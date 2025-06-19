# AIO Pharos Ecosystem Bot

Bot All-in-One (AIO) berbasis Python untuk mengotomatisasi berbagai tugas di testnet **Pharos Ecosystem**. Proyek ini menggabungkan beberapa skrip terpisah menjadi satu antarmuka yang modular, terstruktur, dan mudah digunakan.

Dibuat dan disusun oleh **Airdropversity ID**.

[![Telegram](https://img.shields.io/badge/Join%20Us-Telegram-blue.svg?logo=telegram)](https://t.me/AirdropversityID)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg?logo=python)](https://www.python.org/)

---

## ✨ Fitur Utama

Bot ini terdiri dari 4 modul utama yang bisa dijalankan secara terpisah atau berurutan:

1.  **Pharos Module**
    * Daily Check-in & Klaim Faucet Poin.
    * Wrap & Unwrap PHRS.
    * Swap antar token (WPHRS, USDC, USDT).
    * Menambah likuiditas (Add Liquidity).

2.  **OpenFi Module**
    * Klaim Faucet untuk berbagai token (USDT, USDC, GOLD, TSLA, dll).
    * Deposit PHRS ke protokol lending.
    * Supply, Borrow, dan Withdraw aset di pasar lending.

3.  **Gotchipus Module**
    * Mint NFT Gotchipus gratis (`freeMint`).
    * Klaim "Wearable" setelah minting.

4.  **Brokex Module**
    * Klaim Faucet USDT khusus untuk trading.
    * Melakukan trading (Long/Short) pada berbagai pair yang tersedia.

## 📂 Struktur File

```
aio-pharos-bot/
├── main.py             # File utama untuk menjalankan bot
├── config.py           # Pusat konfigurasi (alamat kontrak, ABI, dll.)
├── requirements.txt    # Daftar pustaka (library) yang dibutuhkan
├── accounts.txt        # (Harus dibuat manual) Daftar private key Anda
├── proxy.txt           # (Opsional) Daftar proxy Anda
└── modules/
    ├── pharos_module.py
    ├── openfi_module.py
    ├── gotchipus_module.py
    └── brokex_module.py
```

## 🛠️ Instalasi & Pengaturan

Ikuti langkah-langkah berikut untuk menjalankan bot.

### 1. Clone Repositori
```bash
git clone [URL_GITHUB_ANDA]
cd aio-pharos-bot
```

### 2. Instal Dependensi
Sangat disarankan untuk menggunakan lingkungan virtual (virtual environment) Python.
```bash
# Buat venv (opsional tapi direkomendasikan)
python -m venv venv
source venv/bin/activate  # Di Windows: venv\Scripts\activate

# Instal semua library yang dibutuhkan
pip install -r requirements.txt
```

### 3. Siapkan Akun
Buat file baru bernama `accounts.txt` di dalam folder utama. Isi file ini dengan **private key** Anda, di mana **setiap key berada di baris baru**.
```
0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
0xcccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc
```

### 4. Siapkan Proxy (Opsional)
Jika Anda ingin menggunakan proxy, buat file baru bernama `proxy.txt`. Isi file ini dengan daftar proxy Anda, satu per baris.
Format yang didukung: `user:pass@ip:port` atau `ip:port`.
```
[http://user:password@1.2.3.4:8080](http://user:password@1.2.3.4:8080)
[http://1.2.3.5:8080](http://1.2.3.5:8080)
socks5://user:pass@1.2.3.6:9090
```

## 🚀 Cara Menjalankan Bot

Setelah semua pengaturan selesai, jalankan bot dengan perintah:
```bash
python main.py
```

Bot akan memandu Anda melalui beberapa pilihan awal:
1.  **Pilihan Proxy**: Bot akan bertanya apakah Anda ingin menggunakan proxy dari `proxy.txt`.
2.  **Menu Utama**: Anda akan disajikan menu utama untuk memilih modul yang ingin dijalankan.

### Mode Operasi
-   **Mode Manual (Pilihan 1-4)**: Jika Anda memilih satu modul spesifik, bot akan menanyakan pengaturan secara manual (jumlah nominal, berapa kali transaksi, dll.) sebelum berjalan.
-   **Mode Otomatis (Pilihan 5)**: Jika Anda memilih "Jalankan SEMUA Modul", bot akan menggunakan pengaturan default yang sudah ditentukan di dalam kode untuk berjalan secara otomatis dari awal sampai akhir.

## ⚠️ Peringatan (Disclaimer)
-   **GUNAKAN DENGAN RISIKO ANDA SENDIRI.** Bot ini berinteraksi langsung dengan smart contract menggunakan private key Anda.
-   **GUNAKAN HANYA WALLET TESTNET/BURNER.** Jangan pernah menggunakan private key dari wallet utama Anda yang berisi aset berharga.
-   Proyek ini dibuat untuk **tujuan edukasi** guna mempelajari interaksi on-chain dengan Python dan Web3.py.

## 🌟 Kredit
-   **Project by**: [Airdropversity ID](https://t.me/AirdropversityID)
-   **Original Scripts**: vonssy