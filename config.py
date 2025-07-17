# config.py
# File konfigurasi terpusat untuk semua modul AIO Bot.
import json

# --- KONFIGURASI UMUM ---
# <<< RPC untuk modul lama (Pharos, OpenFi, dll.) >>>
RPC_URL = "https://testnet.dplabs-internal.com"

# <<< Daftar RPC KHUSUS untuk modul Faroswap >>>
FAROSWAP_RPC_URLS = [
    "https://api.zan.top/node/v1/pharos/testnet/RPC MU",
    "https://testnet.dplabs-internal.com"
]

RPC_URLS = [
    "https://api.zan.top/node/v1/pharos/testnet/RPC MU",
    "https://testnet.dplabs-internal.com"
]

PHAROS_EXPLORER_URL = "https://testnet.pharosscan.xyz"

# --- ABI STANDAR UNTUK SEMUA TOKEN ERC20 ---
STANDARD_ERC20_ABI = json.loads('''[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"remaining","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},{"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}]''')

# --- PHAROS CONFIG ---
PHAROS_API_URL = "https://api.pharosnetwork.xyz"
PHAROS_REF_CODE = "UhJiUMyGIbOahtEh"
PHAROS_TASK_IDS = {"send_to_friends": "103"}
PHAROS_WPHRS_CONTRACT_ADDRESS = "0x76aaaDA469D23216bE5f7C596fA25F282Ff9b364"
PHAROS_USDC_CONTRACT_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
PHAROS_USDT_CONTRACT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
PHAROS_SWAP_ROUTER_ADDRESS = "0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a"
PHAROS_POTITION_MANAGER_ADDRESS = "0xF8a1D4FF0f9b9Af7CE58E1fc1833688F3BFd6115"
PHAROS_BADGE_CONTRACT_ADDRESS = "0x1A4DE519154Ae51200b0Ad7c90F7faC75547888a"
PHAROS_BADGE_MINT_DATA = '0x84bb1e42{wallet_address}0000000000000000000000000000000000000000000000000000000000000001000000000000000000000000eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee0000000000000000000000000000000000000000000000000de0b6b3a764000000000000000000000000000000000000000000000000000000000000000c0000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000000800000000000000000000000000000000000000000000000000000000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
PHAROS_ZENITH_SWAP_ABI = json.loads('''[{"inputs":[{"internalType":"uint256","name":"collectionAndSelfcalls","type":"uint256"},{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[],"stateMutability":"nonpayable","type":"function"}]''')
PHAROS_POSITION_MANAGER_ABI = json.loads('''[{"inputs":[{"internalType":"address","name":"_factory","type":"address"},{"internalType":"address","name":"_WETH9","type":"address"},{"internalType":"address","name":"_tokenDescriptor_","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"approved","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"operator","type":"address"},{"indexed":false,"internalType":"bool","name":"approved","type":"bool"}],"name":"ApprovalForAll","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"address","name":"recipient","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"Collect","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"uint128","name":"liquidity","type":"uint128"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"DecreaseLiquidity","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"},{"indexed":false,"internalType":"uint128","name":"liquidity","type":"uint128"},{"indexed":false,"internalType":"uint256","name":"amount0","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"amount1","type":"uint256"}],"name":"IncreaseLiquidity","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":true,"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[],"name":"WETH9","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"approve","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"balance","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint128","name":"amount0Max","type":"uint128"},{"internalType":"uint128","name":"amount1Max","type":"uint128"}],"internalType":"struct INonfungiblePositionManager.CollectParams","name":"params","type":"tuple"}],"name":"collect","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"uint160","name":"sqrtPriceX96","type":"uint160"}],"name":"createAndInitializePoolIfNecessary","outputs":[{"internalType":"address","name":"pool","type":"address"}],"stateMutability":"payable","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"amount0Min","type":"uint256"},{"internalType":"uint256","name":"amount1Min","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct INonfungiblePositionManager.DecreaseLiquidityParams","name":"params","type":"tuple"}],"name":"decreaseLiquidity","outputs":[{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"factory","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"getApproved","outputs":[{"internalType":"address","name":"operator","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"uint256","name":"amount0Desired","type":"uint256"},{"internalType":"uint256","name":"amount1Desired","type":"uint256"},{"internalType":"uint256","name":"amount0Min","type":"uint256"},{"internalType":"uint256","name":"amount1Min","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct INonfungiblePositionManager.IncreaseLiquidityParams","name":"params","type":"tuple"}],"name":"increaseLiquidity","outputs":[{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"operator","type":"address"}],"name":"isApprovedForAll","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint256","name":"amount0Desired","type":"uint256"},{"internalType":"uint256","name":"amount1Desired","type":"uint256"},{"internalType":"uint256","name":"amount0Min","type":"uint256"},{"internalType":"uint256","name":"amount1Min","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"}],"internalType":"struct INonfungiblePositionManager.MintParams","name":"params","type":"tuple"}],"name":"mint","outputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"amount0","type":"uint256"},{"internalType":"uint256","name":"amount1","type":"uint256"}],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes[]","name":"data","type":"bytes[]"}],"name":"multicall","outputs":[{"internalType":"bytes[]","name":"results","type":"bytes[]"}],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"ownerOf","outputs":[{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"permit","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"positions","outputs":[{"internalType":"uint96","name":"nonce","type":"uint96"},{"internalType":"address","name":"operator","type":"address"},{"internalType":"address","name":"token0","type":"address"},{"internalType":"address","name":"token1","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"int24","name":"tickLower","type":"int24"},{"internalType":"int24","name":"tickUpper","type":"int24"},{"internalType":"uint128","name":"liquidity","type":"uint128"},{"internalType":"uint256","name":"feeGrowthInside0LastX128","type":"uint256"},{"internalType":"uint256","name":"feeGrowthInside1LastX128","type":"uint256"},{"internalType":"uint128","name":"tokensOwed0","type":"uint128"},{"internalType":"uint128","name":"tokensOwed1","type":"uint128"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"refundETH","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"from","type":"address"},{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"tokenId","type":"uint256"},{"internalType":"bytes","name":"_data","type":"bytes"}],"name":"safeTransferFrom","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"operator","type":"address"},{"internalType":"bool","name":"_approved","type":"bool"}],"name":"setApprovalForAll","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes4","name":"interfaceId","type":"bytes4"}],"name":"supportsInterface","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountMinimum","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"name":"sweepToken","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountMinimum","type":"uint256"}],"name":"sweepToken","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountMinimum","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"feeBips","type":"uint256"},{"internalType":"address","name":"feeRecipient","type":"address"}],"name":"sweepTokenWithFee","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountMinimum","type":"uint256"},{"internalType":"uint256","name":"feeBips","type":"uint256"},{"internalType":"address","name":"feeRecipient","type":"address"}],"name":"sweepTokenWithFee","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amountToWrap","type":"uint256"}],"name":"unwrapWETH9","outputs":[],"stateMutability":"payable","type":"function"},{"stateMutability":"payable","type":"receive"}]''')

