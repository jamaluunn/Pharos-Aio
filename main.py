# main.py (Final Cleaned Version)
import asyncio
import random
from colorama import init, Fore, Style
from eth_account import Account
from datetime import datetime, timedelta

# Impor semua modul
from modules.pharos_module import PharosModule
from modules.openfi_module import OpenFiModule
from modules.gotchipus_module import GotchipusModule
from modules.brokex_module import BrokexModule
from modules.faroswap_module import FaroswapModule
import config

init(autoreset=True)

# --- FUNGSI UTILITAS ---
def format_seconds_to_hms(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

def get_user_input(prompt, input_type=float, min_val=0, max_val=None):
    while True:
        try:
            value = input_type(input(Fore.YELLOW + prompt + Style.RESET_ALL))
            if max_val is not None:
                if min_val <= value <= max_val: return value
                else: print(Fore.RED + f"Nilai harus di antara {min_val} dan {max_val}.")
            elif value >= min_val:
                return value
            else:
                print(Fore.RED + f"Nilai harus >= {min_val}.")
        except ValueError:
            print(Fore.RED + f"Input tidak valid.")

# --- FUNGSI MENU ---
def display_main_menu():
    print(Fore.CYAN + Style.BRIGHT + "\n==============================================")
    print(Fore.CYAN + Style.BRIGHT + "==         AIO PHAROS ECOSYSTEM BOT         ==")
    print(Fore.CYAN + Style.BRIGHT + "==============================================")
    print(Fore.WHITE + Style.BRIGHT + "           by Airdropversity ID")
    print(Fore.BLUE + Style.BRIGHT +   "         https://t.me/AirdropversityID")
    print(Fore.CYAN + Style.BRIGHT + "==============================================")
    print(Fore.GREEN + "\nPilih Modul:")
    print("1. Modul Pharos (Zenith Swap & LP)")
    print("2. Modul OpenFi (Lending)")
    print("3. Modul Gotchipus (NFT)")
    print("4. Modul Brokex (Trading)")
    print("5. Modul Faroswap (DODO Router)")
    print(Fore.CYAN + "----------------------------------------------")
    print(Fore.YELLOW + "6. Jalankan SEMUA Modul Otomatis")
    print(Fore.WHITE + "7. Mint Testnet Badge (Satu Kali)")
    print(Fore.MAGENTA + "8. Cek Info Akun Pharos (Poin & Rank)")
    print(Fore.RED + "0. Keluar")
    print(Style.BRIGHT + "==============================================")

def display_pharos_submenu():
    print("\n--- Menu Modul Pharos ---")
    print("1. Jalankan Siklus Penuh")
    print("2. Tes 'Send to Friends'")
    print("3. Tes 'Zenith Swap' (WPHRS -> USDC)")
    print("4. Tes 'Add Liquidity' (WPHRS/USDC)")
    print("0. Kembali ke Menu Utama")
    return get_user_input("Pilih fitur yang ingin diuji: ", int, 0, 4)

def display_faroswap_submenu():
    print("\n--- Menu Modul Faroswap (DODO Router) ---")
    print("1. Jalankan Siklus Penuh")
    print("2. Tes Deposit (Wrap PHRS)")
    print("3. Tes Swap Acak")
    print("4. Tes Add DVM Liquidity (USDC/USDT)")
    print("0. Kembali ke Menu Utama")
    return get_user_input("Pilih fitur yang ingin diuji: ", int, 0, 4)

def display_brokex_submenu():
    print("\n--- Menu Modul Brokex ---")
    print("1. Jalankan Siklus Penuh")
    print("2. Tes Add Liquidity Pool")
    print("3. Tes Withdraw Liquidity Pool")
    print("0. Kembali ke Menu Utama")
    return get_user_input("Pilih fitur yang ingin diuji: ", int, 0, 3)

# --- FUNGSI PENGATURAN DEFAULT ---
def get_pharos_settings_default():
    # --- PERUBAHAN DI FUNGSI INI ---
    return {
        "delay": (10, 30),
        "wrap_amount": (0.01, 0.05),
        "zenith_swap_count": (3, 7),
        "lp_count": (3, 7),
        "send_friends_count": (1, 3),
        "send_friends_amount": (0.001, 0.002),
        
        # Hapus 'zenith_swap_amount' dan ganti dengan yang lebih spesifik
        "zenith_swap_amount_wphrs": (0.005, 0.01),  # Jumlah untuk swap DARI WPHRS
        "zenith_swap_amount_usdc": (0.1, 2),      # Jumlah untuk swap DARI USDC
        "zenith_swap_amount_usdt": (0.1, 3),      # Jumlah untuk swap DARI USDT

        # Pengaturan LP tetap
        "lp_amount_wphrs": (0.001, 0.02),
        "lp_amount_usdc": (0.1, 0.2)
    }
def get_openfi_settings_default():
    return {"delay": (15, 30), "deposit_amount": (0.001, 0.01), "supply_amount": (5, 11), "borrow_amount": (0.01, 0.05), "withdraw_amount": (0.01, 0.05)}
def get_gotchipus_settings_default():
    return {"delay": (10, 25)}
def get_brokex_settings_default():
    return {
        "delay": (10, 30),
        "trade_count": (3, 5),
        "trade_amount": (10.0, 14.5),
        "lp_add_amount": 5.0,         # Jumlah USDT untuk add liquidity
        "lp_withdraw_amount": 0.01      # Jumlah LP token untuk withdraw
    }
def get_faroswap_settings_default():
    return {"delay": (15, 30), "deposit_amount": (0.01, 0.015), "swap_count": (2, 7), "swap_amount": (0.01, 0.1), "lp_count": (2, 7), "lp_amount": (0.01, 0.2)}

# --- FUNGSI RUNNER ---
async def run_feature_for_all_accounts(module_class, feature_func_name, accounts, proxies, *args):
    print(Fore.GREEN + Style.BRIGHT + f"\n[ MENJALANKAN FITUR: {feature_func_name} ]")
    for i, private_key in enumerate(accounts):
        proxy = proxies[i % len(proxies)] if proxies else None
        print(Fore.CYAN + f"\n--- Akun {i+1}/{len(accounts)}: {Account.from_key(private_key).address[:10]}... ---")
        try:
            bot = module_class(private_key=private_key, proxy=proxy)
            feature_func = getattr(bot, feature_func_name)
            await feature_func(*args)
            await asyncio.sleep(random.randint(5,10))
        except Exception as e:
            print(Fore.RED + f"Error pada fitur {feature_func_name}: {e}")

async def run_full_cycle_for_all_accounts(module_class, settings_func, accounts, proxies, module_name):
    print(Fore.GREEN + Style.BRIGHT + f"\n[ MEMULAI SIKLUS PENUH: {module_name} ]")
    settings = settings_func()
    runner_func_name = {"PHAROS": "run_full_interaction_task", "OPENFI": "run_full_lending_cycle", "GOTCHIPUS": "run_minting_cycle", "BROKEX": "run_trading_cycle", "FAROSWAP": "run_full_cycle"}[module_name]
    for i, private_key in enumerate(accounts):
        proxy = proxies[i % len(proxies)] if proxies else None
        print(Fore.CYAN + f"\n--- Akun {i+1}/{len(accounts)}: {Account.from_key(private_key).address[:10]}... ---")
        try:
            bot = module_class(private_key=private_key, proxy=proxy)
            runner_func = getattr(bot, runner_func_name)
            await runner_func(settings)
            delay = random.randint(45, 90); print(Fore.BLUE + f"Jeda antar akun {delay} detik...")
            await asyncio.sleep(delay)
        except Exception as e: print(Fore.RED + f"Error di Modul {module_name} untuk akun {Account.from_key(private_key).address[:10]}: {e}")

async def run_all_modules_auto(accounts, proxies):
    print(Fore.YELLOW + Style.BRIGHT + "\n[ MODE: JALANKAN SEMUA MODUL OTOMATIS ]")
    modules_to_run = [(PharosModule, get_pharos_settings_default, "PHAROS"), (OpenFiModule, get_openfi_settings_default, "OPENFI"), (GotchipusModule, get_gotchipus_settings_default, "GOTCHIPUS"), (BrokexModule, get_brokex_settings_default, "BROKEX"), (FaroswapModule, get_faroswap_settings_default, "FAROSWAP")]
    random.shuffle(modules_to_run)
    for i, (module_class, settings_func, module_name) in enumerate(modules_to_run):
        await run_full_cycle_for_all_accounts(module_class, settings_func, accounts, proxies, module_name)
        if i < len(modules_to_run) - 1: print(Fore.MAGENTA + Style.BRIGHT + f"\n\n=== MODUL {module_name} SELESAI, PINDAH KE MODUL BERIKUTNYA ===\n\n"); await asyncio.sleep(15)

# --- MAIN LOOP ---
async def main():
    try:
        print(Fore.CYAN + Style.BRIGHT + "\n==============================================")
        print(Fore.CYAN + Style.BRIGHT + "==         AIO PHAROS ECOSYSTEM BOT         ==")
        print(Fore.CYAN + Style.BRIGHT + "==============================================")
        print(Fore.WHITE + Style.BRIGHT + "           by Airdropversity ID")
        print(Fore.BLUE + Style.BRIGHT +   "         https://t.me/AirdropversityID")
        print(Fore.CYAN + Style.BRIGHT + "==============================================")

        with open('accounts.txt', 'r') as f: accounts = [line.strip() for line in f if line.strip()]
        if not accounts: print(Fore.RED + "File accounts.txt kosong."); return
        
        use_proxy_input = input(Fore.YELLOW + "\nGunakan proxy dari proxy.txt? (y/n): " + Style.RESET_ALL).lower()
        proxies = []
        if use_proxy_input == 'y':
            with open('proxy.txt', 'r') as f: proxies = [line.strip() for line in f if line.strip()]
            if not proxies: print(Fore.RED + "proxy.txt kosong."); return
            print(Fore.GREEN + f"Berhasil memuat {len(proxies)} proxy.")
        else: print(Fore.GREEN + "Bot akan berjalan tanpa proxy.")

        print("\n" + Fore.CYAN + Style.BRIGHT + "Pilih Mode Eksekusi:")
        print("1. Mode Manual (Pilih dari menu)")
        print("2. Mode Otomatis (Loop 20-24 jam non-stop)")
        execution_mode = get_user_input("Pilihan Anda [1/2]: ", int, 1, 2)

        if execution_mode == 2:
            print(Fore.GREEN + Style.BRIGHT + "\nMode Otomatis Aktif. Siklus pertama akan segera dimulai...")
            while True:
                await run_all_modules_auto(accounts, proxies)
                wait_hours = random.uniform(20, 24)
                wait_seconds = wait_hours * 3600
                next_run_time = datetime.now() + timedelta(seconds=wait_seconds)
                print(Fore.GREEN + Style.BRIGHT + "\n========================================================")
                print(Fore.GREEN + Style.BRIGHT + f"=== SEMUA SIKLUS SELESAI. BOT AKAN TIDUR. ===")
                print(Fore.GREEN + Style.BRIGHT + f"=== Siklus berikutnya dimulai dalam: {format_seconds_to_hms(wait_seconds)} ===")
                print(Fore.GREEN + Style.BRIGHT + f"=== Perkiraan waktu: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
                print(Fore.GREEN + Style.BRIGHT + "========================================================")
                await asyncio.sleep(wait_seconds)
        else:
            while True:
                display_main_menu()
                main_choice = get_user_input("Pilih Modul: ", int, 0, 8)
                if main_choice == 1:
                    while True:
                        sub_choice = display_pharos_submenu()
                        if sub_choice == 1: await run_full_cycle_for_all_accounts(PharosModule, get_pharos_settings_default, accounts, proxies, "PHAROS")
                        elif sub_choice == 2: amount = get_user_input("Jumlah PHRS per transfer: ", float); await run_feature_for_all_accounts(PharosModule, "run_send_to_friends_task", accounts, proxies, amount)
                        elif sub_choice == 3: amount = get_user_input("Jumlah WPHRS untuk swap: ", float); await run_feature_for_all_accounts(PharosModule, "perform_zenith_swap", accounts, proxies, config.PHAROS_WPHRS_CONTRACT_ADDRESS, config.PHAROS_USDC_CONTRACT_ADDRESS, amount)
                        elif sub_choice == 4: amount_wphrs = get_user_input("Jumlah WPHRS untuk LP: ", float); amount_usdc = get_user_input("Jumlah USDC untuk LP: ", float); await run_feature_for_all_accounts(PharosModule, "add_liquidity", accounts, proxies, config.PHAROS_WPHRS_CONTRACT_ADDRESS, config.PHAROS_USDC_CONTRACT_ADDRESS, amount_wphrs, amount_usdc)
                        elif sub_choice == 0: break
                        print(Fore.GREEN + "\nFitur selesai. Kembali ke sub-menu Pharos...")
                elif main_choice == 5:
                     while True:
                        sub_choice = display_faroswap_submenu()
                        if sub_choice == 1: await run_full_cycle_for_all_accounts(FaroswapModule, get_faroswap_settings_default, accounts, proxies, "FAROSWAP")
                        elif sub_choice == 2: amount = get_user_input("Jumlah PHRS untuk deposit (wrap): ", float); await run_feature_for_all_accounts(FaroswapModule, "deposit_phrs", accounts, proxies, amount)
                        elif sub_choice == 3: amount = get_user_input("Jumlah token per swap: ", float); tokens = {"WPHRS": config.FAROSWAP_WPHRS_ADDRESS, "USDC": config.FAROSWAP_USDC_ADDRESS, "USDT": config.FAROSWAP_USDT_ADDRESS}; from_t, to_t = random.sample(list(tokens.keys()), 2); print(f"Swap acak dipilih: {from_t} -> {to_t}"); await run_feature_for_all_accounts(FaroswapModule, "perform_swap", accounts, proxies, tokens[from_t], tokens[to_t], amount)
                        elif sub_choice == 4: amount = get_user_input("Jumlah token per sisi LP (USDC/USDT): ", float); base, quote = random.sample([config.FAROSWAP_USDC_ADDRESS, config.FAROSWAP_USDT_ADDRESS], 2); print(f"Pair LP acak dipilih: {base[-6:]}... / {quote[-6:]}..."); await run_feature_for_all_accounts(FaroswapModule, "add_dvm_liquidity", accounts, proxies, base, quote, amount)
                        elif sub_choice == 0: break
                        print(Fore.GREEN + "\nFitur selesai. Kembali ke sub-menu Faroswap...")
                elif main_choice == 4:
                     while True:
                        sub_choice = display_brokex_submenu()
                        if sub_choice == 1:
                            await run_full_cycle_for_all_accounts(BrokexModule, get_brokex_settings_default, accounts, proxies, "BROKEX")
                        elif sub_choice == 2:
                            amount = get_user_input("Jumlah USDT untuk Add Liquidity: ", float)
                            await run_feature_for_all_accounts(BrokexModule, "add_liquidity", accounts, proxies, amount)
                        elif sub_choice == 3:
                            lp_amount = get_user_input("Jumlah LP Token untuk Withdraw: ", float)
                            await run_feature_for_all_accounts(BrokexModule, "withdraw_liquidity", accounts, proxies, lp_amount)
                        elif sub_choice == 0:
                            break
                        print(Fore.GREEN + "\nFitur selesai. Kembali ke sub-menu Brokex...")
                elif main_choice in [2,3,4]:
                     print(Fore.YELLOW + "Sub-menu belum tersedia. Menjalankan siklus penuh...");
                     if main_choice == 2: await run_full_cycle_for_all_accounts(OpenFiModule, get_openfi_settings_default, accounts, proxies, "OPENFI")
                     elif main_choice == 3: await run_full_cycle_for_all_accounts(GotchipusModule, get_gotchipus_settings_default, accounts, proxies, "GOTCHIPUS")
                     elif main_choice == 4: await run_full_cycle_for_all_accounts(BrokexModule, get_brokex_settings_default, accounts, proxies, "BROKEX")
                elif main_choice == 6: await run_all_modules_auto(accounts, proxies); print(Fore.GREEN + Style.BRIGHT + "\nSemua siklus selesai.")
                elif main_choice == 7: await run_feature_for_all_accounts(PharosModule, "run_mint_badge_task", accounts, proxies); print(Fore.GREEN + "\nTugas Mint Badge selesai.")
                elif main_choice == 8: await run_feature_for_all_accounts(PharosModule, "display_user_profile", accounts, proxies); print(Fore.GREEN + "\nPengecekan Info Akun selesai.")
                elif main_choice == 0: print(Fore.YELLOW + "Terima kasih!"); break
                else: print(Fore.RED + "Pilihan tidak valid.")
    except FileNotFoundError as e: print(Fore.RED + f"File tidak ditemukan: {e}")
    except Exception as e: print(Fore.RED + f"Terjadi kesalahan fatal: {e}")

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print(Fore.YELLOW + "\nBot dihentikan oleh pengguna.")