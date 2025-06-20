# modules/brokex_module.py

from web3 import Web3
from eth_account import Account
from eth_abi.abi import encode
from colorama import *
import asyncio, json, time, random, pytz
from datetime import datetime

import config

wib = pytz.timezone('Asia/Jakarta')

class BrokexModule:
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
            if 'chainId' not in tx:
                tx['chainId'] = self.web3.eth.chain_id

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
            self.log(f"{Fore.RED}Error saat mengirim transaksi: {e}{Style.RESET_ALL}")
            return None

    async def approve_usdt(self, spender_address, amount):
        token_address = config.BROKEX_USDT_ADDRESS
        self.log(f"Memeriksa approval USDT untuk {spender_address}...")
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=config.BROKEX_CLAIM_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10**decimals))
        
        allowance = token_contract.functions.allowance(self.address, spender_address).call()
        if allowance >= amount_in_wei:
            self.log(f"{Fore.GREEN}Approval sudah cukup.{Style.RESET_ALL}")
            return True

        self.log(f"Melakukan approval untuk {amount} USDT...")
        approve_tx_data = token_contract.functions.approve(spender_address, 2**256 - 1)
        
        tx = approve_tx_data.build_transaction({
            "from": self.address,
            "gas": approve_tx_data.estimate_gas({"from": self.address}),
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.address)
        })
        tx_hash = await self._send_transaction(tx)
        if tx_hash:
            await asyncio.sleep(5)
            return True
        return False

    async def perform_claim_faucet(self):
        """ 
        <<<< PERBAIKAN DI SINI >>>>
        Fungsi ini sekarang menangani error revert dengan lebih baik.
        """
        self.log("Mencoba klaim faucet USDT Brokex...")
        contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_CLAIM_ROUTER_ADDRESS), abi=config.BROKEX_CLAIM_ABI)
        try:
            tx_data = contract.functions.claim()
            tx = tx_data.build_transaction({
                "from": self.address,
                "gas": tx_data.estimate_gas({"from": self.address}),
                "gasPrice": self.web3.eth.gas_price,
                "nonce": self.web3.eth.get_transaction_count(self.address),
            })
            tx_hash = await self._send_transaction(tx)
            if tx_hash is None:
                # _send_transaction sudah log error, kita tambahkan info kontekstual
                self.log(f"{Fore.YELLOW}Info: Klaim faucet tidak berhasil. Kemungkinan besar karena sudah pernah klaim (cooldown aktif).{Style.RESET_ALL}")
        except Exception as e:
            # Menangani error bahkan sebelum transaksi dikirim (misal, saat estimate_gas)
            if 'execution reverted' in str(e).lower():
                self.log(f"{Fore.YELLOW}Info: Klaim faucet tidak berhasil. Kemungkinan besar karena sudah pernah klaim (cooldown aktif).{Style.RESET_ALL}")
            else:
                self.log(f"{Fore.RED}Gagal membuat transaksi claim faucet: {e}{Style.RESET_ALL}")


    async def perform_trade(self, pair_id, action, amount):
        pair_name = next((p['name'] for p in config.BROKEX_PAIRS if p['id'] == pair_id), "Unknown")
        action_name = "SHORT" if action == 0 else "LONG"
        self.log(f"Mencoba trade {action_name} {amount} USDT pada pair {pair_name}...")

        if not await self.approve_usdt(config.BROKEX_TRADE_ROUTER_ADDRESS, amount):
            self.log(f"{Fore.RED}Gagal approve USDT, trade dibatalkan.{Style.RESET_ALL}")
            return
            
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_USDT_ADDRESS), abi=config.BROKEX_CLAIM_ABI)
        decimals = token_contract.functions.decimals().call()
        trade_amount_wei = int(amount * (10 ** decimals))

        encoded_data = encode(['uint256','uint256','uint256','uint256','uint256','uint256',],[pair_id,action,trade_amount_wei,5,0,0])
        calldata = "0x3c1395d2" + encoded_data.hex()
        
        try:
            tx = {
                "to": self.web3.to_checksum_address(config.BROKEX_TRADE_ROUTER_ADDRESS),
                "from": self.address,
                "data": calldata,
                "value": 0,
                "gas": 300000,
                "gasPrice": self.web3.eth.gas_price,
                "nonce": self.web3.eth.get_transaction_count(self.address),
            }
            await self._send_transaction(tx)
        except Exception as e:
             self.log(f"{Fore.RED}Gagal membuat transaksi trade: {e}{Style.RESET_ALL}")

    async def run_trading_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS TRADING BROKEX UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']

        await self.perform_claim_faucet()
        await asyncio.sleep(random.uniform(delay_min, delay_max))

        for i in range(settings['trade_count']):
            self.log(f"{Style.BRIGHT}--- Trade ke-{i+1}/{settings['trade_count']} ---")
            pair = random.choice(config.BROKEX_PAIRS)
            action = random.choice([0, 1]) 
            
            await self.perform_trade(pair['id'], action, settings['trade_amount'])
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        self.log(f"{Fore.MAGENTA}--- SIKLUS TRADING BROKEX UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")
