#!/usr/bin/env python3
<<<<<<< HEAD
"""  """
=======
"""Script to generate Synthetic Data"""
>>>>>>> 6930fc46cd10073b0063247c3d4a5497e92c8b27

import random
import pandas as pd
from faker import Faker

fake = Faker()

# Number of users
<<<<<<< HEAD
num_users = random.randint(0,85000)
=======
num_users = random.randint(75000, 85000)
>>>>>>> 6930fc46cd10073b0063247c3d4a5497e92c8b27

# Number of rows
num_rows = 1000000

# Generate user data
users = [fake.user_name() for _ in range(num_users)]

# Function to generate random data for each column
def generate_data():
    return {
        "ID": fake.uuid4(),
        "PROFILE_ID": fake.uuid4(),
        "EVENT_DATE": fake.date_time_this_decade(),
        "USERNAME": random.choice(users),
        "EVENT": fake.word(),
        "IP": fake.ipv4(),
        "SESSIONID": fake.uuid4(),
        "SEVERITY": random.choice(["Low", "Medium", "High"]),
        "SERVER": fake.hostname(),
        "TRACE": fake.sentence(),
        "REPORT_DATE": fake.date_time_this_decade(),
        "LOAD_DATE": fake.date_time_this_decade()
    }

# Generate the data
data = [generate_data() for _ in range(num_rows)]

# Create a DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("generated_logs.csv", index=False)

print("Data generation complete. Saved to 'generated_logs.csv'.")
