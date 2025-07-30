# modules/aquaflux_module.py (MODUL BARU)
from web3 import Web3
from web3.exceptions import TransactionNotFound
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from colorama import *
import asyncio, json, time, random, pytz, re
from datetime import datetime
import config
import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent

wib = pytz.timezone('Asia/Jakarta')

class AquafluxModule:
    def __init__(self, private_key: str, proxy: str = None):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy
        self.web3 = None
        self.nonce = None
        self.access_token = None
        self.headers = {**config.AQUAFLUX_HEADERS, "User-Agent": FakeUserAgent().random}

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    # --- BAGIAN HELPER YANG DI-STANDARDISASI ---
    def _get_web3_provider(self, retries=3, timeout=60):
        # ... (Sama seperti modul sebelumnya, tidak perlu disalin ulang jika sudah ada di base class)
        # Untuk kesederhanaan, kita salin lagi di sini
        request_kwargs = {"timeout": timeout}
        if self.proxy:
            request_kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}
        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(random.choice(config.RPC_URLS), request_kwargs=request_kwargs))
                if web3.is_connected(): return web3
            except Exception as e: self.log(f"{Fore.YELLOW}Error koneksi RPC: {e}, mencoba lagi..{Style.RESET_ALL}")
            time.sleep(2 ** attempt)
        return None

    def _build_proxy_config(self):
        if not self.proxy: return None, None, None
        if self.proxy.startswith("socks"): return ProxyConnector.from_url(self.proxy), None, None
        elif self.proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", self.proxy)
            if match:
                username, password, host_port = match.groups()
                return None, f"http://{host_port}", aiohttp.BasicAuth(username, password)
            return None, self.proxy, None
        raise ValueError("Tipe proxy tidak didukung.")

    async def _send_raw_transaction_with_retries(self, tx, retries=5):
        try:
            tx.update({'nonce': self.nonce, 'from': self.address})
            if 'gas' not in tx: tx['gas'] = await asyncio.to_thread(self.web3.eth.estimate_gas, tx)
            if 'maxFeePerGas' not in tx: tx['maxFeePerGas'] = self.web3.to_wei('1.5', 'gwei')
            if 'maxPriorityFeePerGas' not in tx: tx['maxPriorityFeePerGas'] = self.web3.to_wei('1', 'gwei')
            if 'chainId' not in tx: tx['chainId'] = self.web3.eth.chain_id
            
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            for attempt in range(retries):
                try:
                    tx_hash = await asyncio.to_thread(self.web3.eth.send_raw_transaction, signed_tx.raw_transaction)
                    return tx_hash
                except Exception: await asyncio.sleep(2 ** attempt)
            return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat membangun transaksi: {e}{Style.RESET_ALL}")
            return None

    async def _wait_for_receipt_with_retries(self, tx_hash, timeout=300):
        self.log(f"Transaksi dikirim, menunggu konfirmasi... Hash: {tx_hash.hex()}")
        try:
            receipt = await asyncio.to_thread(self.web3.eth.wait_for_transaction_receipt, tx_hash, timeout=timeout)
            if receipt.status == 1:
                self.log(f"{Fore.GREEN}Transaksi sukses! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                return receipt
            else:
                self.log(f"{Fore.RED}Transaksi gagal! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                return None
        except Exception as e:
            self.log(f"{Fore.RED}Gagal mendapatkan receipt untuk {tx_hash.hex()}: {e}{Style.RESET_ALL}")
            return None

    async def _execute_transaction(self, tx_data, value_wei=0):
        tx = tx_data.build_transaction({"value": value_wei})
        tx_hash_bytes = await self._send_raw_transaction_with_retries(tx)
        if not tx_hash_bytes: return None
        receipt = await self._wait_for_receipt_with_retries(tx_hash_bytes)
        if receipt:
            self.nonce += 1
            return receipt
        return None

    # --- LOGIKA SPESIFIK AQUAFLUX ---
    
    async def _api_request(self, method, endpoint, **kwargs):
        url = f"{config.AQUAFLUX_BASE_API}/{endpoint}"
        connector, proxy_url, proxy_auth = self._build_proxy_config()
        
        for attempt in range(5):
            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.request(method, url, proxy=proxy_url, proxy_auth=proxy_auth, timeout=20, **kwargs) as response:
                        if response.status == 403: # Error spesifik dari API
                            err_data = await response.json()
                            self.log(f"{Fore.RED}API Error: {err_data.get('message', 'Forbidden')}{Style.RESET_ALL}")
                            return None
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                self.log(f"{Fore.YELLOW}Error request API ke {endpoint}: {e}, mencoba lagi...{Style.RESET_ALL}")
                await asyncio.sleep(2 ** attempt)
        return None

    async def wallet_login(self):
        self.log("Mencoba login ke API Aquaflux...")
        timestamp = int(time.time()) * 1000
        message = f"Sign in to AquaFlux with timestamp: {timestamp}"
        encoded_message = encode_defunct(text=message)
        signed_message = self.account.sign_message(encoded_message)
        
        payload = {
            "address": self.address,
            "message": message,
            "signature": to_hex(signed_message.signature)
        }
        
        response = await self._api_request("POST", "users/wallet-login", headers=self.headers, json=payload)
        if response and response.get("data", {}).get("accessToken"):
            self.access_token = response["data"]["accessToken"]
            self.headers['Authorization'] = f"Bearer {self.access_token}"
            self.log(f"{Fore.GREEN}Login API berhasil.{Style.RESET_ALL}")
            return True
        self.log(f"{Fore.RED}Login API gagal.{Style.RESET_ALL}")
        return False

    async def check_nft_status(self, nft_type_str):
        contract = self.web3.eth.contract(address=config.AQUAFLUX_NFT_ADDRESS, abi=config.AQUAFLUX_CONTRACT_ABI)
        if nft_type_str == "Standard":
            return contract.functions.hasClaimedStandardNFT(self.address).call()
        else: # Premium
            return contract.functions.hasClaimedPremiumNFT(self.address).call()

    async def run_nft_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS AQUAFLUX UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        
        self.web3 = self._get_web3_provider()
        if not self.web3: return
        self.nonce = self.web3.eth.get_transaction_count(self.address)
        
        if not await self.wallet_login(): return

        delay_min, delay_max = settings['delay']
        contract = self.web3.eth.contract(address=config.AQUAFLUX_NFT_ADDRESS, abi=config.AQUAFLUX_CONTRACT_ABI)

        for nft_type_int, nft_type_str in enumerate(["Standard", "Premium"]):
            self.log(f"{Style.BRIGHT}--- Memproses NFT Tipe: {nft_type_str} ---")
            
            if await self.check_nft_status(nft_type_str):
                self.log(f"{Fore.YELLOW}NFT {nft_type_str} sudah pernah di-mint.{Style.RESET_ALL}")
                continue

            # Cek eligibilitas untuk Premium
            if nft_type_str == "Premium":
                binding_status = await self._api_request("GET", "users/twitter/binding-status", headers=self.headers)
                if not binding_status or not binding_status.get("data", {}).get("bound"):
                    self.log(f"{Fore.YELLOW}Tidak eligible untuk Premium NFT (Twitter belum terhubung).{Style.RESET_ALL}")
                    continue
            
            # 1. Claim Tokens
            self.log("Step 1: Claim Tokens...")
            if not await self._execute_transaction(contract.functions.claimTokens()):
                continue # Gagal, lanjut ke iterasi berikutnya jika ada
            await asyncio.sleep(random.uniform(delay_min, delay_max))

            # 2. Combine Tokens
            self.log("Step 2: Combine Tokens...")
            holding_status = await self._api_request("POST", "users/check-token-holding", headers=self.headers)
            if holding_status and not holding_status.get("data", {}).get("isHoldingToken"):
                combine_func = random.choice([contract.functions.combineCS, contract.functions.combinePC, contract.functions.combinePS])
                self.log(f"Melakukan combine dengan {combine_func.fn_name}...")
                if not await self._execute_transaction(combine_func(self.web3.to_wei(100, "ether"))):
                    continue
                await asyncio.sleep(random.uniform(delay_min, delay_max))
            else:
                self.log(f"{Fore.GREEN}Combine tidak diperlukan atau sudah dilakukan.{Style.RESET_ALL}")

            # 3. Mint NFT
            self.log("Step 3: Mint NFT...")
            signature_data = await self._api_request("POST", "users/get-signature", headers=self.headers, json={"walletAddress": self.address, "requestedNftType": nft_type_int})
            if not signature_data or "data" not in signature_data:
                self.log(f"{Fore.RED}Gagal mendapatkan signature dari API.{Style.RESET_ALL}")
                continue
            
            expires_at = signature_data["data"]["expiresAt"]
            signature = signature_data["data"]["signature"]
            mint_func = contract.functions.mint(nft_type_int, expires_at, signature)
            await self._execute_transaction(mint_func)
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        
        self.log(f"{Fore.MAGENTA}--- SIKLUS AQUAFLUX UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")