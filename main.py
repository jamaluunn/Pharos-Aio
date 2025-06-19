# main.py

import asyncio
import random
from colorama import init, Fore, Style
from eth_account import Account

# Impor semua modul yang sudah kita buat
from modules.pharos_module import PharosModule
from modules.openfi_module import OpenFiModule
from modules.gotchipus_module import GotchipusModule
from modules.brokex_module import BrokexModule
import config

# Inisialisasi Colorama
init(autoreset=True)

# <<< FUNGSI BARU UNTUK FORMAT WAKTU >>>
def format_seconds_to_hms(seconds):
    """Mengubah detik menjadi format Jam:Menit:Detik"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def display_main_menu():
    """Menampilkan menu utama bot."""
    print(Fore.CYAN + Style.BRIGHT + "\n==============================================")
    print(Fore.CYAN + Style.BRIGHT + "==         AIO PHAROS ECOSYSTEM BOT         ==")
    print(Fore.CYAN + Style.BRIGHT + "==============================================")
    print(Fore.WHITE + Style.BRIGHT + "           by Airdropversity ID")
    print(Fore.BLUE + Style.BRIGHT +   "       https://t.me/AirdropversityID")
    print(Fore.YELLOW + "        Original Script by: vonssy")
    print(Fore.CYAN + Style.BRIGHT + "==============================================")
    
    print(Fore.GREEN + "\nPilih Modul yang ingin dijalankan (akan diulang setiap 24 jam):")
    print(Fore.WHITE + "1. Pharos (Swap & LP)")
    print(Fore.WHITE + "2. OpenFi (Lending)")
    print(Fore.WHITE + "3. Gotchipus (NFT Mint)")
    print(Fore.WHITE + "4. Brokex (Trading)")
    print(Fore.CYAN + "----------------------------------------------")
    print(Fore.YELLOW + Style.BRIGHT + "5. Jalankan SEMUA Modul (Menggunakan Pengaturan Default)")
    print(Fore.CYAN + "----------------------------------------------")
    print(Fore.RED + "0. Keluar (Tidak menjalankan bot)")
    print(Style.BRIGHT + "==============================================")

def get_proxy_settings():
    """Meminta pengguna apakah ingin menggunakan proxy."""
    print(Fore.CYAN + "\n--- Pengaturan Proxy ---")
    while True:
        use_proxy_input = input(Fore.YELLOW + "Apakah Anda ingin menggunakan proxy dari proxy.txt? (y/n): " + Style.RESET_ALL).lower()
        if use_proxy_input in ['y', 'n']:
            return use_proxy_input == 'y'
        print(Fore.RED + "Input tidak valid, masukkan 'y' atau 'n'.")

def get_user_input(prompt, input_type=float, min_val=0):
    while True:
        try:
            value = input_type(input(Fore.YELLOW + prompt + Style.RESET_ALL))
            if value >= min_val:
                return value
            else:
                print(Fore.RED + f"Nilai harus lebih besar atau sama dengan {min_val}.")
        except ValueError:
            print(Fore.RED + f"Input tidak valid. Harap masukkan angka ({input_type.__name__}).")

# --- FUNGSI PENGATURAN (DEFAULT & INTERAKTIF) ---
# (Tidak ada perubahan pada semua fungsi get_..._settings di bawah ini)
def get_pharos_settings_default():
    return {"delay": (10, 20), "wrap_amount": 0.01, "swap_count": 3, "swap_wphrs_usdc_amount": 0.005, "swap_usdc_wphrs_amount": 0.1, "lp_count": 3, "lp_amount_wphrs": 0.002, "lp_amount_usdc": 0.1}
def get_openfi_settings_default():
    return {"delay": (15, 30), "deposit_amount": 0.01, "supply_amount": 1.5, "borrow_amount": 0.5, "withdraw_amount": 0.2}
def get_gotchipus_settings_default():
    return {"delay": (10, 25)}
def get_brokex_settings_default():
    return {"delay": (20, 40), "trade_count": 3, "trade_amount": 1.0}
def get_pharos_settings_interactive():
    print(Fore.CYAN + "\n--- Pengaturan Manual Modul Pharos ---")
    settings = {}
    settings['wrap_amount'] = get_user_input("Jumlah PHRS untuk di-wrap (cth: 0.01): ", float)
    settings['swap_count'] = get_user_input("Berapa kali siklus swap (WPHRS->USDC->WPHRS)?: ", int)
    if settings['swap_count'] > 0:
        settings['swap_wphrs_usdc_amount'] = get_user_input("  Jumlah WPHRS -> USDC (cth: 0.005): ", float)
        settings['swap_usdc_wphrs_amount'] = get_user_input("  Jumlah USDC -> WPHRS (cth: 0.1): ", float)
    settings['lp_count'] = get_user_input("Berapa kali ingin Add Liquidity?: ", int)
    if settings['lp_count'] > 0:
        settings['lp_amount_wphrs'] = get_user_input("  Jumlah WPHRS untuk Add LP (cth: 0.002): ", float)
        settings['lp_amount_usdc'] = get_user_input("  Jumlah USDC untuk Add LP (cth: 0.1): ", float)
    min_delay = get_user_input("Jeda waktu minimum antar transaksi (detik): ", int)
    max_delay = get_user_input("Jeda waktu maksimum antar transaksi (detik): ", int, min_val=min_delay)
    settings['delay'] = (min_delay, max_delay)
    return settings
def get_openfi_settings_interactive():
    print(Fore.CYAN + "\n--- Pengaturan Manual Modul OpenFi ---")
    settings = {}
    settings['deposit_amount'] = get_user_input("Jumlah PHRS untuk di-deposit (cth: 0.01): ", float)
    settings['supply_amount'] = get_user_input("Jumlah setiap token untuk di-supply (cth: 1.5): ", float)
    settings['borrow_amount'] = get_user_input("Jumlah setiap token untuk di-borrow (cth: 0.5): ", float)
    settings['withdraw_amount'] = get_user_input("Jumlah setiap token untuk di-withdraw (cth: 0.2): ", float)
    min_delay = get_user_input("Jeda waktu minimum antar transaksi (detik): ", int)
    max_delay = get_user_input("Jeda waktu maksimum antar transaksi (detik): ", int, min_val=min_delay)
    settings['delay'] = (min_delay, max_delay)
    return settings
def get_gotchipus_settings_interactive():
    print(Fore.CYAN + "\n--- Pengaturan Manual Modul Gotchipus ---")
    min_delay = get_user_input("Jeda waktu antara Mint dan Claim (detik): ", int)
    max_delay = get_user_input("Jeda waktu maksimum (detik): ", int, min_val=min_delay)
    return {"delay": (min_delay, max_delay)}
def get_brokex_settings_interactive():
    print(Fore.CYAN + "\n--- Pengaturan Manual Modul Brokex ---")
    settings = {}
    settings['trade_count'] = get_user_input("Berapa kali ingin melakukan trade per akun?: ", int)
    if settings['trade_count'] > 0:
        settings['trade_amount'] = get_user_input("  Jumlah USDT per trade (cth: 1.0): ", float)
    min_delay = get_user_input("Jeda waktu minimum antar trade (detik): ", int)
    max_delay = get_user_input("Jeda waktu maksimum antar trade (detik): ", int, min_val=min_delay)
    settings['delay'] = (min_delay, max_delay)
    return settings

async def run_module(module_class, settings, accounts, proxies, module_name):
    # ... (Fungsi ini tidak berubah)
    print(Fore.GREEN + Style.BRIGHT + f"\n[ MEMULAI MODUL: {module_name} ]")
    for i, private_key in enumerate(accounts):
        proxy = proxies[i % len(proxies)] if proxies else None
        print(Fore.CYAN + f"\n--- Akun {i+1}/{len(accounts)}: {Account.from_key(private_key).address[:10]}... ---")
        if proxy: print(Fore.WHITE + f"   Proxy Digunakan: {proxy}")
        else: print(Fore.WHITE + f"   Proxy Digunakan: Tidak ada")
        try:
            bot = module_class(private_key=private_key, proxy=proxy)
            if module_name == "PHAROS": await bot.run_full_interaction_task(settings)
            elif module_name == "OPENFI": await bot.run_full_lending_cycle(settings)
            elif module_name == "GOTCHIPUS": await bot.run_minting_cycle(settings)
            elif module_name == "BROKEX": await bot.run_trading_cycle(settings)
            delay = random.randint(45, 90); print(Fore.BLUE + f"Jeda antar akun {delay} detik...")
            await asyncio.sleep(delay)
        except Exception as e:
            print(Fore.RED + f"Error di Modul {module_name} untuk akun {Account.from_key(private_key).address[:10]}: {e}")
            continue

async def run_all_modules(accounts, proxies):
    # ... (Fungsi ini tidak berubah)
    print(Fore.YELLOW + Style.BRIGHT + "\n[ MODE: JALANKAN SEMUA MODUL DENGAN PENGATURAN DEFAULT ]")
    modules_to_run = [(PharosModule, get_pharos_settings_default(), "PHAROS"),(OpenFiModule, get_openfi_settings_default(), "OPENFI"),(GotchipusModule, get_gotchipus_settings_default(), "GOTCHIPUS"),(BrokexModule, get_brokex_settings_default(), "BROKEX")]
    for i, (module_class, settings, module_name) in enumerate(modules_to_run):
        await run_module(module_class, settings, accounts, proxies, module_name)
        if i < len(modules_to_run) - 1:
            print(Fore.MAGENTA + Style.BRIGHT + f"\n\n=== MODUL {module_name} SELESAI, PINDAH KE MODUL BERIKUTNYA DALAM 15 DETIK ===\n\n")
            await asyncio.sleep(15)

# <<< PERUBAHAN UTAMA DIMULAI DI SINI >>>
async def main():
    try:
        with open('accounts.txt', 'r') as f: accounts = [line.strip() for line in f if line.strip()]
        if not accounts: print(Fore.RED + "File accounts.txt kosong."); return
        
        # --- DAPATKAN PILIHAN PENGGUNA SEKALI SAJA DI AWAL ---
        use_proxies = get_proxy_settings()
        proxies = []
        if use_proxies:
            try:
                with open('proxy.txt', 'r') as f: proxies = [line.strip() for line in f if line.strip()]
                if not proxies: print(Fore.RED + "proxy.txt kosong."); return
                print(Fore.GREEN + f"Berhasil memuat {len(proxies)} proxy.")
            except FileNotFoundError: print(Fore.RED + "file proxy.txt tidak ditemukan."); return
        else:
            print(Fore.GREEN + "Bot akan berjalan tanpa proxy.")

        display_main_menu()
        
        initial_choice = None
        while initial_choice is None:
            try:
                choice_input = input(Fore.BLUE + "Masukkan pilihan Anda: " + Style.RESET_ALL)
                if not choice_input: continue
                initial_choice = int(choice_input)
                if initial_choice not in [0, 1, 2, 3, 4, 5]:
                    print(Fore.RED + "Pilihan tidak valid. Harap masukkan angka antara 0-5."); initial_choice = None 
            except ValueError:
                print(Fore.RED + "Input tidak valid. Harap masukkan sebuah angka."); initial_choice = None

        if initial_choice == 0:
            print(Fore.YELLOW + "Bot dihentikan."); return

        # Dapatkan pengaturan sekali saja jika mode manual
        initial_settings = {}
        if initial_choice == 1: initial_settings = get_pharos_settings_interactive()
        elif initial_choice == 2: initial_settings = get_openfi_settings_interactive()
        elif initial_choice == 3: initial_settings = get_gotchipus_settings_interactive()
        elif initial_choice == 4: initial_settings = get_brokex_settings_interactive()

        # --- LOOP UTAMA YANG BERJALAN SELAMANYA ---
        cycle_count = 1
        while True:
            print(Fore.MAGENTA + Style.BRIGHT + f"\n\n==================== MEMULAI SIKLUS KE-{cycle_count} ====================")
            
            if initial_choice == 1: await run_module(PharosModule, initial_settings, accounts, proxies, "PHAROS")
            elif initial_choice == 2: await run_module(OpenFiModule, initial_settings, accounts, proxies, "OPENFI")
            elif initial_choice == 3: await run_module(GotchipusModule, initial_settings, accounts, proxies, "GOTCHIPUS")
            elif initial_choice == 4: await run_module(BrokexModule, initial_settings, accounts, proxies, "BROKEX")
            elif initial_choice == 5: await run_all_modules(accounts, proxies)
            
            print("\n" + Fore.GREEN + Style.BRIGHT + f"Siklus ke-{cycle_count} telah selesai.")
            cycle_count += 1
            
            # --- LOGIKA TUNGGU 24 JAM DENGAN COUNTDOWN ---
            total_seconds = 24 * 60 * 60
            for remaining_seconds in range(total_seconds, 0, -1):
                formatted_time = format_seconds_to_hms(remaining_seconds)
                print(Fore.CYAN + f"Bot akan menjalankan siklus berikutnya dalam: {formatted_time}" + Style.RESET_ALL, end="\r")
                await asyncio.sleep(1)

    except FileNotFoundError: print(Fore.RED + "Pastikan file 'accounts.txt' ada.")
    except Exception as e: print(Fore.RED + f"Terjadi kesalahan fatal: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nBot dihentikan oleh pengguna (Ctrl+C).")
