import pandas as pd
import numpy as np
import os
import pickle  # For storing user history
from datetime import datetime, timedelta
from hmmlearn import hmm
from tensorflow.keras.models import Sequential  #type: ignore
from tensorflow.keras.layers import LSTM, Dense #type: ignore
import tensorflow as tf

# Disable GPU for compatibility
tf.config.set_visible_devices([], 'GPU')

# Define file to store user history
HISTORY_FILE = "user_history.pkl"

def load_user_history():
    """Load existing user history from a pickle file, or return an empty dictionary if it doesn't exist."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "rb") as f:
            return pickle.load(f)
    return {}  # Return empty dict if no history exists

def save_user_history(user_history):
    """Save user history to a pickle file."""
    with open(HISTORY_FILE, "wb") as f:
        pickle.dump(user_history, f)

def parse_event_time(event_time, timezone_offset=0):
    """Adjust EVENT_TIME based on the user's timezone."""
    try:
        dt = datetime.strptime(event_time, "%d%b%Y:%H:%M:%S")
        dt = dt + timedelta(hours=int(timezone_offset))  # Adjust for timezone
        return dt.strftime("%d%b%Y:%H:%M:%S")  # Return adjusted time
    except Exception as e:
        print(f"❌ Error parsing time {event_time}: {e}")
        return event_time  # Return original if error occurs

def build_user_history(csv_path):
    """Process user data, accumulate history, and train HMM/LSTM models."""

    # Load existing history
    user_history = load_user_history()

    # Load new data
    df = pd.read_csv(csv_path)

    # Relevant features
    features = ['USER_ID', 'USER_NAME', 'DATA_S_1', 'IP_ADDRESS', 'IP_CITY', 'TIMEZONE',
                'EVENT_TIME', 'DATA_S_4', 'DATA_S_34', 'RISK_SCORE', 'EVENT_TYPE']
    df = df[features]

    # Preprocess data
    df['USER_NAME'] = df['USER_NAME'].astype(str)
    df['IP_ADDRESS'] = df['IP_ADDRESS'].astype(str)
    df['TIMEZONE'] = pd.to_numeric(df['TIMEZONE'], errors='coerce').fillna(0).astype(int)
    df['EVENT_TIME'] = df.apply(lambda row: parse_event_time(str(row['EVENT_TIME']), row['TIMEZONE']), axis=1)
    df['DATA_S_4'] = pd.to_numeric(df['DATA_S_4'], errors='coerce').fillna(0).astype(int)
    df['DATA_S_34'] = df['DATA_S_34'].astype(str)

    print("\n📊 DEBUG: First few records after preprocessing:")
    print(df.head())

    # Process each user
    for user_id, group in df.groupby('USER_ID'):
        group = group.drop(columns=['USER_ID'])  # Remove USER_ID from the dataframe

        # If user exists in history, append new data
        if user_id in user_history:
            prev_data = user_history[user_id]["history_data"]
            group = pd.concat([prev_data, group])  # Append new records

        # Convert to numerical sequences
        sequence = group.select_dtypes(include=[np.number]).to_numpy()

        # Skip users with fewer than 3 total records
        if len(sequence) < 3:
            print(f"⚠️ Skipping {user_id} (Only {len(sequence)} records, waiting for more data...)")
            user_history[user_id] = {
                "hmm_model": None,
                "lstm_model": None,
                "history_data": group,  # Store history for future runs
                "hidden_states": [-1] * len(sequence)
            }
            continue  # Skip training for now

        # Train HMM Model
        n_components = min(len(sequence), 3)  # Adjust the number of states
        hmm_model = hmm.GaussianHMM(n_components=n_components, covariance_type="diag", n_iter=100)
        hmm_model.fit(sequence)

        # Fix transition matrix if needed
        if not hasattr(hmm_model, "transmat_") or np.any(hmm_model.transmat_ == 0):
            print(f"⚠️ Fixing transition matrix for {user_id}")
            hmm_model.transmat_ = np.full((n_components, n_components), 1.0 / n_components)

        hidden_states = hmm_model.predict(sequence)

        # Prepare data for LSTM
        X = sequence[:-1]  # Inputs
        y = sequence[1:]   # Outputs

        X = X.reshape((X.shape[0], X.shape[1], 1))  # Reshape for LSTM
        y = y.reshape((y.shape[0], y.shape[1]))

        # Define LSTM model
        lstm_model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)),
            LSTM(32, return_sequences=False),
            Dense(y.shape[1])
        ])
        lstm_model.compile(optimizer='adam', loss='mse')

        # Train only if data is sufficient
        if len(X) > 0 and len(y) > 0:
            lstm_model.fit(X, y, epochs=15, batch_size=1, verbose=1)
        else:
            print(f"⚠️ Skipping LSTM training for {user_id} (Not enough data)")
            lstm_model = None

        # Save trained models and history
        user_history[user_id] = {
            "hmm_model": hmm_model,
            "lstm_model": lstm_model,
            "history_data": group,  # Save complete history
            "hidden_states": hidden_states
        }

    # Save updated history
    save_user_history(user_history)

    return user_history
