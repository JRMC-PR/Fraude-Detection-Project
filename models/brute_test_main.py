from brute_testing import run_fraud_detection  # Import your fraud detection function

# Define paths for the authentication log and user history
AUTH_LOG_PATH = "/home/vaiosos/Documents/Holberton/Fraude-Detection-Project/Data/fake_auth_dataset.csv"
USER_HISTORY_PATH = "/home/vaiosos/Documents/Holberton/Fraude-Detection-Project/models/user_history.pkl"

# Run fraud detection using the given files
if __name__ == "__main__":
    print("🚀 Starting Fraud Detection...")
    run_fraud_detection(AUTH_LOG_PATH, USER_HISTORY_PATH)
    print("✅ Fraud Detection Completed! Check 'detected_anomalies.csv' for results.")
