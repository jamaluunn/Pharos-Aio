# modules/primuslabs_module.py (MODUL BARU)
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from colorama import *
import asyncio, random, pytz
from datetime import datetime
import config # Menggunakan config terpusat

wib = pytz.timezone('Asia/Jakarta')

class PrimuslabsModule:
    def __init__(self, private_key: str, proxy: str = None):
        # DIADAPTASI: Constructor yang sesuai dengan main.py
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy # Proxy akan digunakan oleh _get_web3_provider
        self.web3 = None
        self.nonce = None

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    # DIADAPTASI: Menggunakan kembali metode koneksi, pengiriman tx, dan wait receipt yang tangguh
    def _get_web3_provider(self, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}
        if self.proxy:
            request_kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(random.choice(config.RPC_URLS), request_kwargs=request_kwargs))
                if web3.is_connected():
                    return web3
            except Exception as e:
                self.log(f"{Fore.YELLOW}Error koneksi RPC: {e}, mencoba lagi... ({attempt+1}/{retries}){Style.RESET_ALL}")
            asyncio.sleep(2 ** attempt)
        return None

    async def _send_raw_transaction_with_retries(self, tx, retries=5):
        try:
            if 'nonce' not in tx: tx['nonce'] = self.nonce
            if 'gas' not in tx: tx['gas'] = await asyncio.to_thread(self.web3.eth.estimate_gas, tx)
            if 'maxFeePerGas' not in tx: tx['maxFeePerGas'] = self.web3.to_wei('1.5', 'gwei')
            if 'maxPriorityFeePerGas' not in tx: tx['maxPriorityFeePerGas'] = self.web3.to_wei('1', 'gwei')
            if 'chainId' not in tx: tx['chainId'] = self.web3.eth.chain_id
            
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            for attempt in range(retries):
                try:
                    tx_hash = await asyncio.to_thread(self.web3.eth.send_raw_transaction, signed_tx.raw_transaction)
                    return tx_hash
                except (TransactionNotFound, asyncio.exceptions.TimeoutError):
                    pass
                except Exception as e:
                    self.log(f"{Fore.YELLOW}[Attempt {attempt + 1}] Kirim TX error: {e}{Style.RESET_ALL}")
                await asyncio.sleep(2 ** attempt)
            return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat membangun transaksi: {e}{Style.RESET_ALL}")
            return None

    async def _wait_for_receipt_with_retries(self, tx_hash, timeout=300, retries=5):
        self.log(f"Transaksi dikirim, menunggu konfirmasi... Hash: {tx_hash.hex()}")
        for attempt in range(retries):
            try:
                receipt = await asyncio.to_thread(self.web3.eth.wait_for_transaction_receipt, tx_hash, timeout=timeout)
                if receipt.status == 1:
                    self.log(f"{Fore.GREEN}Transaksi sukses! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                    return receipt
                else:
                    self.log(f"{Fore.RED}Transaksi gagal! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                    return None
            except (TransactionNotFound, asyncio.exceptions.TimeoutError):
                pass
            except Exception as e:
                self.log(f"{Fore.YELLOW}[Attempt {attempt + 1}] Menunggu receipt error: {e}{Style.RESET_ALL}")
            await asyncio.sleep(2 ** attempt)
        return None

    async def _execute_transaction(self, tx_data, value_wei=0):
        tx = tx_data.build_transaction({"from": self.address, "value": value_wei})
        tx_hash_bytes = await self._send_raw_transaction_with_retries(tx)
        if not tx_hash_bytes: return None
        receipt = await self._wait_for_receipt_with_retries(tx_hash_bytes)
        if receipt:
            self.nonce += 1
            return receipt
        return None

    def generate_username(self):
        # Fungsi spesifik untuk modul ini, jadi kita pertahankan
        first_parts = ["reza", "andi", "rama", "dika", "zaki", "yoga", "galih", "fajar", "bagas", "ilham", "riko", "arif", "dian", "ivan", "fikri", "adit", "udin", "eko", "faiz", "farhan", "rizky", "david", "ryan", "kevin", "aldi", "joko", "yusuf", "hadi", "andre", "deni", "bayu", "rafi", "irfan", "ari", "fauzi", "sandy", "brian", "randi", "wahyu", "salman", "rudi", "agus"]
        second_parts = ["dev", "bot", "jr", "x", "kun", "gamer", "tv", "yt", "zz", "id", "io", "tech", "ops", "hub", "net", "app", "xyz", "cloud", "main", "lab", "pro", "dark", "light", "sky", "nova", "droid", "blast", "next", "prime", "origin", "script", "mind", "pulse", "spark", "core", "flux", "shift", "sage", "root", "code"]
        numbers = [str(random.randint(10, 999)) for _ in range(50)]
        separators = ["", "_", ""]
        username = random.choice(first_parts) + random.choice(separators) + random.choice(second_parts + numbers)
        return username[:15]

    async def send_tip(self, handler: str, amount: float):
        self.log(f"Mengirim tip {amount} PHRS ke handler '{handler}'...")
        try:
            amount_in_wei = self.web3.to_wei(amount, "ether")
            
            token_param = (1, self.web3.to_checksum_address("0x0000000000000000000000000000000000000000"))
            recipient_param = ("x", handler, amount_in_wei, [])

            contract = self.web3.eth.contract(address=config.PRIMUSLABS_SEND_ROUTER_ADDRESS, abi=config.PRIMUSLABS_CONTRACT_ABI)
            tip_data = contract.functions.tip(token_param, recipient_param)
            
            return await self._execute_transaction(tip_data, value_wei=amount_in_wei) is not None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat mengirim tip: {e}{Style.RESET_ALL}")
            return False

    async def run_tipping_cycle(self, settings: dict):
        # BARU: Fungsi utama yang akan dipanggil oleh main.py
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS PRIMUSLABS UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        
        self.web3 = self._get_web3_provider()
        if not self.web3: return
        self.nonce = self.web3.eth.get_transaction_count(self.address)

        tip_count = random.randint(settings['tip_count'][0], settings['tip_count'][1])
        delay_min, delay_max = settings['delay']

        for i in range(tip_count):
            self.log(f"{Style.BRIGHT}--- Tip ke-{i+1}/{tip_count} ---")
            tip_amount = random.uniform(settings['tip_amount'][0], settings['tip_amount'][1])
            handler = self.generate_username()
            
            balance = self.web3.from_wei(self.web3.eth.get_balance(self.address), "ether")
            if balance < tip_amount:
                self.log(f"{Fore.RED}Saldo tidak cukup ({balance:.4f} PHRS) untuk mengirim tip {tip_amount:.4f} PHRS.{Style.RESET_ALL}")
                break # Hentikan jika saldo tidak cukup

            await self.send_tip(handler, tip_amount)
            
            if i < tip_count - 1:
                delay = random.uniform(delay_min, delay_max)
                self.log(f"Jeda {delay:.2f} detik...")
                await asyncio.sleep(delay)
        
        self.log(f"{Fore.MAGENTA}--- SIKLUS PRIMUSLABS UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")