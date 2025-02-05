import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hmmlearn import hmm
from tensorflow.keras.models import Sequential #type: ignore
from tensorflow.keras.layers import LSTM, Dense #type: ignore
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# Mapping of month abbreviations to numeric values
MONTH_MAP = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
    "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
}

def parse_event_time(event_time):
    """Ensures EVENT_TIME remains in 'DDMMMYYYY:HH:MM:SS' format."""
    try:
        # Validate format
        if len(event_time) >= 15:
            return event_time  # Keep original format
        else:
            raise ValueError("Incorrect event time format")
    except Exception as e:
        print(f"❌ Error processing time {event_time}: {e}")
        return None

def build_user_history(csv_path):
    """Builds user history with correctly formatted fields."""

    # Load CSV data
    df = pd.read_csv(csv_path)

    # Select relevant columns
    features = ['USER_ID', 'USER_NAME', 'DATA_S_1', 'IP_ADDRESS', 'IP_CITY', 'TIMEZONE',
                'EVENT_TIME', 'DATA_S_4', 'DATA_S_34', 'RISK_SCORE', 'EVENT_TYPE']

    df = df[features]  # Keep USER_ID as anchor

    # ✅ Ensure USER_NAME is treated as a string
    df['USER_NAME'] = df['USER_NAME'].astype(str)

    # ✅ Keep IP_ADDRESS as is (do not encode it)
    df['IP_ADDRESS'] = df['IP_ADDRESS'].astype(str)

    # ✅ Ensure EVENT_TIME is kept in its original format
    df['EVENT_TIME'] = df['EVENT_TIME'].apply(parse_event_time)

    # ✅ Ensure DATA_S_4 is an integer (device age)
    df['DATA_S_4'] = pd.to_numeric(df['DATA_S_4'], errors='coerce').fillna(0).astype(int)

    # ✅ Keep DATA_S_34 in its original form
    df['DATA_S_34'] = df['DATA_S_34'].astype(str)

    # Print first few records for debugging
    print("\n📊 DEBUG: First few records after preprocessing:")
    print(df.head())

    # Group data by USER_ID
    user_history = {}

    for user_id, group in df.groupby('USER_ID'):
        group = group.drop(columns=['USER_ID'])  # Remove USER_ID column

        # Convert history into a numerical sequence (except categorical features)
        sequence = group.select_dtypes(include=[np.number]).to_numpy()

        # Skip HMM training for users with fewer than 3 events
        if len(sequence) < 3:
            print(f"⚠️ Skipping HMM training for {user_id} (Not enough data: {len(sequence)} records)")
            user_history[user_id] = {
                "hmm_model": None,
                "lstm_model": None,
                "history_data": group,
                "hidden_states": [-1] * len(sequence)  # Default state for sparse users
            }
            continue

        # Train HMM Model
        hmm_model = hmm.GaussianHMM(n_components=min(3, len(sequence)), covariance_type="diag", n_iter=100)
        hmm_model.fit(sequence)
        hidden_states = hmm_model.predict(sequence)

        # Prepare data for LSTM
        X = sequence[:-1]  # Inputs (all but last)
        y = sequence[1:]   # Outputs (shifted by one step)

        X = X.reshape((X.shape[0], X.shape[1], 1))
        y = y.reshape((y.shape[0], y.shape[1]))

        # Define LSTM model
        lstm_model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)),
            LSTM(32, return_sequences=False),
            Dense(y.shape[1])
        ])

        lstm_model.compile(optimizer='adam', loss='mse')

        # Train LSTM model
        lstm_model.fit(X, y, epochs=15, batch_size=1, verbose=1)

        # Store models & history
        user_history[user_id] = {
            "hmm_model": hmm_model,
            "lstm_model": lstm_model,
            "history_data": group,
            "hidden_states": hidden_states
        }

    return user_history  # Pass to next model
