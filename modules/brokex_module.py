# modules/brokex_module.py (Updated to Latest Version)
from web3 import Web3
from eth_account import Account
from colorama import *
import asyncio, json, time, random, pytz
from datetime import datetime
import config
import aiohttp

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
        return Web3(Web3.HTTPProvider(random.choice(config.RPC_URLS), request_kwargs=request_kwargs))

    def log(self, message):
        print(f"{Fore.CYAN+Style.BRIGHT}[ {datetime.now(wib).strftime('%H:%M:%S')} ]{Style.RESET_ALL} {message}", flush=True)

    async def _send_transaction(self, tx):
        try:
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
                return tx_hash.hex()
            else:
                self.log(f"{Fore.RED}Transaksi gagal! Explorer: {config.PHAROS_EXPLORER_URL}/tx/{tx_hash.hex()}{Style.RESET_ALL}")
                return None
        except Exception as e:
            self.log(f"{Fore.RED}Error saat mengirim transaksi: {e}{Style.RESET_ALL}")
            return None

    async def approve_usdt(self, spender_address, amount):
        token_address = config.BROKEX_USDT_ADDRESS
        self.log(f"Memeriksa approval USDT untuk trade...")

        # --- PERBAIKAN DI SINI ---
        # Mengonversi alamat spender ke format checksum
        spender = self.web3.to_checksum_address(spender_address)
        # -------------------------

        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10**decimals))
    
        allowance = token_contract.functions.allowance(self.address, spender).call()
        if allowance >= amount_in_wei:
            self.log(f"{Fore.GREEN}Approval sudah cukup.{Style.RESET_ALL}")
            return True
    
        self.log(f"Melakukan approval untuk {amount} USDT...")
        # Gunakan variabel 'spender' yang sudah dichecksum
        approve_tx_data = token_contract.functions.approve(spender, 2**256 - 1)
        tx = approve_tx_data.build_transaction({"from": self.address})
        tx_hash = await self._send_transaction(tx)
        if tx_hash:
            await asyncio.sleep(random.randint(5,8))
            return True
        return False

    async def perform_claim_faucet(self):
        self.log("Memeriksa status faucet Brokex...")
        try:
            contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_CLAIM_ROUTER_ADDRESS), abi=config.BROKEX_CLAIM_ABI)
            
            # Logika baru: Cek dulu sebelum klaim
            has_claimed = contract.functions.hasClaimed(self.address).call()
            if has_claimed:
                self.log(f"{Fore.YELLOW}Faucet sudah pernah diklaim untuk akun ini.{Style.RESET_ALL}")
                return

            self.log("Faucet belum diklaim, mencoba klaim USDT...")
            tx_data = contract.functions.claim()
            tx = tx_data.build_transaction({"from": self.address})
            await self._send_transaction(tx)
        except Exception as e:
            self.log(f"{Fore.RED}Error tidak terduga saat klaim faucet: {e}{Style.RESET_ALL}")

    async def get_proof(self, pair_id):
        url = f"https://proofcrypto-production.up.railway.app/proof?pairs={pair_id}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get('proof')
        except Exception as e:
            self.log(f"{Fore.YELLOW}Gagal ambil proof: {e}{Style.RESET_ALL}")
        return None

    async def perform_trade(self, pair_id, is_long, amount):
        pair_name = next((p['name'] for p in config.BROKEX_PAIRS if p['id'] == pair_id), "Unknown")
        action_name = "LONG" if is_long else "SHORT"
        self.log(f"Mencoba trade {action_name} {amount:.2f} USDT pada pair {pair_name}...")

        if not await self.approve_usdt(config.BROKEX_TRADE_ROUTER_ADDRESS, amount):
            self.log(f"{Fore.RED}Gagal approve USDT, trade dibatalkan.{Style.RESET_ALL}"); return

        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_USDT_ADDRESS), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        trade_amount_wei = int(amount * (10 ** decimals))

        # --- Coba trade pakai proof ---
        proof = await self.get_proof(pair_id)
        trade_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_TRADE_ROUTER_ADDRESS), abi=config.BROKEX_ORDER_ABI)
        if proof:
            try:
                tx_data = trade_contract.functions.openPosition(
                    pair_id, proof, is_long, 5, trade_amount_wei, 0, 0
                )
                tx = tx_data.build_transaction({"from": self.address, "value": 0})
                await self._send_transaction(tx)
                return
            except Exception as e:
                self.log(f"{Fore.YELLOW}Trade dengan proof gagal: {e}{Style.RESET_ALL}")
                self.log(f"{Fore.YELLOW}Coba fallback ke createPendingOrder...{Style.RESET_ALL}")

        # --- Fallback ke cara awal ---
        try:
            tx_data = trade_contract.functions.createPendingOrder(
                pair_id, is_long, trade_amount_wei, 5, 0, 0
            )
            tx = tx_data.build_transaction({"from": self.address, "value": 0})
            await self._send_transaction(tx)
        except Exception as e:
            self.log(f"{Fore.RED}Trade fallback juga gagal: {e}{Style.RESET_ALL}")

    async def approve_lp(self, amount):
        token_address = config.BROKEX_USDT_ADDRESS
        spender = self.web3.to_checksum_address(config.BROKEX_POOL_ROUTER_ADDRESS)
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(token_address), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10**decimals))
        allowance = token_contract.functions.allowance(self.address, spender).call()
        if allowance >= amount_in_wei:
            self.log(f"{Fore.GREEN}Approval USDT untuk LP sudah cukup.{Style.RESET_ALL}")
            return True
        self.log(f"Melakukan approval USDT untuk LP...")
        approve_tx_data = token_contract.functions.approve(spender, 2**256 - 1)
        tx = approve_tx_data.build_transaction({"from": self.address})
        tx_hash = await self._send_transaction(tx)
        if tx_hash:
            await asyncio.sleep(random.randint(5,8))
            return True
        return False

    async def add_liquidity(self, amount):
        self.log(f"Menambah liquidity pool {amount:.2f} USDT...")
        if not await self.approve_lp(amount):
            self.log(f"{Fore.RED}Gagal approve USDT untuk LP, add liquidity dibatalkan.{Style.RESET_ALL}"); return
        token_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_USDT_ADDRESS), abi=config.STANDARD_ERC20_ABI)
        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10 ** decimals))
        pool_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_POOL_ROUTER_ADDRESS), abi=config.BROKEX_POOL_ABI)
        tx_data = pool_contract.functions.depositLiquidity(amount_in_wei)
        tx = tx_data.build_transaction({"from": self.address})
        await self._send_transaction(tx)

    async def withdraw_liquidity(self, lp_amount):
        self.log(f"Withdraw liquidity pool {lp_amount:.4f} LP Token...")
        pool_contract = self.web3.eth.contract(address=self.web3.to_checksum_address(config.BROKEX_POOL_ROUTER_ADDRESS), abi=config.BROKEX_POOL_ABI)
        decimals = 18  # Biasanya LP token 18 desimal
        lp_amount_wei = int(lp_amount * (10 ** decimals))
        tx_data = pool_contract.functions.withdrawLiquidity(lp_amount_wei)
        tx = tx_data.build_transaction({"from": self.address})
        await self._send_transaction(tx)

    async def run_trading_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS TRADING BROKEX UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']

        # --- Jalankan Add Liquidity jika ada ---
        lp_add_amount = settings.get("lp_add_amount")
        if lp_add_amount:
            await self.add_liquidity(lp_add_amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        # --- Jalankan Withdraw Liquidity jika ada ---
        lp_withdraw_amount = settings.get("lp_withdraw_amount")
        if lp_withdraw_amount:
            await self.withdraw_liquidity(lp_withdraw_amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        trade_count = random.randint(settings['trade_count'][0], settings['trade_count'][1])
        await self.perform_claim_faucet()
        await asyncio.sleep(random.uniform(delay_min, delay_max))

        for i in range(trade_count):
            self.log(f"{Style.BRIGHT}--- Trade ke-{i+1}/{trade_count} ---")
            trade_amount = random.uniform(settings['trade_amount'][0], settings['trade_amount'][1])
            pair = random.choice(config.BROKEX_PAIRS)
            is_long = random.choice([True, False])
            await self.perform_trade(pair['id'], is_long, trade_amount)
            await asyncio.sleep(random.uniform(delay_min, delay_max))

        self.log(f"{Fore.MAGENTA}--- SIKLUS TRADING BROKEX UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")