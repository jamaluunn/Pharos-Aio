# modules/openfi_module.py

from web3 import Web3
from eth_account import Account
from colorama import *
import asyncio, json, time, random, pytz
from datetime import datetime
import config

wib = pytz.timezone('Asia/Jakarta')

class OpenFiModule:
    def __init__(self, private_key: str, proxy: str = None):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy
        self.web3 = self._get_web3_provider()

    def _get_web3_provider(self):
        request_kwargs = {"timeout": 60}
        if self.proxy:
            request_kwargs["proxies"] = {"http": self.proxy, "https": self.proxy}
        return Web3(Web3.HTTPProvider(config.RPC_URL, request_kwargs=request_kwargs))

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    async def _send_transaction(self, tx):
        try:
            if 'chainId' not in tx: tx['chainId'] = self.web3.eth.chain_id
            retries = 3
            for i in range(retries):
                try:
                    tx['nonce'] = self.web3.eth.get_transaction_count(self.address)
                    signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
                    tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    self.log(f"Transaksi dikirim, menunggu konfirmasi... Hash: {tx_hash.hex()}")
                    receipt = await asyncio.to_thread(self.web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                    if receipt.status == 1:
                        self.log(f"{Fore.GREEN}Transaksi sukses! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                        return tx_hash
                    else:
                        self.log(f"{Fore.RED}Transaksi gagal (reverted)! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                        return None
                except Exception as e:
                    error_message = str(e).upper()
                    if "NONCE TOO LOW" in error_message or "REPLACEMENT TRANSACTION UNDERPRICED" in error_message or "INTERNAL_ERROR" in error_message:
                        self.log(f"{Fore.YELLOW}RPC/Nonce Error. Percobaan {i+1}/{retries}. Mencoba lagi...{Style.RESET_ALL}")
                        await asyncio.sleep(5)
                        continue
                    else: raise e
            self.log(f"{Fore.RED}Gagal mengirim transaksi setelah {retries} percobaan.{Style.RESET_ALL}")
            return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat mengirim transaksi: {e}{Style.RESET_ALL}")
            return None
    
    async def _execute_with_retry(self, func, *args, **kwargs):
        retries = 3
        for i in range(retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_message = str(e).upper()
                if "NONCE TOO LOW" in error_message or "INTERNAL_ERROR" in error_message or "PROXYERROR" in error_message:
                    self.log(f"{Fore.YELLOW}RPC/Proxy Error saat mempersiapkan tx. Percobaan {i+1}/{retries}. Mencoba lagi...{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                else:
                    self.log(f"{Fore.RED}Error tidak terduga dalam _execute_with_retry: {e}{Style.RESET_ALL}")
                    return None
        self.log(f"{Fore.RED}Gagal setelah {retries} percobaan.{Style.RESET_ALL}")
        return None

    async def get_token_balance(self, contract_address: str):
        try:
            if contract_address.upper() == "PHRS":
                balance = self.web3.eth.get_balance(self.address)
                return self.web3.from_wei(balance, 'ether')
            else:
                token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(contract_address), abi=config.STANDARD_ERC20_ABI)
                balance = token_contract.functions.balanceOf(self.address).call()
                decimals = token_contract.functions.decimals().call()
                return balance / (10 ** decimals)
        except Exception as e:
            self.log(f"{Fore.RED}Gagal mendapatkan balance: {e}{Style.RESET_ALL}")
            return 0

    async def approve_token(self, spender_address, token_address, amount):
        async def _approve():
            self.log(f"Memeriksa approval untuk token {token_address}...")
            token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=config.STANDARD_ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_in_wei = int(amount * (10**decimals))
            
            allowance = token_contract.functions.allowance(self.address, spender_address).call()
            if allowance >= amount_in_wei:
                self.log(f"{Fore.GREEN}Approval sudah cukup.{Style.RESET_ALL}")
                return True

            self.log(f"Melakukan approval untuk {amount} token...")
            approve_tx_data = token_contract.functions.approve(spender_address, 2**256 - 1)
            
            tx = approve_tx_data.build_transaction({
                "from": self.address,
                "gas": approve_tx_data.estimate_gas({"from": self.address}),
                "gasPrice": self.web3.eth.gas_price
            })
            tx_hash = await self._send_transaction(tx)
            if tx_hash:
                await asyncio.sleep(5)
                return True
            return False
        return await self._execute_with_retry(_approve)

    async def mint_faucet(self, asset_address, ticker):
        async def _mint():
            self.log(f"Minting 100 {ticker} dari Faucet...")
            mint_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_MINT_ROUTER_ADDRESS), abi=config.OPENFI_MINT_ABI)
            asset_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(asset_address), abi=config.STANDARD_ERC20_ABI)
            decimals = asset_contract.functions.decimals().call()
            amount_to_wei = int(100 * (10 ** decimals))
            
            tx_data = mint_router.functions.mint(self.web3.to_checksum_address(asset_address), self.address, amount_to_wei)
            tx = tx_data.build_transaction({
                "from": self.address,
                "gas": tx_data.estimate_gas({"from": self.address}),
                "gasPrice": self.web3.eth.gas_price
            })
            await self._send_transaction(tx)
        await self._execute_with_retry(_mint)

    async def deposit_phrs(self, amount):
        async def _deposit():
            self.log(f"Melakukan deposit {amount} PHRS...")
            deposit_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_DEPOSIT_ROUTER_ADDRESS), abi=config.OPENFI_LENDING_ABI)
            
            # <<< FIX DI SINI: Menggunakan alamat pool yang benar >>>
            lending_pool_address = self.web3.to_checksum_address(config.OPENFI_SUPPLY_ROUTER_ADDRESS)
            tx_data = deposit_router.functions.depositETH(lending_pool_address, self.address, 0)
            
            tx = tx_data.build_transaction({
                "from": self.address,
                "value": self.web3.to_wei(amount, 'ether'),
                "gas": tx_data.estimate_gas({"from": self.address, "value": self.web3.to_wei(amount, 'ether')}),
                "gasPrice": self.web3.eth.gas_price
            })
            await self._send_transaction(tx)
        await self._execute_with_retry(_deposit)

    async def supply_token(self, asset_address, amount, ticker):
        async def _supply():
            self.log(f"Melakukan supply {amount} {ticker}...")
            if not await self.approve_token(config.OPENFI_SUPPLY_ROUTER_ADDRESS, asset_address, amount):
                self.log(f"{Fore.RED}Gagal approve untuk supply, skip.{Style.RESET_ALL}")
                return
                
            supply_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_SUPPLY_ROUTER_ADDRESS), abi=config.OPENFI_LENDING_ABI)
            token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(asset_address), abi=config.STANDARD_ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_to_wei = int(amount * (10 ** decimals))

            tx_data = supply_router.functions.supply(self.web3.to_checksum_address(asset_address), amount_to_wei, self.address, 0)
            tx = tx_data.build_transaction({
                "from": self.address,
                "gas": tx_data.estimate_gas({"from": self.address}),
                "gasPrice": self.web3.eth.gas_price
            })
            await self._send_transaction(tx)
        await self._execute_with_retry(_supply)

    async def borrow_token(self, asset_address, amount, ticker):
        async def _borrow():
            self.log(f"Melakukan borrow {amount} {ticker}...")
            borrow_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_SUPPLY_ROUTER_ADDRESS), abi=config.OPENFI_LENDING_ABI)
            token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(asset_address), abi=config.STANDARD_ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_to_wei = int(amount * (10 ** decimals))

            tx_data = borrow_router.functions.borrow(self.web3.to_checksum_address(asset_address), amount_to_wei, 2, 0, self.address)
            tx = tx_data.build_transaction({
                "from": self.address,
                "gas": tx_data.estimate_gas({"from": self.address}),
                "gasPrice": self.web3.eth.gas_price
            })
            await self._send_transaction(tx)
        await self._execute_with_retry(_borrow)

    async def withdraw_token(self, asset_address, amount, ticker):
        async def _withdraw():
            self.log(f"Melakukan withdraw {amount} {ticker}...")
            withdraw_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_SUPPLY_ROUTER_ADDRESS), abi=config.OPENFI_LENDING_ABI)
            token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(asset_address), abi=config.STANDARD_ERC20_ABI)
            decimals = token_contract.functions.decimals().call()
            amount_to_wei = int(amount * (10 ** decimals))

            tx_data = withdraw_router.functions.withdraw(self.web3.to_checksum_address(asset_address), amount_to_wei, self.address)
            tx = tx_data.build_transaction({
                "from": self.address,
                "gas": tx_data.estimate_gas({"from": self.address}),
                "gasPrice": self.web3.eth.gas_price
            })
            await self._send_transaction(tx)
        await self._execute_with_retry(_withdraw)
        
    async def run_full_lending_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS LENDING UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']

        self.log(f"{Style.BRIGHT}Langkah 1: Mint Faucet...{Style.RESET_ALL}")
        # Mengacak urutan mint faucet
        asset_items = list(config.OPENFI_FAUCET_ASSETS.items())
        random.shuffle(asset_items)
        for ticker, address in asset_items:
            await self.mint_faucet(address, ticker)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        self.log(f"{Style.BRIGHT}Langkah 2: Deposit PHRS...{Style.RESET_ALL}")
        if await self.get_token_balance("PHRS") > settings['deposit_amount']:
            await self.deposit_phrs(settings['deposit_amount'])
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        else:
            self.log(f"{Fore.YELLOW}Balance PHRS tidak cukup untuk deposit.{Style.RESET_ALL}")

        self.log(f"{Style.BRIGHT}Langkah 3: Supply Tokens...{Style.RESET_ALL}")
        # Mengacak urutan supply
        lending_items = list(config.OPENFI_LENDING_ASSETS.items())
        random.shuffle(lending_items)
        for ticker, address in lending_items:
            # Menggunakan persentase acak dari balance
            balance = await self.get_token_balance(address)
            amount_to_supply = balance * random.uniform(0.3, 0.7)
            if amount_to_supply > 0:
                await self.supply_token(address, amount_to_supply, ticker)
                await asyncio.sleep(random.uniform(delay_min, delay_max))
            else:
                self.log(f"{Fore.YELLOW}Balance {ticker} tidak cukup untuk supply. Skip.{Style.RESET_ALL}")

        self.log(f"{Style.BRIGHT}Langkah 4: Borrow Tokens...{Style.RESET_ALL}")
        # Mengacak urutan borrow
        random.shuffle(lending_items)
        for ticker, address in lending_items:
            await self.borrow_token(address, settings['borrow_amount'], ticker)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        self.log(f"{Style.BRIGHT}Langkah 5: Withdraw Tokens...{Style.RESET_ALL}")
        # Mengacak urutan withdraw
        random.shuffle(lending_items)
        for ticker, address in lending_items:
            # Anda mungkin ingin withdraw sebagian kecil dari yang di-supply
            await self.withdraw_token(address, settings['withdraw_amount'], ticker)
            await asyncio.sleep(random.uniform(delay_min, delay_max))
            
        self.log(f"{Fore.MAGENTA}--- SIKLUS LENDING UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")