import random
import pandas as pd
from faker import Faker

fake = Faker()

# Number of users
num_users = random.randint(75000, 85000)

# Number of rows
num_rows = 1000000

# Generate user data
users = [fake.user_name() for _ in range(num_users)]

# Function to generate random data for each column
def generate_data():
    return {
        "REPORT_DATE": fake.date_time_this_decade(),
        "LASTMODIFIED": fake.date_time_this_decade(),
        "EVENT_ID": fake.uuid4(),
        "USER_ID": fake.uuid4(),
        "user": random.choice(users),
        "SESSION_ID": fake.uuid4(),
        "EVENT_TIME": fake.date_time_this_decade(),
        "EVENT_TYPE": fake.word(),
        "USER_DEFINED_EVENT_TYPE": fake.word(),
        "PRELIMINARY_SCORE": random.randint(1, 100),
        "RISK_SCORE": random.randint(1, 100),
        "PREV_RISK_SCORE": random.randint(1, 100),
        "PREV_RISK_SCORE_DATE": fake.date_time_this_decade(),
        "RISK_1_CONTRIBUTOR": fake.word(),
        "RISK_1_SCORE": random.randint(1, 100),
        "RISK_2_CONTRIBUTOR": fake.word(),
        "RISK_2_SCORE": random.randint(1, 100),
        "RISK_3_CONTRIBUTOR": fake.word(),
        "RISK_3_SCORE": random.randint(1, 100),
        "RISK_4_CONTRIBUTOR": fake.word(),
        "RISK_4_SCORE": random.randint(1, 100),
        "POLICY_RULE_ID": fake.uuid4(),
        "POLICY_ACTION": fake.word(),
        "TEST_POLICY_RULE_ID": fake.uuid4(),
        "TEST_POLICY_ACTION": fake.word(),
        "CHALLENGE_AUTH_METHOD": fake.word(),
        "CHALLENGE_SUCCESSFUL": fake.boolean(),
        "FLAGGED": fake.boolean(),
        "RESOLUTION": fake.word(),
        "RESOLUTION_DATE": fake.date_time_this_decade(),
        "COOKIE": fake.md5(),
        "USER_AGENT_STRING_HASH": fake.md5(),
        "SOFTWARE_FINGERPRINT_HASH": fake.md5(),
        "BROWSER_PLUGINS_HASH": fake.md5(),
        "SCREEN_HASH": fake.md5(),
        "ACCEPT_LANGUAGE": fake.language_code(),
        "BROWSER_LANGUAGE": fake.language_code(),
        "TIMEZONE": fake.timezone(),
        "IP_ADDRESS": fake.ipv4(),
        "IP_COUNTRY": fake.country(),
        "IP_REGION": fake.state(),
        "IP_CITY": fake.city(),
        "IP_ISP": fake.company(),
        "CHANNEL_INDICATOR": fake.word(),
        "IS_DEVICE_BOUND": fake.boolean(),
        "IS_FRAUD_SUSPECT": fake.boolean(),
        "FRAUD_SUSPECT_DATE": fake.date_time_this_decade(),
        "CALC_USER_RISK_SCORE": random.randint(1, 100),
        "USER_PERSISTENT": fake.boolean(),
        "DATA_S_1": fake.word(),
        "DATA_S_4": fake.word(),
        "PREV_DATA_S_4": fake.word(),
        "PREV_DATA_S_4_DATE": fake.date_time_this_decade(),
        "DATA_S_10": fake.word(),
        "DATA_S_11": fake.word(),
        "DATA_S_29": fake.word(),
        "DATA_S_30": fake.word(),
        "DATA_S_31": fake.word(),
        "DATA_S_34": fake.word(),
        "DATA_S_37": fake.word(),
        "PREV_DATA_S37": fake.word(),
        "PREV_DATA_S37_DATE": fake.date_time_this_decade(),
        "DATA_I_20": random.randint(1, 100),
        "DATA_I_23": random.randint(1, 100),
        "DATA_I_63": random.randint(1, 100),
        "DATA_S_76": fake.word(),
        "DATA_S_79": fake.word(),
        "MOBILE_AGE": random.randint(1, 10),
        "DATA_S_100": fake.word(),
        "TEST_RULE_FLAG": fake.boolean(),
        "DFP_AGE": random.randint(1, 10),
        "GEODISTANCE": random.uniform(0, 1000),
        "GEODATA_AGE": random.randint(1, 10),
        "OPERATING_SYSTEM": fake.word(),
        "BROWSER_TYPE": fake.word(),
        "BROWSER_VERSION": fake.word(),
        "IP_ISP_NAME": fake.company(),
        "IP_ISP_NAME_MODE": fake.word()
    }

# Generate the data
data = [generate_data() for _ in range(num_rows)]

# Create a DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("generated_loginsRSA.csv", index=False)

print("Data generation complete. Saved to 'generated_loginsRSA.csv'.")
