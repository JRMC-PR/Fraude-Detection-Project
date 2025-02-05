import pandas as pd
import numpy as np
from hmmlearn import hmm
from tensorflow.keras.models import Sequential #type: ignore
from tensorflow.keras.layers import LSTM, Dense #type: ignore
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

def build_user_history(csv_path):
    """
    Reads CSV and builds a historical profile for each USER_ID using HMM and LSTM.

    Adjusts EVENT_TIME based on TIMEZONE.

    Parameters:
        csv_path (str): Path to the CSV file.

    Returns:
        dict: A dictionary with USER_IDs as keys and their processed history as values.
    """
    # Load CSV data
    df = pd.read_csv(csv_path)

    # Select relevant columns for user profiling
    features = ['USER_NAME', 'DATA_S_1', 'IP_ADDRESS', 'IP_CITY', 'TIMEZONE',
                'EVENT_TIME', 'DATA_S_4', 'DATA_S_34', 'RISK_SCORE']

    df = df[['USER_ID'] + features]  # Keep USER_ID as anchor

    # Convert TIMEZONE column to numeric (ensure it's an integer)
    df['TIMEZONE'] = pd.to_numeric(df['TIMEZONE'], errors='coerce').fillna(0).astype(int)

    # Convert EVENT_TIME to numeric and adjust based on TIMEZONE
    df['EVENT_TIME'] = pd.to_numeric(df['EVENT_TIME'], errors='coerce').fillna(0)
    df['EVENT_TIME'] = df['EVENT_TIME'] + df['TIMEZONE']  # Adjust based on timezone

    # Encode categorical data (USER_NAME, DATA_S_1, IP_ADDRESS, IP_CITY, TIMEZONE, DATA_S_34)
    label_encoders = {}
    for col in ['USER_NAME', 'DATA_S_1', 'IP_ADDRESS', 'IP_CITY', 'DATA_S_34']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le  # Store encoders for future use

    # Normalize numerical values (EVENT_TIME, DATA_S_4, RISK_SCORE)
    scaler = MinMaxScaler()
    df[['EVENT_TIME', 'DATA_S_4', 'RISK_SCORE']] = scaler.fit_transform(df[['EVENT_TIME', 'DATA_S_4', 'RISK_SCORE']])

    # Group data by USER_ID
    user_history = {}

    for user_id, group in df.groupby('USER_ID'):
        group = group.drop(columns=['USER_ID'])  # Remove USER_ID column

        # Convert history into a numerical sequence
        sequence = group.to_numpy()

        # Train Hidden Markov Model (HMM) to model user behavior
        hmm_model = hmm.GaussianHMM(n_components=3, covariance_type="diag", n_iter=100)
        hmm_model.fit(sequence)
        hidden_states = hmm_model.predict(sequence)  # Predict state transitions

        # Prepare data for LSTM model
        X = sequence[:-1]  # Inputs (all but last)
        y = sequence[1:]   # Outputs (shifted by one step)

        # Reshape for LSTM
        X = X.reshape((X.shape[0], X.shape[1], 1))
        y = y.reshape((y.shape[0], y.shape[1]))

        # Define LSTM model for predicting user activity
        lstm_model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)),  # First LSTM layer
            LSTM(32, return_sequences=False),  # Second LSTM layer
            Dense(y.shape[1])  # Output layer matching feature count
        ])

        lstm_model.compile(optimizer='adam', loss='mse')

        # Train LSTM model
        lstm_model.fit(X, y, epochs=15, batch_size=1, verbose=1)

        # Store trained models & history
        user_history[user_id] = {
            "hmm_model": hmm_model,
            "lstm_model": lstm_model,
            "history_data": group,
            "hidden_states": hidden_states
        }

    return user_history  # Pass this to the next model

# Example usage:
csv_path = "path/to/auth_log.csv"
user_profiles = build_user_history(csv_path)

# Print stored user profiles
for user, data in user_profiles.items():
    print(f"User {user}: Hidden States = {data['hidden_states']}")