TOKEN_MAP = {
    PHAROS_WPHRS_CONTRACT_ADDRESS: "WPHRS",
    PHAROS_USDC_CONTRACT_ADDRESS: "USDC",
    PHAROS_USDT_CONTRACT_ADDRESS: "USDT"
}

# Daftar pasangan untuk Zenith Swap
PHAROS_SWAP_PAIRS = [
    (PHAROS_WPHRS_CONTRACT_ADDRESS, PHAROS_USDC_CONTRACT_ADDRESS),
    (PHAROS_WPHRS_CONTRACT_ADDRESS, PHAROS_USDT_CONTRACT_ADDRESS),
    (PHAROS_USDC_CONTRACT_ADDRESS, PHAROS_WPHRS_CONTRACT_ADDRESS),
    (PHAROS_USDT_CONTRACT_ADDRESS, PHAROS_WPHRS_CONTRACT_ADDRESS),
    (PHAROS_USDC_CONTRACT_ADDRESS, PHAROS_USDT_CONTRACT_ADDRESS),
    (PHAROS_USDT_CONTRACT_ADDRESS, PHAROS_USDC_CONTRACT_ADDRESS)
]

# Daftar pasangan untuk Add Liquidity
PHAROS_LP_PAIRS = [
    (PHAROS_WPHRS_CONTRACT_ADDRESS, PHAROS_USDC_CONTRACT_ADDRESS),
    (PHAROS_WPHRS_CONTRACT_ADDRESS, PHAROS_USDT_CONTRACT_ADDRESS),
    (PHAROS_USDC_CONTRACT_ADDRESS, PHAROS_USDT_CONTRACT_ADDRESS)
]

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

# --- BROKEX CONFIG (Updated) ---
BROKEX_USDT_ADDRESS = "0x78ac5e2d8a78a8b8e6d10c7b7274b03c10c91cef"
BROKEX_CLAIM_ROUTER_ADDRESS = "0x50576285BD33261DEe1aD99BF766CD8249520a58"
BROKEX_TRADE_ROUTER_ADDRESS = "0x01f61eb2e4667c6188f4c1c87c0f529155bf888c" # <-- Alamat BARU
BROKEX_PAIRS = [
    {"name": "BTC_USDT", "id": 0},
    {"name": "ETH_USDT", "id": 1},
    {"name": "SOL_USDT", "id": 10},
    {"name": "XRP_USDT", "id": 14}
]
# ABI Baru untuk klaim faucet (dengan fungsi check)
BROKEX_CLAIM_ABI = json.loads('''[
    {"type":"function","name":"hasClaimed","stateMutability":"view","inputs":[{"internalType":"address","name":"","type":"address"}],"outputs":[{"internalType":"bool","name":"","type":"bool"}]},
    {"type":"function","name":"claim","stateMutability":"nonpayable","inputs":[],"outputs":[]}
]''')
# ABI Baru untuk trading (dengan fungsi createPendingOrder)
BROKEX_ORDER_ABI = json.loads('''[
    {
        "name":"createPendingOrder",
        "type":"function",
        "stateMutability":"nonpayable",
        "inputs":[
            {"internalType":"uint256","name":"assetIndex","type":"uint256"},
            {"internalType":"bool","name":"isLong","type":"bool"},
            {"internalType":"uint256","name":"usdSize","type":"uint256"},
            {"internalType":"uint256","name":"leverage","type":"uint256"},
            {"internalType":"uint256","name":"slPrice","type":"uint256"},
            {"internalType":"uint256","name":"tpPrice","type":"uint256"}
        ],
        "outputs":[]
    },
    {
        "name": "openPosition",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"internalType": "uint256", "name": "pairId", "type": "uint256"},
            {"internalType": "bytes", "name": "proof", "type": "bytes"},
            {"internalType": "bool", "name": "isLong", "type": "bool"},
            {"internalType": "uint256", "name": "leverage", "type": "uint256"},
            {"internalType": "uint256", "name": "usdSize", "type": "uint256"},
            {"internalType": "uint256", "name": "slPrice", "type": "uint256"},
            {"internalType": "uint256", "name": "tpPrice", "type": "uint256"}
        ],
        "outputs": []
    }
]''')

