# modules/brokex_module.py (VERSI BARU YANG DI-UPGRADE)
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from colorama import *
import asyncio, json, time, random, pytz, re
from datetime import datetime
import config
import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent

wib = pytz.timezone('Asia/Jakarta')

class BrokexModule:
    def __init__(self, private_key: str, proxy: str = None):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy
        self.web3 = None # Akan diinisialisasi nanti
        self.nonce = None # Akan diinisialisasi nanti
        self.headers = {"User-Agent": FakeUserAgent().random}

    def _get_web3_provider(self, retries=3, timeout=60):
        # DIPERBARUI: Logika koneksi RPC dengan retry
        request_kwargs = {"timeout": timeout}
        if self.proxy:
            request_kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(random.choice(config.RPC_URLS), request_kwargs=request_kwargs))
                if web3.is_connected():
                    return web3
                self.log(f"{Fore.YELLOW}Gagal terhubung ke RPC, mencoba lagi... ({attempt+1}/{retries}){Style.RESET_ALL}")
            except Exception as e:
                self.log(f"{Fore.YELLOW}Error koneksi RPC: {e}, mencoba lagi... ({attempt+1}/{retries}){Style.RESET_ALL}")
            time.sleep(2 ** attempt) # Exponential backoff
        self.log(f"{Fore.RED}Gagal terhubung ke semua RPC setelah {retries} percobaan.{Style.RESET_ALL}")
        return None

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    # BARU: Fungsi pengirim transaksi yang tangguh dengan retry
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
                except TransactionNotFound:
                    pass # Coba lagi
                except Exception as e:
                    self.log(f"{Fore.YELLOW}[Attempt {attempt + 1}] Kirim TX error: {e}{Style.RESET_ALL}")
                await asyncio.sleep(2 ** attempt)
            
            self.log(f"{Fore.RED}Gagal mengirim transaksi setelah {retries} percobaan.{Style.RESET_ALL}")
            return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat membangun transaksi: {e}{Style.RESET_ALL}")
            return None

    # BARU: Fungsi untuk menunggu receipt dengan retry
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
            except TransactionNotFound:
                pass # Coba lagi
            except Exception as e:
                self.log(f"{Fore.YELLOW}[Attempt {attempt + 1}] Menunggu receipt error: {e}{Style.RESET_ALL}")
            await asyncio.sleep(2 ** attempt)

        self.log(f"{Fore.RED}Gagal mendapatkan receipt untuk {tx_hash.hex()} setelah {retries} percobaan.{Style.RESET_ALL}")
        return None

    # BARU: Helper untuk proxy di aiohttp
    def _build_proxy_config(self):
        if not self.proxy:
            return None, None, None
        if self.proxy.startswith("socks"):
            connector = ProxyConnector.from_url(self.proxy)
            return connector, None, None
        elif self.proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", self.proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = aiohttp.BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, self.proxy, None
        raise ValueError("Tipe proxy tidak didukung.")

    # DIPERBARUI: get_proof dengan retry dan proxy yang lebih baik
    async def get_proof(self, pair_id, retries=5):
        url = f"https://proofcrypto-production.up.railway.app/proof?pairs={pair_id}"
        connector, proxy_url, proxy_auth = self._build_proxy_config()
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=15)) as session:
                    async with session.get(url, headers=self.headers, proxy=proxy_url, proxy_auth=proxy_auth) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get('proof')
                        self.log(f"{Fore.YELLOW}Gagal ambil proof (Status: {resp.status}), mencoba lagi...{Style.RESET_ALL}")
            except Exception as e:
                self.log(f"{Fore.YELLOW}Error saat ambil proof: {e}, mencoba lagi...{Style.RESET_ALL}")
            await asyncio.sleep(2 ** attempt)
        return None

    # DIPERBARUI: Semua fungsi on-chain sekarang menggunakan sistem transaksi baru
    async def _execute_transaction(self, tx_data):
        tx = tx_data.build_transaction({"from": self.address, "value": 0})
        tx_hash_bytes = await self._send_raw_transaction_with_retries(tx)
        if not tx_hash_bytes:
            return None
        receipt = await self._wait_for_receipt_with_retries(tx_hash_bytes)
        if receipt:
            self.nonce += 1
            return receipt
        return None

    async def approve_usdt(self, spender_address, amount):
        spender = self.web3.to_checksum_address(spender_address)
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_USDT_ADDRESS), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10**decimals))
        allowance = token_contract.functions.allowance(self.address, spender).call()

        if allowance >= amount_in_wei:
            self.log(f"{Fore.GREEN}Approval USDT untuk {spender[-6:]}.. sudah cukup.{Style.RESET_ALL}")
            return True
        
        self.log(f"Melakukan approval USDT untuk {spender[-6:]}..")
        approve_tx_data = token_contract.functions.approve(spender, 2**256 - 1)
        receipt = await self._execute_transaction(approve_tx_data)
        if receipt:
            await asyncio.sleep(random.randint(5, 8))
            return True
        return False

    async def perform_claim_faucet(self):
        self.log("Memeriksa status faucet Brokex...")
        contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_CLAIM_ROUTER_ADDRESS), abi=config.BROKEX_CLAIM_ABI)
        has_claimed = contract.functions.hasClaimed(self.address).call()
        if has_claimed:
            self.log(f"{Fore.YELLOW}Faucet sudah pernah diklaim untuk akun ini.{Style.RESET_ALL}")
            return True # Anggap sukses jika sudah pernah
        
        self.log("Faucet belum diklaim, mencoba klaim USDT...")
        tx_data = contract.functions.claim()
        return await self._execute_transaction(tx_data) is not None

    async def perform_trade(self, pair_id, is_long, amount):
        pair_name = next((p['name'] for p in config.BROKEX_PAIRS if p['id'] == pair_id), "Unknown")
        action_name = "LONG" if is_long else "SHORT"
        self.log(f"Mencoba trade {action_name} {amount:.2f} USDT pada pair {pair_name}...")

        if not await self.approve_usdt(config.BROKEX_TRADE_ROUTER_ADDRESS, amount):
            self.log(f"{Fore.RED}Gagal approve USDT, trade dibatalkan.{Style.RESET_ALL}"); return
        
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_USDT_ADDRESS), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        trade_amount_wei = int(amount * (10 ** decimals))

        # Menggunakan ABI baru yang lebih lengkap
        trade_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_TRADE_ROUTER_ADDRESS), abi=config.BROKEX_ORDER_ABI_UPDATED)
        
        # Coba dengan proof
        proof = await self.get_proof(pair_id)
        if proof:
            try:
                tx_data = trade_contract.functions.openPosition(pair_id, proof, is_long, 5, trade_amount_wei, 0, 0)
                if await self._execute_transaction(tx_data): return
            except Exception as e:
                self.log(f"{Fore.YELLOW}Trade dengan proof gagal: {e}{Style.RESET_ALL}. Coba fallback...")

        # Fallback ke createPendingOrder
        try:
            self.log("Mencoba fallback ke createPendingOrder...")
            tx_data = trade_contract.functions.createPendingOrder(pair_id, is_long, trade_amount_wei, 5, 0, 0)
            await self._execute_transaction(tx_data)
        except Exception as e:
            self.log(f"{Fore.RED}Trade fallback juga gagal: {e}{Style.RESET_ALL}")

    async def add_liquidity(self, amount):
        self.log(f"Menambah liquidity pool {amount:.2f} USDT...")
        if not await self.approve_usdt(config.BROKEX_POOL_ROUTER_ADDRESS, amount):
            self.log(f"{Fore.RED}Gagal approve USDT untuk LP, add liquidity dibatalkan.{Style.RESET_ALL}"); return
        
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_USDT_ADDRESS), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10 ** decimals))
        pool_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_POOL_ROUTER_ADDRESS), abi=config.BROKEX_POOL_ABI)
        tx_data = pool_contract.functions.depositLiquidity(amount_in_wei)
        await self._execute_transaction(tx_data)

    async def withdraw_liquidity(self, lp_amount):
        self.log(f"Withdraw liquidity pool {lp_amount:.4f} LP Token...")
        pool_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_POOL_ROUTER_ADDRESS), abi=config.BROKEX_POOL_ABI)
        decimals = 18 # LP token decimals
        lp_amount_wei = int(lp_amount * (10 ** decimals))
        tx_data = pool_contract.functions.withdrawLiquidity(lp_amount_wei)
        await self._execute_transaction(tx_data)

    # --- BARU: Fungsi-fungsi untuk close position ---
    async def get_user_open_ids(self):
        try:
            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_TRADE_ROUTER_ADDRESS), abi=config.BROKEX_ORDER_ABI_UPDATED)
            return await asyncio.to_thread(contract.functions.getUserOpenIds(self.address).call)
        except Exception as e:
            self.log(f"{Fore.RED}Gagal mendapatkan Open IDs: {e}{Style.RESET_ALL}")
            return []

    async def close_random_position(self):
        self.log("Mencari posisi terbuka untuk ditutup...")
        open_ids = await self.get_user_open_ids()
        if not open_ids:
            self.log(f"{Fore.YELLOW}Tidak ada posisi trading yang terbuka untuk ditutup.{Style.RESET_ALL}")
            return True # Anggap sukses jika tidak ada yang perlu ditutup

        open_id_to_close = random.choice(open_ids)
        self.log(f"Menutup posisi dengan ID: {open_id_to_close}...")
        
        try:
            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_TRADE_ROUTER_ADDRESS), abi=config.BROKEX_ORDER_ABI_UPDATED)
            position_details = await asyncio.to_thread(contract.functions.getOpenById(open_id_to_close).call)
            pair_id = position_details[2] # assetIndex
            
            proof = await self.get_proof(pair_id)
            if not proof:
                self.log(f"{Fore.RED}Gagal mendapatkan proof untuk menutup posisi. Dibatalkan.{Style.RESET_ALL}")
                return False

            tx_data = contract.functions.closePosition(open_id_to_close, proof)
            return await self._execute_transaction(tx_data) is not None
        except Exception as e:
            self.log(f"{Fore.RED}Gagal menutup posisi ID {open_id_to_close}: {e}{Style.RESET_ALL}")
            return False

    # DIPERBARUI: Siklus utama yang lebih komprehensif
    async def run_trading_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS TRADING BROKEX UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        
        self.web3 = self._get_web3_provider()
        if not self.web3: return
        self.nonce = self.web3.eth.get_transaction_count(self.address)

        delay_min, delay_max = settings['delay']

        # 1. Klaim Faucet
        if not await self.perform_claim_faucet():
            self.log(f"{Fore.YELLOW}Gagal klaim faucet, mungkin akan ada masalah dengan saldo.{Style.RESET_ALL}")
        await asyncio.sleep(random.uniform(delay_min, delay_max))

        # 2. Open Trade
        trade_count = random.randint(settings['trade_count'][0], settings['trade_count'][1])
        for i in range(trade_count):
            self.log(f"{Style.BRIGHT}--- Trade Open ke-{i+1}/{trade_count} ---")
            trade_amount = random.uniform(settings['trade_amount'][0], settings['trade_amount'][1])
            pair = random.choice(config.BROKEX_PAIRS)
            is_long = random.choice([True, False])
            await self.perform_trade(pair['id'], is_long, trade_amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        # 3. Close Trade (BARU)
        close_trade_count = random.randint(settings.get('close_trade_count', [0, 0])[0], settings.get('close_trade_count', [0, 0])[1])
        if close_trade_count > 0:
            for i in range(close_trade_count):
                self.log(f"{Style.BRIGHT}--- Trade Close ke-{i+1}/{close_trade_count} ---")
                await self.close_random_position()
                await asyncio.sleep(random.uniform(delay_min, delay_max))

        # 4. Add Liquidity
        lp_add_amount = settings.get("lp_add_amount")
        if lp_add_amount:
            await self.add_liquidity(lp_add_amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        # 5. Withdraw Liquidity
        lp_withdraw_amount = settings.get("lp_withdraw_amount")
        if lp_withdraw_amount:
            await self.withdraw_liquidity(lp_withdraw_amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        self.log(f"{Fore.MAGENTA}--- SIKLUS TRADING BROKEX UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")