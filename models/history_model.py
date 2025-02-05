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
    """Converts 'DDMMMYYYY:HH:MM:SS' format to 'DDMMYYYYHH:MM:SS'."""
    try:
        day = event_time[:2]
        month_abbr = event_time[2:5].upper()  # Extract month abbreviation
        year = event_time[5:9]
        time_part = event_time[10:]  # Extract HH:MM:SS

        if month_abbr in MONTH_MAP:
            month_numeric = MONTH_MAP[month_abbr]
            return f"{day}{month_numeric}{year}{time_part}"
        else:
            raise ValueError(f"Invalid month abbreviation: {month_abbr}")

    except Exception as e:
        print(f"❌ Error processing time {event_time}: {e}")
        return None  # Return None if conversion fails

def adjust_event_time(event_time, timezone_offset):
    """Adjusts EVENT_TIME based on TIMEZONE offset."""
    try:
        dt = datetime.strptime(event_time, "%d%m%Y%H:%M:%S")
        dt = dt - timedelta(hours=timezone_offset)  # Adjust timezone
        return dt.strftime("%d%m%Y%H:%M:%S")
    except Exception as e:
        print(f"❌ Error adjusting time {event_time}: {e}")
        return event_time  # Return original if error occurs

def build_user_history(csv_path):
    """Builds user history using HMM & LSTM while handling sparse data issues."""

    # Load CSV data
    df = pd.read_csv(csv_path)

    # Select relevant columns
    features = ['USER_NAME', 'DATA_S_1', 'IP_ADDRESS', 'IP_CITY', 'TIMEZONE',
                'EVENT_TIME', 'DATA_S_4', 'DATA_S_34', 'RISK_SCORE']
    df = df[['USER_ID'] + features]  # Keep USER_ID as anchor

    # Ensure TIMEZONE is numeric
    df['TIMEZONE'] = pd.to_numeric(df['TIMEZONE'], errors='coerce').fillna(0).astype(int)

    # Convert EVENT_TIME from '18MAY2022:18:13:07' to '1805202218:13:07'
    df['EVENT_TIME'] = df['EVENT_TIME'].apply(parse_event_time)

    # Apply timezone adjustment to EVENT_TIME
    df['EVENT_TIME'] = df.apply(lambda row: adjust_event_time(str(row['EVENT_TIME']), row['TIMEZONE']), axis=1)

    # Convert EVENT_TIME to Unix timestamp
    df['EVENT_TIME'] = df['EVENT_TIME'].apply(lambda x: datetime.strptime(x, "%d%m%Y%H:%M:%S").timestamp())

    # Encode categorical data
    label_encoders = {}
    for col in ['USER_NAME', 'DATA_S_1', 'IP_ADDRESS', 'IP_CITY', 'DATA_S_34']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le  # Store encoders for future use

    # Normalize numerical values
    scaler = MinMaxScaler()
    df[['EVENT_TIME', 'DATA_S_4', 'RISK_SCORE']] = scaler.fit_transform(df[['EVENT_TIME', 'DATA_S_4', 'RISK_SCORE']])

    # Group data by USER_ID
    user_history = {}

    for user_id, group in df.groupby('USER_ID'):
        group = group.drop(columns=['USER_ID'])  # Remove USER_ID column

        # Convert history into a numerical sequence
        sequence = group.to_numpy()

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

