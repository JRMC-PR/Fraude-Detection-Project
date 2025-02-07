import pandas as pd
import numpy as np
import hdbscan
import re
import pickle
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import tensorflow as tf
import os

# Force TensorFlow to use CPU only
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
tf.config.set_visible_devices([], 'GPU')



# 📌 Function to load user history from a .pkl file
def load_user_history(pickle_path):
    """
    Loads user history from a pickle (.pkl) file.

    Parameters:
        pickle_path (str): Path to the user history pickle file.

    Returns:
        dict: Loaded user history data.
    """
    try:
        with open(pickle_path, "rb") as file:
            return pickle.load(file)  # Load user history dictionary
    except FileNotFoundError:
        print(f"\n❌ Error: File '{pickle_path}' not found.")
        return {}
    except Exception as e:
        print(f"\n❌ Error loading pickle file: {e}")
        return {}

# 📌 Function to extract numbers from a username
def extract_numbers_and_clean(username):
    """
    Extracts numerical values from a username and returns the cleaned username.

    Parameters:
        username (str): The username to process.

    Returns:
        tuple: (cleaned username, extracted numbers as a concatenated string)
    """
    numbers = ''.join(re.findall(r'\d+', username))  # Extract numerical values
    cleaned_id = re.sub(r'\d+', '', username)  # Remove numbers from username
    return cleaned_id, numbers

# 📌 Main fraud detection function
def run_fraud_detection(auth_path, user_history_path):
    """
    Detects fraud patterns in login attempts using HDBSCAN & Isolation Forest.

    Parameters:
        auth_path (str): Path to the authentication log file (AUTH.csv).
        user_history_path (str): Path to the user history pickle file.

    Saves:
        - processed_login_attempts.csv (Preprocessed login data)
        - detected_anomalies.csv (Flagged anomalies)
    """
    try:
        # Load user history from pickle file
        user_history = load_user_history(user_history_path)
        if not user_history:
            print("\n❌ No user history found. Exiting fraud detection.")
            return

        # Load authentication log
        df_auth = pd.read_csv(auth_path)

        # Ensure required columns exist in the AUTH log
        required_columns = {"ID", "PROFILE_ID", "EVENT_DATE", "USERNAME", "EVENT", "IP", "SESSIONID"}
        if not required_columns.issubset(df_auth.columns):
            raise ValueError(f"CSV file must contain columns: {required_columns}")

        # Convert EVENT_DATE to datetime format
        df_auth["EVENT_DATE"] = pd.to_datetime(df_auth["EVENT_DATE"], format="%d%m%y%H:%M:%S")

        # Extract numbers from USERNAME for anomaly detection
        df_auth["CLEANED_USERNAME"], df_auth["EXTRACTED_NUMBERS"] = zip(*df_auth["USERNAME"].apply(extract_numbers_and_clean))

        ### 📌 **1️⃣ Detect Numerical Value Attacks (Guessing Usernames)**
        df_invalid_usernames = df_auth[df_auth["EVENT"] == "INVALID_USERNAME"]
        attacked_users = set()

        for _, row in df_invalid_usernames.iterrows():
            attempted_username = row["CLEANED_USERNAME"]
            attempted_numbers = row["EXTRACTED_NUMBERS"]

            for user_id in user_history.keys():
                cleaned_user_id, extracted_numbers = extract_numbers_and_clean(user_id)

                if cleaned_user_id == attempted_username and attempted_numbers != extracted_numbers:
                    attacked_users.add(user_id)

        print(f"\n🔍 Numerical value attack detected on: {attacked_users}")

        ### 📌 **2️⃣ Detect Multiple Users Logging in from the Same IP**
        ip_attempt_counts = df_auth.groupby("IP")["USERNAME"].nunique()
        suspicious_ips = ip_attempt_counts[ip_attempt_counts > 3].index.tolist()
        print(f"\n⚠️ Multiple users logging in from the same IP detected: {suspicious_ips}")

        ### 📌 **3️⃣ Detect Brute-Force Attacks (Repeated Attempts in Short Time)**
        df_auth.sort_values(by=["USERNAME", "EVENT_DATE"], inplace=True)
        df_auth["TIME_DIFF"] = df_auth.groupby("USERNAME")["EVENT_DATE"].diff().dt.total_seconds()
        df_auth["IS_BRUTE_FORCE"] = df_auth["TIME_DIFF"] < 60
        brute_force_attempts = df_auth[df_auth["IS_BRUTE_FORCE"]]
        print("\n⚠️ Brute-force attack attempts detected:")
        print(brute_force_attempts[["USERNAME", "EVENT_DATE", "TIME_DIFF"]])

        ### 📌 **4️⃣ Detect Account Changes (Email, Password, Username Updates)**
        account_changes = df_auth[df_auth["EVENT"].isin(["CHANGE_EMAIL_SUCCESS", "CHANGE_PASSWORD_SUCCESS", "CHANGE_USERNAME_SUCCESS"])]
        print("\n🔍 Account changes detected:")
        print(account_changes[["USERNAME", "EVENT", "EVENT_DATE"]])

        ### 📌 **5️⃣ HDBSCAN for Outlier Detection**
        df_auth["LOGIN_COUNT"] = df_auth.groupby("USERNAME")["USERNAME"].transform("count")
        df_auth["UNIQUE_IP_COUNT"] = df_auth.groupby("USERNAME")["IP"].transform("nunique")
        df_auth["AVG_TIME_DIFF"] = df_auth.groupby("USERNAME")["TIME_DIFF"].transform("mean")

        # Prepare data for clustering
        features = ["LOGIN_COUNT", "UNIQUE_IP_COUNT", "AVG_TIME_DIFF"]
        df_auth[features] = df_auth[features].fillna(0)  # Handle missing values

        scaler = StandardScaler()
        df_auth_scaled = scaler.fit_transform(df_auth[features])

        # Run HDBSCAN clustering
        clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=2, metric="euclidean", cluster_selection_method="eom")
        df_auth["HDBSCAN_CLUSTER"] = clusterer.fit_predict(df_auth_scaled)

        # Mark HDBSCAN outliers (cluster -1)
        df_auth["HDBSCAN_ANOMALY"] = df_auth["HDBSCAN_CLUSTER"] == -1

        ### 📌 **6️⃣ Isolation Forest for Anomaly Detection**
        iso_forest = IsolationForest(contamination=0.05, random_state=42)
        df_auth["ISOLATION_SCORE"] = iso_forest.fit_predict(df_auth_scaled)

        # Mark Isolation Forest outliers (-1 means anomaly)
        df_auth["ISOLATION_ANOMALY"] = df_auth["ISOLATION_SCORE"] == -1

        ### 📌 **7️⃣ Flag Final Anomalies**
        df_auth["IS_ANOMALY"] = df_auth["HDBSCAN_ANOMALY"] | df_auth["ISOLATION_ANOMALY"]

        # Save results
        df_auth.to_csv("processed_login_attempts.csv", index=False)
        anomalies = df_auth[df_auth["IS_ANOMALY"]]
        anomalies.to_csv("detected_anomalies.csv", index=False)

        print("\n✅ Fraud detection complete! Check 'detected_anomalies.csv' for results.")

    except FileNotFoundError:
        print(f"\n❌ Error: The file '{auth_path}' was not found. Please check the path and try again.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")


