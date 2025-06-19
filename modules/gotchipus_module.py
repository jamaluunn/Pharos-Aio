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
            # Mengatur gas fee menjadi sangat rendah atau nol untuk free mint
            tx['maxFeePerGas'] = self.web3.to_wei(0.01, 'gwei')
            tx['maxPriorityFeePerGas'] = self.web3.to_wei(0.01, 'gwei')

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

    async def get_phrs_balance(self):
        try:
            balance = self.web3.eth.get_balance(self.address)
            return self.web3.from_wei(balance, 'ether')
        except Exception as e:
            self.log(f"{Fore.RED}Gagal mendapatkan balance PHRS: {e}{Style.RESET_ALL}")
            return 0
    
    async def perform_mint_nft(self):
        self.log("Mencoba free mint Gotchipus NFT...")
        
        balance = await self.get_phrs_balance()
        if balance < 0.0005: # Perkiraan gas fee
            self.log(f"{Fore.YELLOW}Gas fee tidak cukup untuk mint (Balance: {balance} PHRS). Skip.{Style.RESET_ALL}")
            return

        contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.GOTCHIPUS_NFT_CONTRACT_ADDRESS), abi=config.GOTCHIPUS_MINT_ABI)
        tx_data = contract.functions.freeMint()
        
        try:
            tx = tx_data.build_transaction({
                "from": self.address,
                "gas": tx_data.estimate_gas({"from": self.address}),
                "nonce": self.web3.eth.get_transaction_count(self.address),
                "chainId": self.web3.eth.chain_id
            })
            await self._send_transaction(tx)
        except Exception as e:
            self.log(f"{Fore.RED}Gagal membuat transaksi mint: {e}{Style.RESET_ALL}")


    async def perform_claim_wearable(self):
        self.log("Mencoba claim Wearable...")

        balance = await self.get_phrs_balance()
        if balance < 0.0008: # Perkiraan gas fee
            self.log(f"{Fore.YELLOW}Gas fee tidak cukup untuk claim (Balance: {balance} PHRS). Skip.{Style.RESET_ALL}")
            return

        contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.GOTCHIPUS_NFT_CONTRACT_ADDRESS), abi=config.GOTCHIPUS_MINT_ABI)
        tx_data = contract.functions.claimWearable()

        try:
            tx = tx_data.build_transaction({
                "from": self.address,
                "gas": tx_data.estimate_gas({"from": self.address}),
                "nonce": self.web3.eth.get_transaction_count(self.address),
                "chainId": self.web3.eth.chain_id
            })
            await self._send_transaction(tx)
        except Exception as e:
            self.log(f"{Fore.RED}Gagal membuat transaksi claim: {e}{Style.RESET_ALL}")


    async def run_minting_cycle(self, settings):
        """Menjalankan siklus mint NFT dan claim wearable."""
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS MINTING GOTCHIPUS UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']

        # 1. Mint NFT
        await self.perform_mint_nft()
        
        self.log(f"Jeda {delay_min}-{delay_max} detik...")
        await asyncio.sleep(random.uniform(delay_min, delay_max))

        # 2. Claim Wearable
        await self.perform_claim_wearable()

        self.log(f"{Fore.MAGENTA}--- SIKLUS MINTING GOTCHIPUS UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")
