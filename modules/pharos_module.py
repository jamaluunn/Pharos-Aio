# modules/pharos_module.py (Updated to Latest Version)
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from colorama import *
import asyncio, json, time, random, pytz
from datetime import datetime, timezone
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
import config

wib = pytz.timezone('Asia/Jakarta')

class PharosModule:
    def __init__(self, private_key: str, proxy: str = None):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy
        self.web3 = self._get_web3_provider()
        self.access_token = None
        self.headers = self._get_default_headers()
        self.nonce = None # Untuk manajemen nonce manual

    def _get_default_headers(self):
        return {"Accept":"application/json, text/plain, */*","Accept-Language":"id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7","Origin":"https://testnet.pharosnetwork.xyz","Referer":"https://testnet.pharosnetwork.xyz/","User-Agent":FakeUserAgent().random}
    
    def _get_web3_provider(self):
        # Menggunakan RPC acak dari config untuk stabilitas
        rpc_url = random.choice(config.RPC_URLS)
        request_kwargs={"timeout":60}
        if self.proxy: request_kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}
        return Web3(Web3.HTTPProvider(rpc_url, request_kwargs=request_kwargs))

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    async def _send_transaction(self, tx):
        try:
            # Manajemen nonce manual
            if self.nonce is None:
                self.nonce = self.web3.eth.get_transaction_count(self.address)
            tx['nonce'] = self.nonce
            
            if 'chainId' not in tx: tx['chainId'] = self.web3.eth.chain_id
            if 'maxFeePerGas' not in tx: tx['maxFeePerGas'] = self.web3.to_wei('1.5', 'gwei')
            if 'maxPriorityFeePerGas' not in tx: tx['maxPriorityFeePerGas'] = self.web3.to_wei('1', 'gwei')
            if 'gas' not in tx: tx['gas'] = self.web3.eth.estimate_gas(tx)

            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.log(f"Transaksi dikirim, menunggu konfirmasi... Hash: {tx_hash.hex()}")
            receipt = await asyncio.to_thread(self.web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            
            if receipt.status == 1:
                self.log(f"{Fore.GREEN}Transaksi sukses! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                self.nonce += 1 # Naikkan nonce jika sukses
                return tx_hash.hex()
            else:
                self.log(f"{Fore.RED}Transaksi gagal! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                self.nonce = None # Reset nonce jika gagal agar disinkronkan ulang
                return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat mengirim transaksi: {e}{Style.RESET_ALL}")
            self.nonce = None # Reset nonce jika ada error
            return None

    def _generate_login_payload(self):
        """Membangun payload SIWE untuk login."""
        nonce = self.web3.eth.get_transaction_count(self.address)
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        message = f"testnet.pharosnetwork.xyz wants you to sign in with your Ethereum account:\n{self.address}\n\nI accept the Pharos Terms of Service: testnet.pharosnetwork.xyz/privacy-policy/Pharos-PrivacyPolicy.pdf\n\nURI: https://testnet.pharosnetwork.xyz\n\nVersion: 1\n\nChain ID: 688688\n\nNonce: {nonce}\n\nIssued At: {timestamp}"
        
        encoded_message = encode_defunct(text=message)
        signed_message = self.account.sign_message(encoded_message)
        signature = signed_message.signature.hex()

        return {
            "address": self.address,
            "signature": signature,
            "wallet": "OKX Wallet",
            "nonce": str(nonce),
            "chain_id": "688688",
            "timestamp": timestamp,
            "domain": "testnet.pharosnetwork.xyz",
            "invite_code": config.PHAROS_REF_CODE
        }

    async def user_login(self):
        """Login menggunakan metode POST dengan payload SIWE."""
        url = f"{config.PHAROS_API_URL}/user/login"
        payload = self._generate_login_payload()
        headers = {**self.headers, "Authorization": "Bearer null"}
        try:
            connector = ProxyConnector.from_url(self.proxy) if self.proxy else None
            async with ClientSession(connector=connector) as session:
                async with session.post(url, headers=headers, json=payload, timeout=20) as response:
                    data = await response.json()
                    if response.status == 200 and data.get("code") == 0:
                        self.access_token = data["data"]["jwt"]
                        self.headers["Authorization"] = f"Bearer {self.access_token}"
                        self.log(f"{Fore.GREEN}Login berhasil.{Style.RESET_ALL}")
                        return True
                    else:
                        self.log(f"{Fore.YELLOW}Login gagal: {data.get('msg')}{Style.RESET_ALL}")
                        return False
        except Exception as e:
            self.log(f"{Fore.RED}Error saat login: {e}{Style.RESET_ALL}"); return False
            
    async def display_user_profile(self):
        # ... (fungsi ini sudah stabil, tidak perlu diubah lagi)
        self.log(f"Mencoba mengambil info Poin Pharos...")
        url = f"https://api.pharos.fi/api/user/point?address={self.address}"
        try:
            connector = ProxyConnector.from_url(self.proxy) if self.proxy else None
            async with ClientSession(connector=connector) as session:
                async with session.get(url, headers=self.headers, timeout=20) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("code") == 0 and data.get("data"):
                            user_data = data["data"]
                            points = user_data.get("points", "N/A")
                            rank = user_data.get("rank", "N/A")
                            self.log(f"{Fore.GREEN+Style.BRIGHT}================ INFO AKUN ================{Style.RESET_ALL}")
                            self.log(f"{Fore.GREEN+Style.BRIGHT} Poin Total: {points} | Peringkat: {rank}{Style.RESET_ALL}")
                            self.log(f"{Fore.GREEN+Style.BRIGHT}=========================================={Style.RESET_ALL}")
                        else:
                            self.log(f"{Fore.YELLOW}Gagal mendapatkan data: {data.get('msg', 'Format respons tidak dikenal')}{Style.RESET_ALL}")
                    # Jika endpoint .fi gagal, kembali ke metode lama yang stabil
                    else:
                        await self.user_login() # Butuh login untuk endpoint lama
                        url_fallback = f"{config.PHAROS_API_URL}/user/profile?address={self.address}"
                        async with session.get(url_fallback, headers=self.headers, timeout=20) as fallback_response:
                            fallback_data = await fallback_response.json()
                            points = fallback_data.get("data", {}).get("user_info", {}).get("TotalPoints", "N/A")
                            self.log(f"{Fore.GREEN+Style.BRIGHT}================ INFO AKUN ================{Style.RESET_ALL}")
                            self.log(f"{Fore.GREEN+Style.BRIGHT} Poin Total: {points} (Rank tidak tersedia){Style.RESET_ALL}")
                            self.log(f"{Fore.GREEN+Style.BRIGHT}=========================================={Style.RESET_ALL}")
        except Exception as e:
            self.log(f"{Fore.RED}Error saat mengambil profil pengguna: {e}{Style.RESET_ALL}")


    async def check_in_and_faucet(self):
        if not self.access_token:
            if not await self.user_login(): return

        # Check-in
        self.log("Memeriksa status check-in harian...")
        try:
            async with ClientSession(connector=ProxyConnector.from_url(self.proxy) if self.proxy else None) as session:
                checkin_url = f"{config.PHAROS_API_URL}/sign/in"
                async with session.post(checkin_url, headers=self.headers, json={"address": self.address}) as response:
                    data = await response.json()
                    if data.get('msg') == 'ok': self.log(f"{Fore.GREEN}Check-in Harian: Berhasil.{Style.RESET_ALL}")
                    elif "already signed in" in data.get('msg', ''): self.log(f"{Fore.YELLOW}Check-in Harian: Sudah dilakukan.{Style.RESET_ALL}")
                    else: self.log(f"{Fore.RED}Check-in Harian: Gagal - {data.get('msg')}{Style.RESET_ALL}")
        except Exception as e: self.log(f"{Fore.RED}Error saat check-in: {e}{Style.RESET_ALL}")
        await asyncio.sleep(random.uniform(2, 4))

        # Faucet
        self.log("Memeriksa status faucet...")
        try:
            async with ClientSession(connector=ProxyConnector.from_url(self.proxy) if self.proxy else None) as session:
                status_url = f"{config.PHAROS_API_URL}/faucet/status?address={self.address}"
                async with session.get(status_url, headers=self.headers) as response:
                    status_data = await response.json()
                    if not status_data.get("data", {}).get("is_able_to_faucet"):
                        self.log(f"{Fore.YELLOW}Faucet: Belum waktunya untuk klaim.{Style.RESET_ALL}"); return
                
                self.log("Mencoba klaim faucet...")
                claim_url = f"{config.PHAROS_API_URL}/faucet/daily"
                async with session.post(claim_url, headers=self.headers, json={"address": self.address}) as response:
                    claim_data = await response.json()
                    if claim_data.get('msg') == 'ok': self.log(f"{Fore.GREEN}Faucet: Klaim 0.2 PHRS berhasil.{Style.RESET_ALL}")
                    else: self.log(f"{Fore.RED}Faucet: Gagal klaim - {claim_data.get('msg')}{Style.RESET_ALL}")
        except Exception as e: self.log(f"{Fore.RED}Error saat klaim faucet: {e}{Style.RESET_ALL}")
    
    # Fungsi lainnya (approve, wrap, swap, LP, etc.) tetap sama tapi akan memanggil _send_transaction yang baru
    # Pastikan tidak ada lagi parameter "gasPrice" di dalamnya

    async def approve_token(self, spender_address, token_address, amount):
        self.log(f"Memeriksa approval untuk token {token_address[-6:]}...")
        spender = self.web3.to_checksum_address(spender_address)
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=config.STANDARD_ERC20_ABI)
        amount_in_wei = int(amount * (10**token_contract.functions.decimals().call()))
        if token_contract.functions.allowance(self.address, spender).call() >= amount_in_wei:
            self.log(f"{Fore.GREEN}Approval sudah cukup.{Style.RESET_ALL}"); return True
        self.log(f"Melakukan approval untuk {amount} token...")
        approve_tx_data = token_contract.functions.approve(spender, 2**256 - 1)
        tx = approve_tx_data.build_transaction({"from": self.address})
        tx_hash = await self._send_transaction(tx)
        await asyncio.sleep(5); return tx_hash is not None

    async def wrap_phrs(self, amount: float):
        self.log(f"Wrapping {amount:.4f} PHRS menjadi WPHRS...")
        wphrs_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.PHAROS_WPHRS_CONTRACT_ADDRESS), abi=config.STANDARD_ERC20_ABI)
        tx_data = wphrs_contract.functions.deposit()
        tx = tx_data.build_transaction({"from": self.address,"value": self.web3.to_wei(amount, 'ether')})
        await self._send_transaction(tx)

    async def perform_zenith_swap(self, from_token, to_token, amount):
        self.log(f"Zenith Swap: {amount:.4f} WPHRS -> USDC...")
        from_token_addr = self.web3.to_checksum_address(from_token)
        to_token_addr = self.web3.to_checksum_address(to_token)
        if await self.get_token_balance(from_token_addr) < amount:
            self.log(f"{Fore.YELLOW}Balance tidak cukup untuk swap. Skip.{Style.RESET_ALL}"); return
        
        router_addr = self.web3.to_checksum_address(config.PHAROS_SWAP_ROUTER_ADDRESS)
        if not await self.approve_token(router_addr, from_token_addr, amount):
            self.log(f"{Fore.RED}Gagal approve, swap dibatalkan.{Style.RESET_ALL}"); return
        
        router_contract = self.web3.eth.contract(address=router_addr, abi=config.PHAROS_ZENITH_SWAP_ABI)
        from eth_abi.abi import encode
        amount_in_wei = int(amount * (10**18)) # Asumsi WPHRS 18 desimal
        encoded_data = encode(["address","address","uint256","address","uint256","uint256","uint256",],[from_token_addr,to_token_addr,500,self.address,amount_in_wei,0,0,])
        multicall_data = [b'\x04\xe4Z\xaf' + encoded_data]
        tx_data = router_contract.functions.multicall(int(time.time()) + 300, multicall_data)
        tx = tx_data.build_transaction({"from":self.address})
        await self._send_transaction(tx)
        
    async def add_liquidity(self, token_a_addr, token_b_addr, amount_a, amount_b):
        position_manager_addr = self.web3.to_checksum_address(config.PHAROS_POTITION_MANAGER_ADDRESS)
        addr_a, addr_b = self.web3.to_checksum_address(token_a_addr), self.web3.to_checksum_address(token_b_addr)
        token0_addr, token1_addr, amount0, amount1 = (addr_a, addr_b, amount_a, amount_b) if addr_a < addr_b else (addr_b, addr_a, amount_b, amount_a)
        
        if await self.get_token_balance(token0_addr) < amount0 or await self.get_token_balance(token1_addr) < amount1:
            self.log(f"{Fore.YELLOW}Balance untuk Add LP tidak cukup. Skip.{Style.RESET_ALL}"); return
        if not (await self.approve_token(position_manager_addr, token0_addr, amount0) and await self.approve_token(position_manager_addr, token1_addr, amount1)):
            self.log(f"{Fore.RED}Gagal approve, Add LP dibatalkan.{Style.RESET_ALL}"); return
        
        amount0_wei = int(amount0 * (10 ** self.web3.eth.contract(address=token0_addr, abi=config.STANDARD_ERC20_ABI).functions.decimals().call()))
        amount1_wei = int(amount1 * (10 ** self.web3.eth.contract(address=token1_addr, abi=config.STANDARD_ERC20_ABI).functions.decimals().call()))
        
        self.log(f"Membuat posisi likuiditas baru dengan {amount0:.4f} & {amount1:.4f} token...")
        position_manager_contract = self.web3.eth.contract(address=position_manager_addr, abi=config.PHAROS_POSITION_MANAGER_ABI)
        params = {'token0': token0_addr, 'token1': token1_addr, 'fee': 3000, 'tickLower': -887220, 'tickUpper': 887220, 'amount0Desired': amount0_wei, 'amount1Desired': amount1_wei, 'amount0Min': 0, 'amount1Min': 0, 'recipient': self.address, 'deadline': int(time.time()) + 20 * 60}
        tx_data = position_manager_contract.functions.mint(params)
        tx = tx_data.build_transaction({"from": self.address})
        await self._send_transaction(tx)

    async def verify_task(self, tx_hash: str, task_id: str):
        self.log(f"Mencoba verifikasi Task ID {task_id} dengan tx_hash: {tx_hash[:10]}...")
        if not self.access_token: 
            if not await self.user_login(): self.log(f"{Fore.YELLOW}Token login tidak ada, skip verifikasi.{Style.RESET_ALL}"); return False
        
        url = f"{config.PHAROS_API_URL}/task/verify"
        payload = {"address": self.address, "task_id": int(task_id), "tx_hash": tx_hash}
        for i in range(5):
            try:
                connector = ProxyConnector.from_url(self.proxy) if self.proxy else None
                async with ClientSession(connector=connector) as session:
                    async with session.post(url, headers=self.headers, json=payload) as response:
                        data = await response.json(); msg = data.get('msg', '').lower()
                        if data.get('code') == 0 and ('ok' in msg or 'successfully' in msg):
                            self.log(f"{Fore.GREEN}Verifikasi task ID {task_id} berhasil!{Style.RESET_ALL}"); return True
                        elif 'already verified' in msg:
                            self.log(f"{Fore.YELLOW}Task ID {task_id} sudah diverifikasi.{Style.RESET_ALL}"); return True
                        else: self.log(f"{Fore.YELLOW}Verifikasi gagal: {data.get('msg')}. Coba lagi...{Style.RESET_ALL}")
            except Exception as e: self.log(f"{Fore.RED}Error verifikasi: {e}. Coba lagi...{Style.RESET_ALL}")
            await asyncio.sleep(10) # Jeda lebih lama untuk verifikasi
        return False

    async def run_send_to_friends_task(self, amount: float):
        self.log(f"{Style.BRIGHT}Memulai tugas 'Send to Friends'...{Style.RESET_ALL}")
        if await self.get_token_balance("PHRS") < amount:
            self.log(f"{Fore.YELLOW}Balance PHRS tidak cukup untuk transfer.{Style.RESET_ALL}"); return
        receiver = Account.create().address
        tx = {'to': receiver,'value': self.web3.to_wei(amount, "ether"),'gas': 21000}
        tx_hash = await self._send_transaction(tx)
        if tx_hash:
            await asyncio.sleep(15)
            await self.verify_task(tx_hash, config.PHAROS_TASK_IDS['send_to_friends'])

    async def run_mint_badge_task(self):
        self.log(f"{Style.BRIGHT}Memulai tugas 'Mint Testnet Badge'...{Style.RESET_ALL}")
        if await self.get_token_balance("PHRS") < 1.0:
            self.log(f"{Fore.YELLOW}Balance tidak cukup untuk mint badge (butuh ~1 PHRS).{Style.RESET_ALL}"); return
        
        data_payload = config.PHAROS_BADGE_MINT_DATA.format(wallet_address=self.address[2:].zfill(64))
        tx = {'to': self.web3.to_checksum_address(config.PHAROS_BADGE_CONTRACT_ADDRESS),'data': data_payload,'value': self.web3.to_wei(1, 'ether')}
        await self._send_transaction(tx)

    async def run_full_interaction_task(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS PHAROS UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']
        
        await self.display_user_profile()
        await asyncio.sleep(random.uniform(delay_min, delay_max))
        
        wrap_amount = random.uniform(settings['wrap_amount'][0], settings['wrap_amount'][1])
        send_friends_count = random.randint(settings['send_friends_count'][0], settings['send_friends_count'][1])
        zenith_swap_count = random.randint(settings['zenith_swap_count'][0], settings['zenith_swap_count'][1])
        lp_count = random.randint(settings['lp_count'][0], settings['lp_count'][1])

        await self.check_in_and_faucet()
        await asyncio.sleep(random.uniform(delay_min, delay_max))

        for i in range(send_friends_count):
            self.log(f"--- Send to Friends ke-{i+1}/{send_friends_count} ---")
            amount = random.uniform(settings['send_friends_amount'][0], settings['send_friends_amount'][1])
            await self.run_send_to_friends_task(amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        if await self.get_token_balance("PHRS") > wrap_amount:
            self.log(f"{Style.BRIGHT}Melakukan Wrap PHRS...{Style.RESET_ALL}")
            await self.wrap_phrs(wrap_amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        for i in range(zenith_swap_count):
            self.log(f"--- Zenith Swap ke-{i+1}/{zenith_swap_count} ---")
            amount = random.uniform(settings['zenith_swap_amount'][0], settings['zenith_swap_amount'][1])
            await self.perform_zenith_swap(config.PHAROS_WPHRS_CONTRACT_ADDRESS, config.PHAROS_USDC_CONTRACT_ADDRESS, amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        for i in range(lp_count):
            self.log(f"--- Add/Increase LP ke-{i+1}/{lp_count} ---")
            amount_wphrs = random.uniform(settings['lp_amount_wphrs'][0], settings['lp_amount_wphrs'][1])
            amount_usdc = random.uniform(settings['lp_amount_usdc'][0], settings['lp_amount_usdc'][1])
            await self.add_liquidity(config.PHAROS_WPHRS_CONTRACT_ADDRESS, config.PHAROS_USDC_CONTRACT_ADDRESS, amount_wphrs, amount_usdc)
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        
        self.log(f"{Fore.MAGENTA}--- SEMUA INTERAKSI PHAROS UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")
