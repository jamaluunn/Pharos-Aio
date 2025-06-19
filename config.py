# config.py
# File konfigurasi terpusat untuk semua modul AIO Bot.
import json

# --- KONFIGURASI UMUM ---
# RPC URL yang digunakan oleh semua modul
RPC_URL = "https://testnet.dplabs-internal.com"
PHAROS_EXPLORER_URL = "https://testnet.pharosscan.xyz"

# --- PHAROS CONFIG ---
PHAROS_API_URL = "https://api.pharosnetwork.xyz"
PHAROS_REF_CODE = "PNFXEcz1CWezuu3g" # Bisa diganti dengan kode referral Anda

# Alamat Kontrak Pharos
PHAROS_WPHRS_CONTRACT_ADDRESS = "0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"
PHAROS_USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
PHAROS_USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
PHAROS_SWAP_ROUTER_ADDRESS = "0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a"
PHAROS_POTITION_MANAGER_ADDRESS = "0xF8a1D4FF0f9b9Af7CE58E1fc1833688F3BFd6115"

# ABI untuk Pharos
PHAROS_ERC20_ABI = json.loads('''[
    {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
    {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
    {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
    {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
    {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
    {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
]''')
PHAROS_SWAP_ABI = [{"inputs":[{"internalType":"uint256","name":"collectionAndSelfcalls","type":"uint256"},{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[],"stateMutability":"nonpayable","type":"function"}]
PHAROS_ADD_LP_ABI = [{"inputs":[{"components":[{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint256","name":"amount0Desired","type":"uint256"},{"internalType":"uint256","name":"amount1Desired","type":"uint256"},{"internalType":"uint256","name":"amount0Min","type":"uint256"},{"internalType":"uint256","name":"amount1Min","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct INonfungiblePositionManager.MintParams","name":"params","type":"tuple"}],"name":"mint","outputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"payable","type":"function"}]

# --- OPENFI CONFIG ---
OPENFI_USDT_CONTRACT_ADDRESS = "0x0B00Fb1F513E02399667FBA50772B21f34c1b5D9"
OPENFI_USDC_CONTRACT_ADDRESS = "0x48249feEb47a8453023f702f15CF00206eeBdF08"
OPENFI_WPHRS_CONTRACT_ADDRESS = "0x253F3534e1e36B9E4a1b9A6F7b6dE47AC3e7AaD3"
OPENFI_GOLD_CONTRACT_ADDRESS = "0x77f532df5f46DdFf1c97CDae3115271A523fa0f4"
OPENFI_TSLA_CONTRACT_ADDRESS = "0xCDA3DF4AAB8a571688fE493EB1BdC1Ad210C09E4"
OPENFI_BTC_CONTRACT_ADDRESS = "0xA4a967FC7cF0E9815bF5c2700A055813628b65BE"
OPENFI_NVIDIA_CONTRACT_ADDRESS = "0x3299cc551B2a39926Bf14144e65630e533dF6944"
OPENFI_MINT_ROUTER_ADDRESS = "0x2E9D89D372837F71Cb529e5BA85bFbC1785C69Cd"
OPENFI_DEPOSIT_ROUTER_ADDRESS = "0xa8E550710Bf113DB6A1B38472118b8d6d5176D12"
OPENFI_SUPPLY_ROUTER_ADDRESS = "0xAd3B4E20412A097F87CD8e8d84FbBe17ac7C89e9"

OPENFI_FAUCET_ASSETS = {"USDT": OPENFI_USDT_CONTRACT_ADDRESS,"USDC": OPENFI_USDC_CONTRACT_ADDRESS,"GOLD": OPENFI_GOLD_CONTRACT_ADDRESS,"TSLA": OPENFI_TSLA_CONTRACT_ADDRESS,"BTC": OPENFI_BTC_CONTRACT_ADDRESS,"NVIDIA": OPENFI_NVIDIA_CONTRACT_ADDRESS}
OPENFI_LENDING_ASSETS = {"WPHRS": OPENFI_WPHRS_CONTRACT_ADDRESS, **OPENFI_FAUCET_ASSETS}

OPENFI_MINT_ABI = [{"type":"function","name":"mint","inputs":[{"internalType":"address","name":"_asset","type":"address"},{"internalType":"address","name":"_account","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"outputs":[],"stateMutability":"nonpayable"}]
OPENFI_LENDING_ABI = [{"type":"function","name":"depositETH","inputs":[{"name":"lendingPool","type":"address"},{"name":"onBehalfOf","type":"address"},{"name":"referralCode","type":"uint16"}],"outputs":[],"stateMutability":"payable"},{"type":"function","name":"supply","inputs":[{"name":"asset","type":"address"},{"name":"amount","type":"uint256"},{"name":"onBehalfOf","type":"address"},{"name":"referralCode","type":"uint16"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"borrow","inputs":[{"name":"asset","type":"address"},{"name":"amount","type":"uint256"},{"name":"interestRateMode","type":"uint256"},{"name":"referralCode","type":"uint16"},{"name":"onBehalfOf","type":"address"}],"outputs":[],"stateMutability":"nonpayable"},{"type":"function","name":"withdraw","inputs":[{"name":"asset","type":"address"},{"name":"amount","type":"uint256"},{"name":"to","type":"address"}],"outputs":[{"name":"","type":"uint256"}],"stateMutability":"nonpayable"}]

# --- GOTCHIPUS CONFIG ---
GOTCHIPUS_NFT_CONTRACT_ADDRESS = "0x0000000038f050528452D6Da1E7AACFA7B3Ec0a8"
GOTCHIPUS_MINT_ABI = [{"inputs":[],"name":"freeMint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"claimWearable","outputs":[],"stateMutability":"nonpayable","type":"function"}]

# --- BROKEX CONFIG ---
BROKEX_USDT_ADDRESS = "0x78ac5e2d8a78a8b8e6d10c7b7274b03c10c91cef"
BROKEX_CLAIM_ROUTER_ADDRESS = "0x7AaFfFe358fe10074254aa5109eBe4550781B8c6"
BROKEX_TRADE_ROUTER_ADDRESS = "0xBb24da1F6aaA4b0Cb3ff9ae971576790BB65673C"

BROKEX_PAIRS = [{"name":"BTC_USDT","id":0},{"name":"ETH_USDT","id":1},{"name":"SOL_USDT","id":10},{"name":"XRP_USDT","id":14}]
BROKEX_CLAIM_ABI = json.loads('''[
    {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
    {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
    {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
    {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
    {"type":"function","name":"claim","stateMutability":"nonpayable","inputs":[],"outputs":[]}
]''')
