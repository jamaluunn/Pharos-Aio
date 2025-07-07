# modules/gotchipus_module.py

from web3 import Web3
from eth_account import Account
from colorama import *
import asyncio, json, time, random, pytz
from datetime import datetime
import config

wib = pytz.timezone('Asia/Jakarta')

class GotchipusModule:
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
                    if "-32603" in error_message or "INTERNAL_ERROR" in error_message or "TX_REPLAY_ATTACK" in error_message:
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
                if "-32603" in error_message or "INTERNAL_ERROR" in error_message or "TX_REPLAY_ATTACK" in error_message:
                    self.log(f"{Fore.YELLOW}RPC Error saat mempersiapkan tx. Percobaan {i+1}/{retries}. Mencoba lagi...{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                else:
                    self.log(f"{Fore.RED}Error tidak terduga: {e}{Style.RESET_ALL}")
                    return None
        self.log(f"{Fore.RED}Gagal setelah {retries} percobaan.{Style.RESET_ALL}")
        return None

    async def get_phrs_balance(self):
        try:
            balance = self.web3.eth.get_balance(self.address)
            return self.web3.from_wei(balance, 'ether')
        except Exception as e:
            self.log(f"{Fore.RED}Gagal mendapatkan balance PHRS: {e}{Style.RESET_ALL}")
            return 0
    
    async def perform_mint_nft(self):
        async def _mint():
            self.log("Mencoba free mint Gotchipus NFT...")
            balance = await self.get_phrs_balance()
            if balance < 0.0005:
                self.log(f"{Fore.YELLOW}Gas fee tidak cukup untuk mint (Balance: {balance} PHRS). Skip.{Style.RESET_ALL}")
                return
            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.GOTCHIPUS_NFT_CONTRACT_ADDRESS), abi=config.GOTCHIPUS_MINT_ABI)
            tx_data = contract.functions.freeMint()
            tx = tx_data.build_transaction({"from": self.address,"gas": tx_data.estimate_gas({"from": self.address}),"gasPrice": self.web3.eth.gas_price,"nonce": self.web3.eth.get_transaction_count(self.address)})
            await self._send_transaction(tx)
        await self._execute_with_retry(_mint)

    async def perform_claim_wearable(self):
        async def _claim():
            self.log("Mencoba claim Wearable...")
            balance = await self.get_phrs_balance()
            if balance < 0.0008:
                self.log(f"{Fore.YELLOW}Gas fee tidak cukup untuk claim (Balance: {balance} PHRS). Skip.{Style.RESET_ALL}")
                return
            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.GOTCHIPUS_NFT_CONTRACT_ADDRESS), abi=config.GOTCHIPUS_MINT_ABI)
            tx_data = contract.functions.claimWearable()
            tx = tx_data.build_transaction({"from": self.address,"gas": tx_data.estimate_gas({"from": self.address}),"gasPrice": self.web3.eth.gas_price,"nonce": self.web3.eth.get_transaction_count(self.address)})
            await self._send_transaction(tx)
        await self._execute_with_retry(_claim)

    async def run_minting_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS MINTING GOTCHIPUS UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']
        await self.perform_mint_nft()
        self.log(f"Jeda {delay_min}-{delay_max} detik...")
        await asyncio.sleep(random.uniform(delay_min, delay_max))
        await self.perform_claim_wearable()
        self.log(f"{Fore.MAGENTA}--- SIKLUS MINTING GOTCHIPUS UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")
