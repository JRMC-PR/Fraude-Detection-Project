import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime, timedelta
import re

# Load the data
data = pd.read_csv("path/to/data.csv")

# Convert date columns to datetime
data['REPORT_DATE'] = pd.to_datetime(data['REPORT_DATE'])
data['EVENT_TIME'] = pd.to_datetime(data['EVENT_TIME'])

# Normalize timezones (assuming the `TIMEZONE` column contains UTC offsets like "+02:00")
def normalize_time(row):
    try:
        return row['EVENT_TIME'].tz_localize(row['TIMEZONE']).astimezone(datetime.timezone.utc)
    except Exception:
        return row['EVENT_TIME']

data['EVENT_TIME_UTC'] = data.apply(normalize_time, axis=1)

# Extract numerical parts from USER_NAME for variation analysis
data['NUMERIC_PART'] = data['USER_NAME'].apply(lambda x: int(re.sub(r'\D', '', x)) if re.search(r'\d', x) else 0)

# Group data by USER_ID for time-based analysis
user_login_profiles = data.groupby('USER_ID').agg(
    avg_login_hour=('EVENT_TIME_UTC', lambda x: x.dt.hour.mean()),
    std_login_hour=('EVENT_TIME_UTC', lambda x: x.dt.hour.std())
).reset_index()

# Join the profiles back to the original data
data = data.merge(user_login_profiles, on='USER_ID', how='left')

# Compute deviation from the user's average login hour
data['hour_deviation'] = abs(data['EVENT_TIME_UTC'].dt.hour - data['avg_login_hour'])

# Feature for multiple login attempts within 1 second
data['login_burst'] = data.groupby(['USER_ID', 'EVENT_TIME_UTC']).cumcount() + 1

# Feature for multiple users logging in from the same IP in a short timeframe
ip_group = data.groupby(['IP_ADDRESS', pd.Grouper(key='EVENT_TIME_UTC', freq='1S')])
data['users_per_ip'] = ip_group['USER_ID'].transform('nunique')

# Features for anomaly detection
anomaly_features = ['hour_deviation', 'NUMERIC_PART', 'login_burst', 'users_per_ip']

# Fill NaNs (for cases where no deviations exist yet)
data[anomaly_features] = data[anomaly_features].fillna(0)

# Anomaly Detection Model
model = IsolationForest(contamination=0.01, random_state=42)
data['anomaly_score'] = model.fit_predict(data[anomaly_features])

# Rule-based detection
data['rule_violation'] = (
    (data['login_burst'] > 3) |  # Too many login attempts within 1 second
    (data['users_per_ip'] > 5)  # Too many users logging in from the same IP in 1 second
)

# Combine model and rules for final detection
data['brute_force_detected'] = (data['anomaly_score'] == -1) | (data['rule_violation'])

# Save results
data.to_csv("brute_force_detection_results.csv", index=False)

# Output summary
print("Brute force detection summary:")
print(data['brute_force_detected'].value_counts())
