# modules/pharos_module.py

from web3 import Web3
from eth_account import Account
from colorama import *
import asyncio, json, time, random, pytz
from datetime import datetime
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

    def _get_default_headers(self):
        return {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.pharosnetwork.xyz",
            "Referer": "https://testnet.pharosnetwork.xyz/",
            "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }

    def _get_web3_provider(self):
        request_kwargs = {"timeout": 60}
        if self.proxy:
            request_kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}
        return Web3(Web3.HTTPProvider(config.RPC_URL, request_kwargs=request_kwargs))

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    def generate_signature(self):
        from eth_account.messages import encode_defunct
        encoded_message = encode_defunct(text="pharos")
        signed_message = self.account.sign_message(encoded_message)
        return signed_message.signature.hex()

    async def _send_transaction(self, tx):
        try:
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.log(f"Transaksi dikirim, menunggu konfirmasi... Hash: {tx_hash.hex()}")
            receipt = await asyncio.to_thread(self.web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            
            if receipt.status == 1:
                self.log(f"{Fore.GREEN}Transaksi sukses! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                return tx_hash
            else:
                self.log(f"{Fore.RED}Transaksi gagal! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat mengirim transaksi: {e}{Style.RESET_ALL}")
            return None
            
    async def get_token_balance(self, contract_address: str):
        try:
            if contract_address.upper() == "PHRS":
                balance = self.web3.eth.get_balance(self.address)
                return self.web3.from_wei(balance, 'ether')
            else:
                token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(contract_address), abi=config.PHAROS_ERC20_ABI)
                balance = token_contract.functions.balanceOf(self.address).call()
                decimals = token_contract.functions.decimals().call()
                return balance / (10 ** decimals)
        except Exception as e:
            self.log(f"{Fore.RED}Gagal mendapatkan balance: {e}{Style.RESET_ALL}")
            return 0
            
    async def user_login(self):
        signature = self.generate_signature()
        url = f"{config.PHAROS_API_URL}/user/login?address={self.address}&signature={signature}&invite_code={config.PHAROS_REF_CODE}"
        headers = {**self.headers, "Authorization": "Bearer null", "Content-Length": "0"}
        connector = ProxyConnector.from_url(self.proxy) if self.proxy else None
        async with ClientSession(connector=connector) as session:
            try:
                async with session.post(url, headers=headers) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data.get("code") == 0:
                        self.access_token = data["data"]["jwt"]
                        self.headers["Authorization"] = f"Bearer {self.access_token}"
                        self.log(f"{Fore.GREEN}Login berhasil.{Style.RESET_ALL}")
                        return True
                    self.log(f"{Fore.YELLOW}Login gagal: {data.get('msg')}{Style.RESET_ALL}")
                    return False
            except Exception as e:
                self.log(f"{Fore.RED}Error saat login: {e}{Style.RESET_ALL}")
                return False

    async def check_in(self):
        if not self.access_token: await self.user_login()
        if not self.access_token: return
        url = f"{config.PHAROS_API_URL}/sign/in?address={self.address}"
        connector = ProxyConnector.from_url(self.proxy) if self.proxy else None
        async with ClientSession(connector=connector) as session:
            try:
                async with session.post(url, headers=self.headers) as response:
                    data = await response.json()
                    if data.get('msg') == 'ok': self.log(f"{Fore.GREEN}Check-in Harian: Berhasil.{Style.RESET_ALL}")
                    elif "already signed in" in data.get('msg', ''): self.log(f"{Fore.YELLOW}Check-in Harian: Sudah dilakukan hari ini.{Style.RESET_ALL}")
                    else: self.log(f"{Fore.RED}Check-in Harian: Gagal - {data.get('msg')}{Style.RESET_ALL}")
            except Exception as e: self.log(f"{Fore.RED}Error saat check-in: {e}{Style.RESET_ALL}")

    async def claim_faucet(self):
        if not self.access_token: await self.user_login()
        if not self.access_token: return
        status_url = f"{config.PHAROS_API_URL}/faucet/status?address={self.address}"
        connector = ProxyConnector.from_url(self.proxy) if self.proxy else None
        async with ClientSession(connector=connector) as session:
            try:
                async with session.get(status_url, headers=self.headers) as response:
                    status_data = await response.json()
                    if not status_data.get("data", {}).get("is_able_to_faucet"):
                        self.log(f"{Fore.YELLOW}Faucet: Belum waktunya untuk klaim.{Style.RESET_ALL}")
                        return
                claim_url = f"{config.PHAROS_API_URL}/faucet/daily?address={self.address}"
                async with session.post(claim_url, headers=self.headers) as response:
                    claim_data = await response.json()
                    if claim_data.get('msg') == 'ok': self.log(f"{Fore.GREEN}Faucet: Klaim 0.2 PHRS berhasil.{Style.RESET_ALL}")
                    else: self.log(f"{Fore.RED}Faucet: Gagal klaim - {claim_data.get('msg')}{Style.RESET_ALL}")
            except Exception as e: self.log(f"{Fore.RED}Error saat klaim faucet: {e}{Style.RESET_ALL}")
                
    async def approve_token(self, spender_address, token_address, amount):
        self.log(f"Memeriksa approval untuk token {token_address}...")
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=config.PHAROS_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10**decimals))
        allowance = token_contract.functions.allowance(self.address, spender_address).call()
        if allowance >= amount_in_wei:
            self.log(f"{Fore.GREEN}Approval sudah cukup.{Style.RESET_ALL}")
            return True
        self.log(f"Melakukan approval untuk {amount} token...")
        approve_tx_data = token_contract.functions.approve(spender_address, 2**256 - 1)
        tx = approve_tx_data.build_transaction({"from": self.address,"gas": approve_tx_data.estimate_gas({"from": self.address}),"gasPrice": self.web3.eth.gas_price,"nonce": self.web3.eth.get_transaction_count(self.address),"chainId": self.web3.eth.chain_id})
        tx_hash = await self._send_transaction(tx)
        await asyncio.sleep(5) 
        return tx_hash is not None

    async def wrap_phrs(self, amount: float):
        self.log(f"Wrapping {amount} PHRS menjadi WPHRS...")
        wphrs_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.PHAROS_WPHRS_CONTRACT_ADDRESS), abi=config.PHAROS_ERC20_ABI)
        tx_data = wphrs_contract.functions.deposit()
        tx = tx_data.build_transaction({"from": self.address,"value": self.web3.to_wei(amount, 'ether'),"gas": tx_data.estimate_gas({"from": self.address, "value": self.web3.to_wei(amount, 'ether')}),"gasPrice": self.web3.eth.gas_price,"nonce": self.web3.eth.get_transaction_count(self.address),"chainId": self.web3.eth.chain_id})
        await self._send_transaction(tx)

    async def swap(self, from_token_addr: str, to_token_addr: str, amount: float):
        from_ticker = "WPHRS" if from_token_addr == config.PHAROS_WPHRS_CONTRACT_ADDRESS else "USDC" if from_token_addr == config.PHAROS_USDC_CONTRACT_ADDRESS else "USDT"
        to_ticker = "WPHRS" if to_token_addr == config.PHAROS_WPHRS_CONTRACT_ADDRESS else "USDC" if to_token_addr == config.PHAROS_USDC_CONTRACT_ADDRESS else "USDT"
        self.log(f"Menyiapkan swap {amount} {from_ticker} -> {to_ticker}...")
        
        if await self.get_token_balance(from_token_addr) < amount:
            self.log(f"{Fore.YELLOW}Balance {from_ticker} tidak cukup untuk swap. Skip.{Style.RESET_ALL}")
            return

        approved = await self.approve_token(config.PHAROS_SWAP_ROUTER_ADDRESS, from_token_addr, amount)
        if not approved:
            self.log(f"{Fore.RED}Gagal approve token, swap dibatalkan.{Style.RESET_ALL}")
            return

        swap_router_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.PHAROS_SWAP_ROUTER_ADDRESS), abi=config.PHAROS_SWAP_ABI)
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(from_token_addr), abi=config.PHAROS_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10**decimals))
        from eth_abi.abi import encode
        encoded_data = encode(["address","address","uint24","address","uint256","uint256","uint256",],[self.web3.to_checksum_address(from_token_addr),self.web3.to_checksum_address(to_token_addr),500,self.address,amount_in_wei,0,0,])
        multicall_data = [b'\x04\xe4\x5a\xaf' + encoded_data]
        tx_data = swap_router_contract.functions.multicall(int(time.time()) + 300, multicall_data)
        tx = tx_data.build_transaction({"from":self.address,"gas":tx_data.estimate_gas({"from":self.address}),"gasPrice":self.web3.eth.gas_price,"nonce":self.web3.eth.get_transaction_count(self.address),"chainId":self.web3.eth.chain_id,})
        await self._send_transaction(tx)

    async def add_liquidity(self, token_a_addr, token_b_addr, amount_a, amount_b):
        """ 
        <<<< PERBAIKAN DI SINI >>>>
        Fungsi ini sekarang mengurutkan token secara otomatis sebelum membuat transaksi.
        """
        addr_a = self.web3.to_checksum_address(token_a_addr)
        addr_b = self.web3.to_checksum_address(token_b_addr)

        # Mengurutkan token berdasarkan alamat kontrak
        if addr_a < addr_b:
            token0_addr, token1_addr = addr_a, addr_b
            amount0, amount1 = amount_a, amount_b
        else:
            token0_addr, token1_addr = addr_b, addr_a
            amount0, amount1 = amount_b, amount_a

        self.log(f"Menambahkan likuiditas untuk pair: {token0_addr} & {token1_addr}")

        if await self.get_token_balance(token0_addr) < amount0 or await self.get_token_balance(token1_addr) < amount1:
            self.log(f"{Fore.YELLOW}Balance untuk Add LP tidak cukup. Skip.{Style.RESET_ALL}")
            return
            
        approved0 = await self.approve_token(config.PHAROS_POTITION_MANAGER_ADDRESS, token0_addr, amount0)
        approved1 = await self.approve_token(config.PHAROS_POTITION_MANAGER_ADDRESS, token1_addr, amount1)
        if not (approved0 and approved1):
            self.log(f"{Fore.RED}Gagal approve, Add LP dibatalkan.{Style.RESET_ALL}")
            return

        manager_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.PHAROS_POTITION_MANAGER_ADDRESS), abi=config.PHAROS_ADD_LP_ABI)
        
        token0_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token0_addr), abi=config.PHAROS_ERC20_ABI)
        amount0_desired = int(amount0 * (10 ** token0_contract.functions.decimals().call()))
        
        token1_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token1_addr), abi=config.PHAROS_ERC20_ABI)
        amount1_desired = int(amount1 * (10 ** token1_contract.functions.decimals().call()))
        
        mint_params = {"token0":token0_addr,"token1":token1_addr,"fee":500,"tickLower":-887270,"tickUpper":887270,"amount0Desired":amount0_desired,"amount1Desired":amount1_desired,"amount0Min":0,"amount1Min":0,"recipient":self.address,"deadline":int(time.time())+600}
        
        tx_data = manager_contract.functions.mint(mint_params)
        tx = tx_data.build_transaction({"from":self.address,"gas":tx_data.estimate_gas({"from":self.address}),"gasPrice":self.web3.eth.gas_price,"nonce":self.web3.eth.get_transaction_count(self.address),"chainId":self.web3.eth.chain_id,})
        await self._send_transaction(tx)

    async def run_full_interaction_task(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI INTERAKSI PHAROS UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']
        
        self.log(f"{Style.BRIGHT}Langkah 1: Check-in & Faucet...{Style.RESET_ALL}")
        if await self.user_login():
            await self.check_in()
            await asyncio.sleep(2)
            await self.claim_faucet()
        await asyncio.sleep(random.uniform(delay_min, delay_max))

        self.log(f"{Style.BRIGHT}Langkah 2: Wrap PHRS...{Style.RESET_ALL}")
        if await self.get_token_balance("PHRS") > settings['wrap_amount']:
            await self.wrap_phrs(settings['wrap_amount'])
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        else:
            self.log(f"{Fore.YELLOW}Balance PHRS tidak cukup untuk wrap.{Style.RESET_ALL}")

        self.log(f"{Style.BRIGHT}Langkah 3: Melakukan {settings['swap_count']} kali Swap...{Style.RESET_ALL}")
        for i in range(settings['swap_count']):
            self.log(f"--- Swap ke-{i+1}/{settings['swap_count']} ---")
            await self.swap(config.PHAROS_WPHRS_CONTRACT_ADDRESS, config.PHAROS_USDC_CONTRACT_ADDRESS, settings['swap_wphrs_usdc_amount'])
            await asyncio.sleep(random.uniform(delay_min, delay_max))
            await self.swap(config.PHAROS_USDC_CONTRACT_ADDRESS, config.PHAROS_WPHRS_CONTRACT_ADDRESS, settings['swap_usdc_wphrs_amount'])
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        self.log(f"{Style.BRIGHT}Langkah 4: Melakukan {settings['lp_count']} kali Add Liquidity...{Style.RESET_ALL}")
        for i in range(settings['lp_count']):
            self.log(f"--- Add LP ke-{i+1}/{settings['lp_count']} ---")
            await self.add_liquidity(config.PHAROS_WPHRS_CONTRACT_ADDRESS, config.PHAROS_USDC_CONTRACT_ADDRESS, settings['lp_amount_wphrs'], settings['lp_amount_usdc'])
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        
        self.log(f"{Fore.MAGENTA}--- SEMUA INTERAKSI PHAROS UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")
