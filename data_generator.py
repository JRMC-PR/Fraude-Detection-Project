#!/usr/bin/env python3
""" Generate synthetic data for Client Information Table """

import pandas as pd
import random
from faker import Faker

fake = Faker()

# Generate synthetic data for Client Information Table
def generate_client_info(rows=20000):
    """ Generate synthetic data for Client Information Table """
    client_data = {
        "client_id": [fake.uuid4() for _ in range(rows)],
        "first_name": [fake.first_name() for _ in range(rows)],
        "last_name": [fake.last_name() for _ in range(rows)],
        "address": [fake.address().replace("\n", ", ") for _ in range(rows)],
        "email": [fake.email() for _ in range(rows)],
        "phone_number": [fake.phone_number() for _ in range(rows)],
        "account_creation_date": [fake.date_between(start_date='-10y', end_date='today') for _ in range(rows)],
        "account_status": [random.choice(["active", "inactive", "suspended", "closed"]) for _ in range(rows)],
    }
    return pd.DataFrame(client_data)

# Generate data and save as CSV
client_info = generate_client_info()
client_info.to_csv("client_info.csv", index=False)

# Print first few rows
print(client_info.head())
