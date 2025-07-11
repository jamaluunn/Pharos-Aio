# modules/faroswap_module.py (Final Version)
from web3 import Web3
from eth_account import Account
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, json, time, os, pytz, random
import config

wib = pytz.timezone('Asia/Jakarta')

class FaroswapModule:
    def __init__(self, private_key: str, proxy: str = None):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy
        self.web3 = self._get_web3_provider()
        self.headers = self._get_default_headers()
        self.pools_data = self._load_pools()

    def _get_default_headers(self):
        return {"Accept": "application/json, text/plain, */*","Origin": "https://faroswap.xyz","Referer": "https://faroswap.xyz/","User-Agent": FakeUserAgent().random}

    def _get_web3_provider(self):
        rpc_url = random.choice(config.FAROSWAP_RPC_URLS)
        return Web3(Web3.HTTPProvider(rpc_url))

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    def _load_pools(self):
        filename = "pools.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}PENTING: File {filename} tidak ditemukan! Fitur Add LP akan gagal.{Style.RESET_ALL}")
                return None
            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list) and len(data) > 0: return data[0]
            return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat memuat {filename}: {e}{Style.RESET_ALL}"); return None

    async def _send_transaction(self, tx):
        try:
            if 'nonce' not in tx: tx['nonce'] = self.web3.eth.get_transaction_count(self.address)
            if 'chainId' not in tx: tx['chainId'] = self.web3.eth.chain_id
            if 'maxFeePerGas' not in tx: tx['maxFeePerGas'] = self.web3.to_wei('2', 'gwei')
            if 'maxPriorityFeePerGas' not in tx: tx['maxPriorityFeePerGas'] = self.web3.to_wei('1', 'gwei')
            if 'gas' not in tx: tx['gas'] = self.web3.eth.estimate_gas(tx)
            
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            self.log(f"Transaksi dikirim, menunggu konfirmasi... Hash: {tx_hash.hex()}")
            receipt = await asyncio.to_thread(self.web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            
            if receipt.status == 1:
                self.log(f"{Fore.GREEN}Transaksi sukses! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                return tx_hash.hex()
            else:
                self.log(f"{Fore.RED}Transaksi gagal! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}"); return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat mengirim transaksi: {e}{Style.RESET_ALL}"); return None

    async def approve_token(self, spender_address, token_address, amount_in_wei):
        try:
            spender = self.web3.to_checksum_address(spender_address)
            token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=config.STANDARD_ERC20_ABI)
            
            if token_contract.functions.allowance(self.address, spender).call() >= amount_in_wei: return True

            self.log(f"Approval untuk {token_address[-6:]} ke {spender[-6:]}...")
            approve_data = token_contract.functions.approve(spender, 2**256 - 1)
            tx = approve_data.build_transaction({"from": self.address, "gas": 100000})
            tx_hash = await self._send_transaction(tx)
            if tx_hash: await asyncio.sleep(5); return True
            return False
        except Exception as e:
            self.log(f"{Fore.RED}Gagal approve token: {e}{Style.RESET_ALL}"); return False
            
    async def get_token_balance(self, token_address: str):
        try:
            if token_address == config.FAROSWAP_PHRS_ADDRESS:
                return self.web3.from_wei(self.web3.eth.get_balance(self.address), 'ether')
            else:
                contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=config.STANDARD_ERC20_ABI)
                return contract.functions.balanceOf(self.address).call() / (10 ** contract.functions.decimals().call())
        except Exception as e:
            self.log(f"{Fore.RED}Gagal mendapatkan balance: {e}{Style.RESET_ALL}"); return 0

    async def get_dodo_route(self, from_token, to_token, amount_in_wei):
        url = (f"https://api.dodoex.io/route-service/v2/widget/getdodoroute?chainId=688688&deadLine={int(time.time()) + 600}"
               f"&apikey=a37546505892e1a952&slippage=3.225&source=dodoV2AndMixWasm&toTokenAddress={to_token}"
               f"&fromTokenAddress={from_token}&userAddr={self.address}&estimateGas=true&fromAmount={amount_in_wei}")
        for _ in range(3):
            try:
                connector = ProxyConnector.from_url(self.proxy) if self.proxy else None
                async with ClientSession(connector=connector) as session:
                    async with session.get(url, headers=self.headers, timeout=15) as response:
                        data = await response.json()
                        if data.get("status") == 200: return data.get("data")
                self.log(f"{Fore.YELLOW}Gagal DODO route: {data.get('data', 'No response')}. Coba lagi...{Style.RESET_ALL}"); await asyncio.sleep(3)
            except Exception as e:
                self.log(f"{Fore.RED}Error request DODO route: {e}{Style.RESET_ALL}"); await asyncio.sleep(3)
        return None

    async def perform_swap(self, from_token_addr, to_token_addr, amount):
        is_native = (from_token_addr == config.FAROSWAP_PHRS_ADDRESS)
        self.log(f"Swap: {amount:.4f} {'PHRS' if is_native else from_token_addr[-4:]} -> {to_token_addr[-4:]}...")
        
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(from_token_addr), abi=config.STANDARD_ERC20_ABI)
        decimals = 18 if is_native else token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10**decimals))
        
        route = await self.get_dodo_route(from_token_addr, to_token_addr, amount_in_wei)
        if not route: return

        router_address = self.web3.to_checksum_address(config.FAROSWAP_MIXSWAP_ROUTER_ADDRESS)
        if not is_native:
            if not await self.approve_token(router_address, from_token_addr, amount_in_wei): return

        tx = {
            "to": router_address, 
            "from": self.address, 
            "value": int(route.get("value")), 
            "data": route.get("data"),
        }
        await self._send_transaction(tx)

    async def add_dvm_liquidity(self, base_token_addr, quote_token_addr, amount):
        if not self.pools_data:
            self.log(f"{Fore.RED}Data pool dari pools.json tidak tersedia. Skip Add LP.{Style.RESET_ALL}"); return
        
        pair_key = "USDC_USDT" if base_token_addr == config.FAROSWAP_USDC_ADDRESS else "USDT_USDC"
        dvm_address_str = self.pools_data.get(pair_key)
        if not dvm_address_str:
            self.log(f"{Fore.RED}Alamat pool untuk {pair_key} tidak ditemukan di pools.json. Skip.{Style.RESET_ALL}"); return
            
        self.log(f"Add DVM Liquidity ke Pool {dvm_address_str[-6:]}...")
        
        amount_wei = int(amount * (10**6))
        min_amount = int(amount_wei * 0.98) 
        deadline = int(time.time()) + 600

        if not await self.approve_token(config.FAROSWAP_POOL_ROUTER_ADDRESS, base_token_addr, amount_wei): return
        if not await self.approve_token(config.FAROSWAP_POOL_ROUTER_ADDRESS, quote_token_addr, amount_wei): return
        
        dvm_router_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.FAROSWAP_DVM_ROUTER_ADDRESS), abi=config.FAROSWAP_DVM_POOL_ABI)
        tx_data = dvm_router_contract.functions.addDVMLiquidity(self.web3.to_checksum_address(dvm_address_str), amount_wei, amount_wei, min_amount, min_amount, 0, deadline)
        tx = tx_data.build_transaction({"from": self.address})
        await self._send_transaction(tx)

    async def run_full_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS PENUH FAROSWAP ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']
        
        deposit_amount = random.uniform(settings['deposit_amount'][0], settings['deposit_amount'][1])
        swap_count = random.randint(settings['swap_count'][0], settings['swap_count'][1])
        lp_count = random.randint(settings['lp_count'][0], settings['lp_count'][1])

        phrs_balance = await self.get_token_balance(config.FAROSWAP_PHRS_ADDRESS)
        if phrs_balance > deposit_amount:
            self.log(f"Memulai deposit (wrap) {deposit_amount:.4f} PHRS...")
            wphrs_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.FAROSWAP_WPHRS_ADDRESS), abi=config.STANDARD_ERC20_ABI)
            tx_data = wphrs_contract.functions.deposit()
            tx = tx_data.build_transaction({"from": self.address, "value": self.web3.to_wei(deposit_amount, 'ether'), "gas": 100000})
            await self._send_transaction(tx)
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        else:
            self.log(f"{Fore.YELLOW}Balance PHRS tidak cukup untuk deposit. Skip.{Style.RESET_ALL}")

        for i in range(swap_count):
            self.log(f"{Style.BRIGHT}--- Swap ke-{i+1}/{swap_count} ---")
            swap_amount = random.uniform(settings['swap_amount'][0], settings['swap_amount'][1])
            tokens = {"WPHRS": config.FAROSWAP_WPHRS_ADDRESS, "USDC": config.FAROSWAP_USDC_ADDRESS, "USDT": config.FAROSWAP_USDT_ADDRESS, "PHRS": config.FAROSWAP_PHRS_ADDRESS}
            from_t, to_t = random.sample(list(tokens.keys()), 2)
            
            if (from_t == "WPHRS" and to_t == "PHRS") or (from_t == "PHRS" and to_t == "WPHRS"): continue

            balance = await self.get_token_balance(tokens[from_t])
            if balance > swap_amount:
                await self.perform_swap(tokens[from_t], tokens[to_t], swap_amount)
            else: 
                self.log(f"{Fore.YELLOW}Balance {from_t} ({balance:.4f}) tidak cukup untuk swap ({swap_amount:.4f}).{Style.RESET_ALL}")
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        for i in range(lp_count):
            self.log(f"{Style.BRIGHT}--- Add DVM LP ke-{i+1}/{lp_count} ---")
            lp_amount = random.uniform(settings['lp_amount'][0], settings['lp_amount'][1])
            base_addr, quote_addr = random.sample([config.FAROSWAP_USDC_ADDRESS, config.FAROSWAP_USDT_ADDRESS], 2)
            
            balance = await self.get_token_balance(base_addr)
            if balance > lp_amount: 
                await self.add_dvm_liquidity(base_addr, quote_addr, lp_amount)
            else: 
                self.log(f"{Fore.YELLOW}Balance token tidak cukup untuk LP ({lp_amount:.4f}). Skip.{Style.RESET_ALL}")
            await asyncio.sleep(random.uniform(delay_min, delay_max))
            
        self.log(f"{Fore.MAGENTA}--- SIKLUS FAROSWAP SELESAI ---{Style.RESET_ALL}")