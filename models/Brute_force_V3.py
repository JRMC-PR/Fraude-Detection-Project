#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import joblib
import os

# Function to load the CSV data
def load_data(file_path):
    """Loads the CSV data and parses the REPORT_DATE column."""
    data = pd.read_csv(file_path)

    # Define date format to match bank data
    date_format = "%d%b%Y:%H:%M:%S"

    # error='coerce' will return NaT for any parsing errors
    data['REPORT_DATE'] = pd.to_datetime(data['REPORT_DATE'], format=date_format, errors='coerce')

    return data

# Function to train and apply Isolation Forest
def apply_isolation_forest(data, feature_columns, contamination=0.05, model_name="isolation_forest_model.pkl"):
    """Trains Isolation Forest, saves the model, and predicts anomalies."""
    # Check for NaN values in feature columns
    if data[feature_columns].isna().any().any():
        raise ValueError(f"Input data contains NaN values in columns: {feature_columns}. Please handle missing values before calling Isolation Forest.")

    # Check if the model already exists
    if os.path.exists(model_name):
        print(f"Loading saved Isolation Forest model: {model_name}")
        model = joblib.load(model_name)
    else:
        # Train a new Isolation Forest model
        print(f"Training new Isolation Forest model and saving it as: {model_name}")
        model = IsolationForest(contamination=contamination, random_state=42)
        model.fit(data[feature_columns])

        # Save the trained model
        joblib.dump(model, model_name)

    # Predict anomalies
    data['anomaly_score'] = model.predict(data[feature_columns])
    return data

# Flag 1: Detect username variations with Isolation Forest
def detect_username_variations(data):
    """Uses Isolation Forest to detect username variations."""
    # Feature: USER_NAME encoded to numerical hashes
    data['USER_NAME_HASH'] = data['USER_NAME'].apply(hash).astype(np.int64)
    feature_columns = ['USER_NAME_HASH']

    # Use a unique model name for Flag 1
    model_name = "flag1_username_variations.pkl"
    flagged_data = apply_isolation_forest(data, feature_columns, model_name=model_name)
    anomalies = flagged_data[flagged_data['anomaly_score'] == -1]

    # Filter for successful logins
    flagged_anomalies = anomalies[anomalies['EVENT_TYPE'] == 'successful_login']
    return flagged_anomalies

# Flag 2: Detect multiple users logging in from the same IP
def detect_multiple_users_same_ip(data, contamination=0.05):
    """Uses Isolation Forest to detect multiple users from the same IP address."""
    # Group data by IP and count unique USER_IDs per IP
    ip_grouped = data.groupby('IP_ADDRESS').agg({'USER_ID': 'nunique'}).reset_index()
    ip_grouped.columns = ['IP_ADDRESS', 'UNIQUE_USERS']

    # Use a unique model name for Flag 2
    model_name = "flag2_multiple_users_same_ip.pkl"
    flagged_data = apply_isolation_forest(ip_grouped, feature_columns=['UNIQUE_USERS'], contamination=contamination, model_name=model_name)
    anomalies = flagged_data[flagged_data['anomaly_score'] == -1]

    # Match anomalies with the original dataset
    flagged_ips = anomalies['IP_ADDRESS'].tolist()
    flagged_rows = data[data['IP_ADDRESS'].isin(flagged_ips) & (data['EVENT_TYPE'] == 'successful_login')]
    return flagged_rows

