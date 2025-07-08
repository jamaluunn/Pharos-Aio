# AIO Pharos Ecosystem Bot

Bot All-in-One (AIO) berbasis Python untuk mengotomatisasi berbagai tugas di testnet **Pharos Ecosystem**. Proyek ini menggabungkan beberapa skrip terpisah menjadi satu antarmuka yang modular, terstruktur, dan mudah digunakan.

Dibuat dan disusun oleh **Airdropversity ID**.

[![Telegram](https://img.shields.io/badge/Join%20Us-Telegram-blue.svg?logo=telegram)](https://t.me/AirdropversityID)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg?logo=python)](https://www.python.org/)

---

## 🚀 Pembaruan Terbaru (Juli 2025)

Update ini membawa perubahan besar yang bertujuan untuk membuat aktivitas bot terlihat lebih natural seperti manusia dan meningkatkan stabilitas secara keseluruhan.

* **Mode Loop Otomatis 24 Jam**: Bot kini bisa ditinggal berjalan sendiri dan akan otomatis mengulang semua tugas setiap 20-24 jam.
* **Randomisasi Aktivitas**: Mode otomatis (`Jalankan SEMUA Modul`) tidak lagi menggunakan parameter yang kaku. Jumlah transaksi dan nominalnya sekarang akan diambil secara acak dari rentang minimum-maksimum.
* **Stabilitas Swap Faroswap**: Modul Faroswap tidak lagi bergantung pada API eksternal. Semua proses swap dilakukan **langsung secara on-chain**, sehingga jauh lebih andal.
* **Logika Add Liquidity Baru**: Fitur Add Liquidity pada modul Faroswap telah diperbarui untuk menggunakan DVM (Dynamic Vending Machine) Pool, yang memerlukan konfigurasi `pools.json`.

---

## ✨ Fitur Utama

Bot ini terdiri dari 5 modul utama yang bisa dijalankan secara terpisah atau berurutan:

1.  **Pharos Module**
    * Daily Check-in & Klaim Faucet Poin.
    * Wrap & Unwrap PHRS.
    * **Zenith Swap** (WPHRS, USDC).
    * Menambah likuiditas di pool Zenith.
    * Mint Testnet Badge & verifikasi task "Send to Friends".

2.  **OpenFi Module**
    * Klaim Faucet untuk berbagai token (USDT, USDC, GOLD, dll).
    * Siklus lending penuh: Deposit, Supply, Borrow, dan Withdraw.

3.  **Gotchipus Module**
    * Mint NFT Gotchipus gratis (`freeMint`).
    * Klaim "Wearable" setelah minting.

4.  **Brokex Module**
    * Klaim Faucet USDT khusus untuk trading.
    * Melakukan trading (Long/Short) pada berbagai pair yang tersedia.

5.  **Faroswap Module**
    * Menggunakan sistem **multi-RPC** untuk koneksi yang lebih stabil.
    * Melakukan **Swap On-Chain** acak antar token (WPHRS, USDC, USDT).
    * Menambah **likuiditas DVM** untuk pair stablecoin.

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
git clone https://github.com/jamaluunn/Pharos-Aio.git
cd Pharos-Aio
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

### 5. Siapkan Pool Likuiditas (`pools.json`) - Wajib untuk Faroswap
Untuk menjalankan fitur **Add DVM Liquidity** pada modul Faroswap, Anda **WAJIB** membuat file `pools.json` dan mengisinya dengan alamat pool yang Anda buat sendiri.

#### Cara Membuat dan Mengisi `pools.json`:
1.  Buka Faroswap & pergi ke halaman "Pool".
2.  Pilih "Create Pool" > "PMM Pool" > "Standard".
3.  Pilih pasangan token **USDC/USDT**.
4.  Masukkan jumlah yang sama untuk keduanya (misal: 1 USDC dan 1 USDT).
5.  Klik "Create" dan konfirmasi transaksi.
6.  Setelah berhasil, cek menu "My Pools", lalu salin alamat pool tersebut.
7.  Ulangi langkah yang sama untuk pasangan **USDT/USDC**.
8.  Isi file `pools.json` dengan format berikut:
    ```json
    [
      {
        "USDC_USDT": "0x...Alamat_Pool_USDC_USDT_Anda...",
        "USDT_USDC": "0x...Alamat_Pool_USDT_USDC_Anda..."
      }
    ]
    ```

## 🚀 Cara Menjalankan Bot

Setelah semua pengaturan selesai, jalankan bot dengan perintah:
```bash
python main.py
```

### Mode Operasi
Bot akan memandu Anda untuk memilih mode operasi:

* **Mode Otomatis (Loop 20-24 jam)**: Pilihan terbaik untuk penggunaan jangka panjang. Bot akan langsung menjalankan semua modul secara acak, lalu tidur selama 20-24 jam, dan mengulang siklusnya secara otomatis tanpa henti. Cukup jalankan sekali dan biarkan.

* **Mode Manual**: Anda akan masuk ke menu utama di mana Anda bisa:
    * **Menjalankan siklus penuh** untuk satu modul spesifik.
    * **Menguji fitur individual** dari modul Pharos atau Faroswap melalui sub-menu.
    * **Menjalankan semua modul** sekali jalan (tanpa loop).

### Kustomisasi Pengaturan Acak
Untuk mengubah rentang randomisasi (jumlah swap, nominal, dll) pada mode otomatis, edit fungsi `get_*_settings_default()` di dalam file `main.py`.

**Contoh:**
```python
# main.py
def get_faroswap_settings_default():
    return {
        "delay": (15, 30), 
        "swap_count": (2, 4),  # Akan melakukan swap antara 2 hingga 4 kali
        "swap_amount": (0.001, 0.002), # Nominal swap acak
        "lp_count": (1, 2),      
        "lp_amount": (0.1, 0.15)
    }
```

## ⚠️ Peringatan (Disclaimer)
-   **GUNAKAN DENGAN RISIKO ANDA SENDIRI.** Bot ini berinteraksi langsung dengan smart contract menggunakan private key Anda.
-   **GUNAKAN HANYA WALLET TESTNET/BURNER.** Jangan pernah menggunakan private key dari wallet utama Anda yang berisi aset berharga.
-   Proyek ini dibuat untuk **tujuan edukasi** guna mempelajari interaksi on-chain dengan Python dan Web3.py.

## 🌟 Kredit
-   **Project by**: [Airdropversity ID](https://t.me/AirdropversityID)
-   **Original Scripts**: vonssy
