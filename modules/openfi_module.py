# modules/openfi_module.py (Updated with randomized logic)
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

    # GANTI FUNGSI LAMA DENGAN VERSI BARU INI
    async def _send_transaction(self, tx):
        try:
            # Menggunakan parameter EIP-1559 yang lebih modern
            if 'nonce' not in tx: tx['nonce'] = self.web3.eth.get_transaction_count(self.address)
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
                # Mengembalikan format hex string agar konsisten
                return tx_hash.hex() 
            else:
                self.log(f"{Fore.RED}Transaksi gagal (reverted)! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
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
                token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(contract_address), abi=config.STANDARD_ERC20_ABI)
                balance = token_contract.functions.balanceOf(self.address).call()
                decimals = token_contract.functions.decimals().call()
                return balance / (10 ** decimals)
        except Exception as e:
            self.log(f"{Fore.RED}Gagal mendapatkan balance: {e}{Style.RESET_ALL}")
            return 0

    async def approve_token(self, spender_address, token_address, amount):
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
        tx = approve_tx_data.build_transaction({"from": self.address,"gas": approve_tx_data.estimate_gas({"from": self.address})})
        tx_hash = await self._send_transaction(tx)
        if tx_hash:
            await asyncio.sleep(5)
            return True
        return False

    async def mint_faucet(self, asset_address, ticker):
        self.log(f"Minting 100 {ticker} dari Faucet...")
        mint_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_MINT_ROUTER_ADDRESS), abi=config.OPENFI_MINT_ABI)
        asset_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(asset_address), abi=config.STANDARD_ERC20_ABI)
        decimals = asset_contract.functions.decimals().call()
        amount_to_wei = int(100 * (10 ** decimals))
        tx_data = mint_router.functions.mint(self.web3.to_checksum_address(asset_address), self.address, amount_to_wei)
        tx = tx_data.build_transaction({"from": self.address,"gas": tx_data.estimate_gas({"from": self.address})})
        await self._send_transaction(tx)

    async def deposit_phrs(self, amount):
        self.log(f"Melakukan deposit {amount:.4f} PHRS...")
        deposit_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_DEPOSIT_ROUTER_ADDRESS), abi=config.OPENFI_LENDING_ABI)
        lending_pool_address = self.web3.to_checksum_address(config.OPENFI_SUPPLY_ROUTER_ADDRESS)
        tx_data = deposit_router.functions.depositETH(lending_pool_address, self.address, 0)
        tx = tx_data.build_transaction({"from": self.address,"value": self.web3.to_wei(amount, 'ether'),"gas": tx_data.estimate_gas({"from": self.address, "value": self.web3.to_wei(amount, 'ether')})})
        await self._send_transaction(tx)

    async def supply_token(self, asset_address, amount, ticker):
        self.log(f"Melakukan supply {amount:.4f} {ticker}...")
        if not await self.approve_token(config.OPENFI_SUPPLY_ROUTER_ADDRESS, asset_address, amount):
            self.log(f"{Fore.RED}Gagal approve untuk supply, skip.{Style.RESET_ALL}"); return
        supply_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_SUPPLY_ROUTER_ADDRESS), abi=config.OPENFI_LENDING_ABI)
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(asset_address), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_to_wei = int(amount * (10 ** decimals))
        tx_data = supply_router.functions.supply(self.web3.to_checksum_address(asset_address), amount_to_wei, self.address, 0)
        tx = tx_data.build_transaction({"from": self.address,"gas": tx_data.estimate_gas({"from": self.address})})
        await self._send_transaction(tx)

    async def borrow_token(self, asset_address, amount, ticker):
        self.log(f"Melakukan borrow {amount:.4f} {ticker}...")
        borrow_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_SUPPLY_ROUTER_ADDRESS), abi=config.OPENFI_LENDING_ABI)
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(asset_address), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_to_wei = int(amount * (10 ** decimals))
        tx_data = borrow_router.functions.borrow(self.web3.to_checksum_address(asset_address), amount_to_wei, 2, 0, self.address)
        tx = tx_data.build_transaction({"from": self.address,"gas": tx_data.estimate_gas({"from": self.address})})
        await self._send_transaction(tx)

    async def withdraw_token(self, asset_address, amount, ticker):
        self.log(f"Melakukan withdraw {amount:.4f} {ticker}...")
        withdraw_router = self.web3.eth.contract(address=self.web3.to_checksum_address(config.OPENFI_SUPPLY_ROUTER_ADDRESS), abi=config.OPENFI_LENDING_ABI)
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(asset_address), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_to_wei = int(amount * (10 ** decimals))
        tx_data = withdraw_router.functions.withdraw(self.web3.to_checksum_address(asset_address), amount_to_wei, self.address)
        tx = tx_data.build_transaction({"from": self.address,"gas": tx_data.estimate_gas({"from": self.address})})
        await self._send_transaction(tx)
        
    async def run_full_lending_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS LENDING UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']

        self.log(f"{Style.BRIGHT}Langkah 1: Mint Faucet...{Style.RESET_ALL}")
        asset_items = list(config.OPENFI_FAUCET_ASSETS.items())
        random.shuffle(asset_items)
        for ticker, address in asset_items:
            await self.mint_faucet(address, ticker)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        deposit_amount = random.uniform(settings['deposit_amount'][0], settings['deposit_amount'][1])
        self.log(f"{Style.BRIGHT}Langkah 2: Deposit PHRS...{Style.RESET_ALL}")
        if await self.get_token_balance("PHRS") > deposit_amount:
            await self.deposit_phrs(deposit_amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))
        else:
            self.log(f"{Fore.YELLOW}Balance PHRS tidak cukup untuk deposit.{Style.RESET_ALL}")

        self.log(f"{Style.BRIGHT}Langkah 3: Supply Tokens...{Style.RESET_ALL}")
        lending_items = list(config.OPENFI_LENDING_ASSETS.items())
        random.shuffle(lending_items)
        for ticker, address in lending_items:
            supply_amount = random.uniform(settings['supply_amount'][0], settings['supply_amount'][1])
            balance = await self.get_token_balance(address)
            amount_to_supply = min(balance * random.uniform(0.3, 0.7), supply_amount)
            if amount_to_supply > 0:
                await self.supply_token(address, amount_to_supply, ticker)
                await asyncio.sleep(random.uniform(delay_min, delay_max))
            else:
                self.log(f"{Fore.YELLOW}Balance {ticker} tidak cukup untuk supply. Skip.{Style.RESET_ALL}")

        self.log(f"{Style.BRIGHT}Langkah 4: Borrow Tokens...{Style.RESET_ALL}")
        random.shuffle(lending_items)
        for ticker, address in lending_items:
            borrow_amount = random.uniform(settings['borrow_amount'][0], settings['borrow_amount'][1])
            await self.borrow_token(address, borrow_amount, ticker)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        self.log(f"{Style.BRIGHT}Langkah 5: Withdraw Tokens...{Style.RESET_ALL}")
        random.shuffle(lending_items)
        for ticker, address in lending_items:
            withdraw_amount = random.uniform(settings['withdraw_amount'][0], settings['withdraw_amount'][1])
            await self.withdraw_token(address, withdraw_amount, ticker)
            await asyncio.sleep(random.uniform(delay_min, delay_max))
            
        self.log(f"{Fore.MAGENTA}--- SIKLUS LENDING UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")
