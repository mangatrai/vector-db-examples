import asyncio
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.cqlengine import columns, connection
from cassandra.cqlengine.models import Model
from cassandra.cqlengine.management import sync_table
from functools import partial

# Set up the connection
cloud_config = {
    'secure_connect_bundle': '/path/secure_connect_bundle.zip'
}
auth_provider = PlainTextAuthProvider(username='', password='') # Input your username and password
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect()
connection.set_session(session)

# Define the data model using cqlengine ORM
class UserWalletCurrentHoldingCS(Model):
    __keyspace__ = "ks1"
    __table_name__ = "user_wallet_current_holding"

    # Primary keys
    user_id = columns.Text(primary_key=True, partition_key=True)
    user_wallet_id = columns.Text(primary_key=True, partition_key=False)
    asset_id = columns.Text(primary_key=True, partition_key=False)
    id = columns.Text(primary_key=True, partition_key=False)

    # Additional columns
    quantity = columns.Float()
    price = columns.Float()
    value = columns.Float()
    cost_basis = columns.Float()
    portfolio_allocation = columns.Float()
    wallet_allocation = columns.Float()
    company_valuation = columns.Float()
    percent_ownership = columns.Float()
    price_1d_ago = columns.Float()
    quantity_1d_ago = columns.Float()
    value_1d_ago = columns.Float()
    verified = columns.Boolean()

# Sync the model with Cassandra to create the table
sync_table(UserWalletCurrentHoldingCS)

# Sample data to insert
sample_data = [
    {
        'user_id': 'user1',
        'user_wallet_id': 'wallet1',
        'asset_id': 'asset1',
        'id': 'id1',
        'quantity': 10.0,
        'price': 100.0,
        'value': 1000.0,
        'cost_basis': 900.0,
        'portfolio_allocation': 0.5,
        'wallet_allocation': 0.7,
        'company_valuation': 500000.0,
        'percent_ownership': 0.02,
        'price_1d_ago': 95.0,
        'quantity_1d_ago': 10.0,
        'value_1d_ago': 950.0,
        'verified': True,
    },
    {
        'user_id': 'user2',
        'user_wallet_id': 'wallet2',
        'asset_id': 'asset2',
        'id': 'id2',
        'quantity': 15.0,
        'price': 200.0,
        'value': 3000.0,
        'cost_basis': 2500.0,
        'portfolio_allocation': 0.6,
        'wallet_allocation': 0.8,
        'company_valuation': 750000.0,
        'percent_ownership': 0.03,
        'price_1d_ago': 190.0,
        'quantity_1d_ago': 15.0,
        'value_1d_ago': 2850.0,
        'verified': False,
    },
    {
        'user_id': 'user3',
        'user_wallet_id': 'wallet3',
        'asset_id': 'asset3',
        'id': 'id3',
        'quantity': 20.0,
        'price': 150.0,
        'value': 3000.0,
        'cost_basis': 2800.0,
        'portfolio_allocation': 0.4,
        'wallet_allocation': 0.5,
        'company_valuation': 600000.0,
        'percent_ownership': 0.025,
        'price_1d_ago': 145.0,
        'quantity_1d_ago': 20.0,
        'value_1d_ago': 2900.0,
        'verified': True,
    },
    {
        'user_id': 'user4',
        'user_wallet_id': 'wallet4',
        'asset_id': 'asset4',
        'id': 'id4',
        'quantity': 5.0,
        'price': 500.0,
        'value': 2500.0,
        'cost_basis': 2300.0,
        'portfolio_allocation': 0.3,
        'wallet_allocation': 0.6,
        'company_valuation': 800000.0,
        'percent_ownership': 0.015,
        'price_1d_ago': 480.0,
        'quantity_1d_ago': 5.0,
        'value_1d_ago': 2400.0,
        'verified': True,
    },
    {
        'user_id': 'user5',
        'user_wallet_id': 'wallet5',
        'asset_id': 'asset5',
        'id': 'id5',
        'quantity': 50.0,
        'price': 20.0,
        'value': 1000.0,
        'cost_basis': 950.0,
        'portfolio_allocation': 0.2,
        'wallet_allocation': 0.3,
        'company_valuation': 400000.0,
        'percent_ownership': 0.01,
        'price_1d_ago': 19.0,
        'quantity_1d_ago': 50.0,
        'value_1d_ago': 950.0,
        'verified': False,
    }
    # Add more sample data as needed
]

# Asynchronous function to insert data
async def insert_data_async(data):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        partial(UserWalletCurrentHoldingCS.create, **data)
    )

# Asynchronous function to query data
async def query_data_async(user_id, user_wallet_id, asset_id, id):
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None,
        lambda: UserWalletCurrentHoldingCS.objects(
            user_id=user_id,
            user_wallet_id=user_wallet_id,
            asset_id=asset_id,
            id=id
        ).first()
    )
    return result

# Main asynchronous function
async def main():
    # Insert data concurrently
    insert_tasks = [insert_data_async(data) for data in sample_data]
    await asyncio.gather(*insert_tasks)

    # Query data concurrently
    query_tasks = [
        query_data_async(
            data['user_id'],
            data['user_wallet_id'],
            data['asset_id'],
            data['id']
        )
        for data in sample_data
    ]
    results = await asyncio.gather(*query_tasks)

    # Print the results
    for result in results:
        if result:
            print(f"User ID: {result.user_id}, Wallet ID: {result.user_wallet_id}, "
                  f"Asset ID: {result.asset_id}, Value: {result.value}")
        else:
            print("Record not found")

# Run the main function
asyncio.run(main())

# Close the session when done
session.shutdown()
cluster.shutdown()
