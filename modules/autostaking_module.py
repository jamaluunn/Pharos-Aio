# modules/autostaking_module.py (MODUL BARU)
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from web3 import Web3
from eth_account import Account
from colorama import *
import asyncio, json, time, random, pytz, re
from datetime import datetime
from base64 import b64encode
import config
import aiohttp
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent

wib = pytz.timezone('Asia/Jakarta')

class AutostakingModule:
    def __init__(self, private_key: str, proxy: str = None):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy
        self.web3 = None
        self.nonce = None
        self.auth_token = None
        self.headers = {**config.AUTOSTAKING_HEADERS, "User-Agent": FakeUserAgent().random}

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    # --- BAGIAN HELPER YANG DI-STANDARDISASI (dapat di-refactor ke base class nanti) ---
    def _get_web3_provider(self, retries=3):
        request_kwargs = {"timeout": 60}
        if self.proxy: request_kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}
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

    async def _execute_transaction(self, tx_data, value_wei=0):
        try:
            tx = tx_data.build_transaction({'from': self.address, 'value': value_wei, 'nonce': self.nonce})
            tx['gas'] = await asyncio.to_thread(self.web3.eth.estimate_gas, tx)
            tx.update({'maxFeePerGas': self.web3.to_wei('1.5', 'gwei'), 'maxPriorityFeePerGas': self.web3.to_wei('1', 'gwei')})
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = await asyncio.to_thread(self.web3.eth.send_raw_transaction, signed_tx.raw_transaction)
            self.log(f"Transaksi dikirim, menunggu konfirmasi... Hash: {tx_hash.hex()}")
            receipt = await asyncio.to_thread(self.web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            if receipt.status == 1:
                self.log(f"{Fore.GREEN}Transaksi sukses! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                self.nonce += 1
                return receipt
            else:
                self.log(f"{Fore.RED}Transaksi gagal! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat eksekusi transaksi: {e}{Style.RESET_ALL}")
            return None
            
    # --- LOGIKA SPESIFIK AUTOSTAKING ---
    
    def _generate_auth_token(self):
        try:
            public_key = serialization.load_pem_public_key(config.AUTOSTAKING_PUBLIC_KEY_PEM)
            ciphertext = public_key.encrypt(
                self.address.encode('utf-8'),
                padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
            )
            return b64encode(ciphertext).decode('utf-8')
        except Exception as e:
            self.log(f"{Fore.RED}Gagal membuat token otentikasi: {e}{Style.RESET_ALL}")
            return None

    async def _api_post_request(self, endpoint, payload):
        url = f"{config.AUTOSTAKING_BASE_API}/{endpoint}"
        connector, proxy_url, proxy_auth = self._build_proxy_config()
        headers = {**self.headers, 'Authorization': self.auth_token}
        for attempt in range(5):
            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(url, json=payload, headers=headers, proxy=proxy_url, proxy_auth=proxy_auth, timeout=60) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as e:
                self.log(f"{Fore.YELLOW}Error request API ke {endpoint}: {e}, mencoba lagi...{Style.RESET_ALL}")
                await asyncio.sleep(3)
        return None

    async def _approve_token(self, token_address, amount):
        token_contract = self.web3.eth.contract(address=token_address, abi=config.STANDARD_ERC20_ABI)
        decimals = await asyncio.to_thread(token_contract.functions.decimals().call)
        amount_in_wei = int(amount * (10**decimals))
        allowance = await asyncio.to_thread(token_contract.functions.allowance(self.address, config.AUTOSTAKING_ROUTER_ADDRESS).call)
        if allowance >= amount_in_wei:
            self.log(f"{Fore.GREEN}Approval untuk {token_address[-6:]}.. sudah cukup.{Style.RESET_ALL}")
            return True
        self.log(f"Melakukan approval untuk {amount} token di {token_address[-6:]}..")
        approve_data = token_contract.functions.approve(config.AUTOSTAKING_ROUTER_ADDRESS, 2**256 - 1)
        return await self._execute_transaction(approve_data) is not None

    async def claim_faucet(self):
        self.log("Memeriksa faucet Autostaking...")
        contract = self.web3.eth.contract(address=config.AUTOSTAKING_MVMUSD_ADDRESS, abi=config.AUTOSTAKING_FAUCET_ABI)
        next_claim_time = await asyncio.to_thread(contract.functions.getNextFaucetClaimTime(self.address).call)
        if int(time.time()) >= next_claim_time:
            self.log("Faucet tersedia, mencoba klaim...")
            claim_data = contract.functions.claimFaucet()
            await self._execute_transaction(claim_data)
        else:
            claim_time_str = datetime.fromtimestamp(next_claim_time, wib).strftime('%Y-%m-%d %H:%M:%S')
            self.log(f"{Fore.YELLOW}Faucet sudah diklaim. Klaim berikutnya pada: {claim_time_str}{Style.RESET_ALL}")

    async def run_staking_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS AUTOSTAKING UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        self.web3 = self._get_web3_provider()
        if not self.web3: return
        self.nonce = self.web3.eth.get_transaction_count(self.address)
        
        self.auth_token = self._generate_auth_token()
        if not self.auth_token: return

        await self.claim_faucet()
        await asyncio.sleep(random.uniform(5, 10))

        staking_count = random.randint(settings['staking_count'][0], settings['staking_count'][1])
        for i in range(staking_count):
            self.log(f"{Style.BRIGHT}--- Staking ke-{i+1}/{staking_count} ---")
            
            # 1. Get Recommendation
            rec_payload = {"user": self.address, "profile": config.AUTOSTAKING_PROMPT, "userPositions": [], 
                           "userAssets": [], "chainIds": [688688], "tokens": ["USDC", "USDT", "MockUSD"], 
                           "protocols": ["MockVault"], "env": "pharos"}
            recommendation = await self._api_post_request("investment/financial-portfolio-recommendation", rec_payload)
            if not recommendation or not recommendation.get("data", {}).get("changes"):
                self.log(f"{Fore.RED}Gagal mendapatkan rekomendasi portofolio.{Style.RESET_ALL}"); continue
            
            # 2. Get Transaction Data
            changes = recommendation["data"]["changes"]
            tx_payload = {"user": self.address, "changes": changes, "prevTransactionResults": {}}
            tx_data_response = await self._api_post_request("investment/generate-change-transactions", tx_payload)
            if not tx_data_response or "data" not in tx_data_response.get("data", {}).get("688688", {}):
                self.log(f"{Fore.RED}Gagal mendapatkan calldata transaksi.{Style.RESET_ALL}"); continue

            calldata = tx_data_response["data"]["688688"]["data"]
            
            # 3. Approve Tokens
            usdc_amt = float(settings['usdc_amount'][0] + settings['usdc_amount'][1]) / 2
            usdt_amt = float(settings['usdt_amount'][0] + settings['usdt_amount'][1]) / 2
            musd_amt = float(settings['musd_amount'][0] + settings['musd_amount'][1]) / 2

            if not await self._approve_token(config.AUTOSTAKING_USDC_ADDRESS, usdc_amt): continue
            if not await self._approve_token(config.AUTOSTAKING_USDT_ADDRESS, usdt_amt): continue
            if not await self._approve_token(config.AUTOSTAKING_MUSD_ADDRESS, musd_amt): continue

            # 4. Execute Staking
            self.log("Melakukan eksekusi transaksi staking yang direkomendasikan...")
            tx = {'to': config.AUTOSTAKING_ROUTER_ADDRESS, 'data': calldata}
            # Kita tidak perlu build_transaction di sini karena _send_raw_transaction... sudah menanganinya
            tx_hash_bytes = await self._send_raw_transaction_with_retries(tx)
            if tx_hash_bytes:
                if await self._wait_for_receipt_with_retries(tx_hash_bytes):
                    self.nonce += 1 # Manual increment karena tx ini tidak lewat _execute_transaction
            
            if i < staking_count - 1:
                delay = random.uniform(settings['delay'][0], settings['delay'][1])
                self.log(f"Jeda {delay:.2f} detik...")
                await asyncio.sleep(delay)
                
        self.log(f"{Fore.MAGENTA}--- SIKLUS AUTOSTAKING UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")