BROKEX_POOL_ROUTER_ADDRESS = "0x9A88d07850723267DB386C681646217Af7e220d7"  # Ganti sesuai pool router Brokex kamu

BROKEX_POOL_ABI = json.loads('''[
    {
        "name": "depositLiquidity",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            { "internalType": "uint256", "name": "usdtAmount", "type": "uint256" }
        ],
        "outputs": []
    },
    {
        "name": "withdrawLiquidity",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            { "internalType": "uint256", "name": "lpAmount", "type":"uint256" }
        ],
        "outputs": []
    }
]''')

# --- FAROSWAP (DODO ROUTER) CONFIG ---
FAROSWAP_PHRS_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
FAROSWAP_WPHRS_ADDRESS = "0x3019B247381c850ab53Dc0EE53bCe7A07Ea9155f"
FAROSWAP_USDC_ADDRESS = "0x72df0bcd7276f2dFbAc900D1CE63c272C4BCcCED"
FAROSWAP_USDT_ADDRESS = "0xD4071393f8716661958F766DF660033b3d35fD29"
FAROSWAP_WETH_ADDRESS = "0x4E28826d32F1C398DED160DC16Ac6873357d048f"
FAROSWAP_WBTC_ADDRESS = "0x8275c526d1bCEc59a31d673929d3cE8d108fF5c7"
FAROSWAP_MIXSWAP_ROUTER_ADDRESS = "0x3541423f25A1Ca5C98fdBCf478405d3f0aaD1164"
FAROSWAP_DVM_ROUTER_ADDRESS = "0x4b177AdEd3b8bD1D5D747F91B9E853513838Cd49"
FAROSWAP_LP_POOL_ADDRESS = "0x73cafc894dbfc181398264934f7be4e482fc9d40"
# <<< FIX: Menambahkan FAROSWAP_MIXSWAP_ABI >>>
FAROSWAP_MIXSWAP_ABI = json.loads('''[{"inputs":[{"components":[{"internalType":"address","name":"tokenIn","type":"address"},{"internalType":"address","name":"tokenOut","type":"address"},{"internalType":"uint24","name":"fee","type":"uint24"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"uint256","name":"amountOutMinimum","type":"uint256"},{"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}],"internalType":"struct ISwapRouter.ExactInputSingleParams","name":"params","type":"tuple"}],"name":"exactInputSingle","outputs":[{"internalType":"uint256","name":"amountOut","type":"uint256"}],"stateMutability":"payable","type":"function"}]''')
FAROSWAP_DVM_POOL_ABI = json.loads('''[{"type":"function","name":"addDVMLiquidity","stateMutability":"payable","inputs":[{"internalType":"address","name":"dvmAddress","type":"address"},{"internalType":"uint256","name":"baseInAmount","type":"uint256"},{"internalType":"uint256","name":"quoteInAmount","type":"uint256"},{"internalType":"uint256","name":"baseMinAmount","type":"uint256"},{"internalType":"uint256","name":"quoteMinAmount","type":"uint256"},{"internalType":"uint8","name":"flag","type":"uint8"},{"internalType":"uint256","name":"deadLine","type":"uint256"}],"outputs":[{"internalType":"uint256","name":"shares","type":"uint256"},{"internalType":"uint256","name":"baseAdjustedInAmount","type":"uint256"},{"internalType":"uint256","name":"quoteAdjustedInAmount","type":"uint256"}]}]''')

# --- FAROSWAP (METODE BARU) CONFIG ---
FAROSWAP_MIXSWAP_ROUTER_ADDRESS = "0x3541423f25A1Ca5C98fdBCf478405d3f0aaD1164"
FAROSWAP_POOL_ROUTER_ADDRESS = "0x73cafc894dbfc181398264934f7be4e482fc9d40"