# Flag 3: Detect logins outside regular hours
def detect_logins_outside_regular_hours(data, contamination=0.05):
    """Uses Isolation Forest to detect logins outside of regular hours."""
    # Extract hour from REPORT_DATE
    data['LOGIN_HOUR'] = data['REPORT_DATE'].dt.hour

    # Learn regular login hours for each user
    user_grouped = data.groupby('USER_ID').agg({'LOGIN_HOUR': 'mean'}).reset_index()
    user_grouped.columns = ['USER_ID', 'AVG_LOGIN_HOUR']

    # Add deviation feature
    user_grouped['HOUR_DEVIATION'] = data.groupby('USER_ID').LOGIN_HOUR.std()

    # Ensure only numeric columns are used
    numeric_columns = ['AVG_LOGIN_HOUR', 'HOUR_DEVIATION']

    # Debug: Check for NaN values before handling them
    print("Before handling NaN values:")
    print(user_grouped.isna().sum())

    # Fill missing values with defaults
    user_grouped['AVG_LOGIN_HOUR'].fillna(12, inplace=True)  # Default to noon if no mean login hour
    user_grouped['HOUR_DEVIATION'].fillna(0, inplace=True)  # Default to 0 if no deviation exists

    # Debug: Check for remaining NaN values after filling
    print("After handling NaN values:")
    print(user_grouped.isna().sum())

    # Use a unique model name for Flag 3
    model_name = "flag3_login_hours.pkl"
    flagged_data = apply_isolation_forest(user_grouped, feature_columns=numeric_columns, contamination=contamination, model_name=model_name)
    anomalies = flagged_data[flagged_data['anomaly_score'] == -1]

    # Match anomalies back to original data
    flagged_users = anomalies['USER_ID'].tolist()
    flagged_rows = data[data['USER_ID'].isin(flagged_users)]
    return flagged_rows

# Flag 4: Detect excessive login attempts
def detect_excessive_login_attempts(data, contamination=0.05):
    """Uses Isolation Forest to detect excessive login attempts."""
    # Create a feature for login attempts in 1-minute windows
    data['time_bucket'] = data['REPORT_DATE'].dt.floor('1T')  # Bucket by minute
    user_grouped = data.groupby(['USER_ID', 'time_bucket']).size().reset_index(name='ATTEMPT_COUNT')

    # Use a unique model name for Flag 4
    model_name = "flag4_excessive_login_attempts.pkl"
    flagged_data = apply_isolation_forest(user_grouped, feature_columns=['ATTEMPT_COUNT'], contamination=contamination, model_name=model_name)
    anomalies = flagged_data[flagged_data['anomaly_score'] == -1]

    # Match anomalies back to original data
    flagged_users = anomalies['USER_ID'].tolist()
    flagged_rows = data[data['USER_ID'].isin(flagged_users)]
    return flagged_rows

# Save results to files
def save_results(fraud_data, summary_data, report_date):
    """Saves fraud detection results and summary to CSV files."""
    fraud_file = f"Fraud_{report_date}.csv"
    summary_file = f"Summary_{report_date}.csv"
    fraud_data.to_csv(fraud_file, index=False)
    summary_data.to_csv(summary_file, index=False)
    print(f"Saved fraud report to {fraud_file}")
    print(f"Saved summary report to {summary_file}")

# Main function
def main(input_file):
    # Load data
    data = load_data(input_file)
    report_date = data['REPORT_DATE'].iloc[0].strftime('%Y-%m-%d')

    # Initialize summary dictionary
    summary = {'USR_ID': [], 'Flag_1': [], 'Flag_2': [], 'Flag_3': [], 'Flag_4': [], 'Flag_5': [], 'Flag_6': [], 'User_IP': [], 'Date': []}

    # Apply Isolation Forest for each flag
    flag1_data = detect_username_variations(data)
    flag2_data = detect_multiple_users_same_ip(data)
    flag3_data = detect_logins_outside_regular_hours(data)
    flag4_data = detect_excessive_login_attempts(data)

    # Populate summary
    for user_id in data['USER_ID'].unique():
        summary['USR_ID'].append(user_id)
        summary['Flag_1'].append(flag1_data['USER_ID'].tolist().count(user_id))
        summary['Flag_2'].append(flag2_data['USER_ID'].tolist().count(user_id))
        summary['Flag_3'].append(flag3_data['USER_ID'].tolist().count(user_id))
        summary['Flag_4'].append(flag4_data['USER_ID'].tolist().count(user_id))
        summary['Flag_5'].append(None)  # Placeholder
        summary['Flag_6'].append(None)  # Placeholder
        summary['User_IP'].append(data[data['USER_ID'] == user_id]['IP_ADDRESS'].iloc[0])
        summary['Date'].append(report_date)

    # Combine fraud reports
    fraud_reports = pd.concat([flag1_data, flag2_data, flag3_data, flag4_data], ignore_index=True)

    # Save results
    save_results(fraud_reports, pd.DataFrame(summary), report_date)

if __name__ == "__main__":
    input_file = "/home/vaiosos/Documents/Holberton/Fraude-Detection-Project/Data/cleaned_RSA.csv"  # Replace with your actual file
    main(input_file)
