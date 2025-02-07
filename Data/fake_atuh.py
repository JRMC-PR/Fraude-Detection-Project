import pandas as pd
import random
import uuid
from faker import Faker

# Initialize Faker for generating fake data
fake = Faker()

# Define possible EVENT values
EVENTS = [
    "PIN_REQUEST_CC_SUCCESS", "AA_SIGNATURE_PLUS_ACCEPT_TC", "AA_SIGNATURE_PLUS_VI_ACCEPT_TC",
    "ACCEPTED_DOCUMENTS", "ACCEPTED_UNICA_OFFER", "ACTIVATE_ATH_ERROR", "ACTIVATE_ATH_INT_ERROR",
    "ACTIVATE_ATH_INT_SUCCESS", "ACTIVATE_ATH_SUCCESS", "ACTIVATE_CC_ERROR", "ACTIVATE_CC_SUCCESS",
    "ACTIVATED_CCA_EBILL", "ACTIVATED_CCA_PURCHASE_SMS_ALERT", "ADD_AUTH_USER_ERROR",
    "ADD_AUTH_USER_SUCCESS", "ADD_PUSHNOTIFICATION_SUCCESS", "ADD_PUSHTOKEN_SUCCESS",
    "ADD_SMS_ALERTS", "ADDRESS_CHANGE", "ANALYTICS_COOKIES_ACTIVATION",
    "BLACK_DUAL_ACCEPT_TC", "CARD_OFF_SUCCESS", "CARD_ON_SUCCESS", "CHANGE_EMAIL_FAIL",
    "CHANGE_EMAIL_SUCCESS", "CHANGE_PASSWORD_FAIL", "CHANGE_PASSWORD_SUCCESS",
    "CUSTOMER_TENURE_BLOCK", "DEVICE_AUTH_BLOCK", "DEVICE_AUTH_EMAIL_SUCCESS",
    "DEVICE_AUTH_SMS_SUCCESS", "ENROLL_UPGRADE", "FAILED_TENURE_RULES", "FREQUENCY_ALWAYS_OOB",
    "FREQUENCY_AS_REQUIRED_OOB", "IN_APP_PROVISIONING_SUCCESS", "MFA_SMS_SUCCESS",
    "MOBILE_CASH_TR_ASSIGN_ATM", "OOB_AUTHENTICATION_SUCCESS", "PASSWORD_RESET_SUCCESS",
    "RECOVER_USERNAME_SUCCESS", "REQUEST_CARD_SUCCESS", "REMOTE_DEPOSIT_SUCCESS",
    "REGAIN_ACCESS_ACCT_SUCCESS", "SIGNON_SUCCESS", "TRANSFER_SEND", "UPDATE_SMS_ALERTS",
    "VALIDATE_ACCOUNT_INF_SUCCESS", "VIEW_PDF_STMT"
]

# Define severity levels
SEVERITY_LEVELS = ["info", "warning"]

# Number of rows to generate
NUM_RECORDS = 10000

# Function to generate fake event timestamps
def generate_event_time():
    return fake.date_time_this_decade().strftime("%d%m%y%H:%M:%S")  # Format as ddmmyyH:M:S

# Generate fake dataset
data = []
for _ in range(NUM_RECORDS):
    record = {
        "ID": str(uuid.uuid4()),  # Generate a unique UUID
        "PROFILE_ID": str(uuid.uuid4()),  # Generate a unique PROFILE_ID
        "EVENT_DATE": generate_event_time(),  # Generate a fake event time
        "USERNAME": fake.user_name(),  # Fake username
        "EVENT": random.choice(EVENTS),  # Select a random event from the list
        "IP": fake.ipv4(),  # Generate a valid IPv4 address
        "SESSIONID": str(uuid.uuid4()),  # Generate a unique SESSIONID
        "SEVERITY": random.choice(SEVERITY_LEVELS),  # Randomly assign 'info' or 'warning'
        "SERVER": f"server-{random.randint(1, 100)}",  # Randomly generate a server ID
        "TRACE": fake.sentence(nb_words=6),  # Generate fake phone trace information
        "REPORT_DATE": generate_event_time(),  # Generate a fake report date
        "LOAD_DATE": generate_event_time(),  # Generate a fake load date
    }
    data.append(record)

# Convert to Pandas DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("fake_auth_dataset.csv", index=False)

print("✅ Fake dataset 'fake_dataset.csv' created successfully!")
