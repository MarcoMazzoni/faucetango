import os
from faucet.service.impl.eth_blockchain_service import ETHBlockchainService

blockchain_service = ETHBlockchainService(
    deposit_wallet_private_key=os.environ.get('DEPOSIT_WALLET_PRIVATE_KEY'),
    ethereum_node_url=os.environ.get('ETHEREUM_NODE_URL'),
)