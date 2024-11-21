Composite Partition Key

If you need a composite partition key (e.g., using user_id and user_wallet_id together):


class UserWalletCurrentHoldingCS(Model):
    __keyspace__ = "user_portfolio_data"
    __table_name__ = "user_wallet_current_holding"

    # Composite partition key
    user_id = columns.Text(primary_key=True, partition_key=True)
    user_wallet_id = columns.Text(primary_key=True, partition_key=True)
    # Clustering keys
    asset_id = columns.Text(primary_key=True)
    id = columns.Text(primary_key=True)

    # Rest of the columns...
