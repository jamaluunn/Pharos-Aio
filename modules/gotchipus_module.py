# modules/gotchipus_module.py

from web3 import Web3
from eth_account import Account
from colorama import *
import asyncio, json, time, random, pytz
from datetime import datetime
import config
from eth_abi.abi import encode
from eth_utils import keccak, to_hex
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent

wib = pytz.timezone('Asia/Jakarta')

class GotchipusModule:
    def __init__(self, private_key: str, proxy: str = None):
        self.private_key = private_key
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.proxy = proxy
        self.web3 = self._get_web3_provider()

        self.headers = {
            "Accept": "*/*",
            "Origin": "https://gotchipus.com",
            "Referer": "https://gotchipus.com/",
            "User-Agent": FakeUserAgent().random
        }

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

    def _build_checkin_signature_payload(self):
        """Membangun payload EIP-712 untuk verifikasi check-in."""
        domain_typehash = keccak(text="EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)")
        name_hash = keccak(text="Gotchipus")
        version_hash = keccak(text="v0.1.0")

        domain_separator = keccak(encode(
            ['bytes32', 'bytes32', 'bytes32', 'uint256', 'address'],
            [domain_typehash, name_hash, version_hash, 688688, self.web3.to_checksum_address(config.GOTCHIPUS_NFT_CONTRACT_ADDRESS)]
        ))

        checkin_typehash = keccak(text="CheckIn(string intent,address user,uint256 timestamp)")
        intent_hash = keccak(text="Daily Check-In for Gotchipus")
        timestamp = int(time.time())

        struct_hash = keccak(encode(
            ['bytes32', 'bytes32', 'address', 'uint256'],
            [checkin_typehash, intent_hash, self.address, timestamp]
        ))

        digest = keccak(b"\x19\x01" + domain_separator + struct_hash)
        signed = self.account.unsafe_sign_hash(digest)
        signature = to_hex(signed.signature)

        return {"address": self.address, "signature": signature, "timestamp": timestamp}

    async def perform_daily_checkin(self):
        self.log("Memulai proses Check-in Harian Gotchipus...")
        connector = ProxyConnector.from_url(self.proxy) if self.proxy else None
        async with ClientSession(connector=connector) as session:
            try:
                # 1. Dapatkan info tugas untuk cek status
                info_url = "https://gotchipus.com/api/tasks/info"
                async with session.post(info_url, headers=self.headers, json={"address": self.address}) as response:
                    info_data = await response.json()
                    if info_data.get("code") != 0:
                        self.log(f"{Fore.RED}Gagal mendapatkan info check-in: {info_data.get('message')}{Style.RESET_ALL}")
                        return
                
                xp = info_data.get("data", {}).get("xp", 0)
                level = info_data.get("data", {}).get("level", 0)
                self.log(f"Info Akun: {Fore.YELLOW}{xp} XP{Style.RESET_ALL}, Level {Fore.YELLOW}{level}{Style.RESET_ALL}")

                last_checkin_ts = info_data.get("data", {}).get("latest_check_in_at")
                if last_checkin_ts and (int(time.time()) < last_checkin_ts + 86400):
                    next_claim_time = datetime.fromtimestamp(last_checkin_ts + 86400, wib).strftime('%Y-%m-%d %H:%M:%S')
                    self.log(f"{Fore.YELLOW}Check-in harian sudah dilakukan. Coba lagi setelah {next_claim_time}{Style.RESET_ALL}")
                    return

                # 2. Verifikasi dengan signature EIP-712
                self.log("Membuat dan mengirim signature verifikasi...")
                verify_url = "https://gotchipus.com/api/tasks/verify"
                payload = self._build_checkin_signature_payload()
                async with session.post(verify_url, headers=self.headers, json=payload) as response:
                    verify_data = await response.json()
                    if verify_data.get("code") != 0:
                        self.log(f"{Fore.RED}Gagal verifikasi signature: {verify_data.get('message')}{Style.RESET_ALL}")
                        return
                self.log(f"{Fore.GREEN}Verifikasi signature berhasil.{Style.RESET_ALL}")

                # 3. Klaim check-in
                await asyncio.sleep(2)
                claim_url = "https://gotchipus.com/api/tasks/checkin"
                async with session.post(claim_url, headers=self.headers, json={"address": self.address, "event": "check_in"}) as response:
                    claim_data = await response.json()
                    if claim_data.get("code") == 0:
                        self.log(f"{Fore.GREEN}Check-in Harian berhasil diklaim!{Style.RESET_ALL}")
                    else:
                        self.log(f"{Fore.RED}Gagal klaim check-in: {claim_data.get('message')}{Style.RESET_ALL}")

            except Exception as e:
                self.log(f"{Fore.RED}Error saat proses check-in: {e}{Style.RESET_ALL}")
    
    async def run_checkin_cycle(self, settings):
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS CHECK-IN GOTCHIPUS UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']
        
        await self.perform_daily_checkin()
        
        self.log(f"Jeda {delay_min}-{delay_max} detik sebelum lanjut ke akun berikutnya...")
        await asyncio.sleep(random.uniform(delay_min, delay_max))
        
        self.log(f"{Fore.MAGENTA}--- SIKLUS CHECK-IN GOTCHIPUS UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")

    async def run_full_cycle(self, settings):
        """
        Fungsi ini menggabungkan semua tugas: check-in, mint, dan claim.
        """
        self.log(f"{Fore.MAGENTA}--- MEMULAI SIKLUS PENUH GOTCHIPUS UNTUK {self.address[:10]}... ---{Style.RESET_ALL}")
        delay_min, delay_max = settings['delay']
        
        # 1. Jalankan Check-in
        await self.perform_daily_checkin()
        
        self.log(f"Jeda {delay_min}-{delay_max} detik...")
        await asyncio.sleep(random.uniform(delay_min, delay_max))
        
        # 2. Jalankan Mint NFT
        await self.perform_mint_nft()
        
        self.log(f"Jeda {delay_min}-{delay_max} detik...")
        await asyncio.sleep(random.uniform(delay_min, delay_max))

        # 3. Jalankan Claim Wearable
        await self.perform_claim_wearable()
        
        self.log(f"{Fore.MAGENTA}--- SIKLUS PENUH GOTCHIPUS UNTUK {self.address[:10]}... SELESAI ---{Style.RESET_ALL}")
