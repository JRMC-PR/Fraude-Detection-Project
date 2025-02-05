import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from hmmlearn import hmm
from tensorflow.keras.models import Sequential  #type: ignore
from tensorflow.keras.layers import LSTM, Dense  # type: ignore
from sklearn.preprocessing import LabelEncoder, MinMaxScaler  # Preprocessing utilities

# Mapping of month abbreviations to numeric values for EVENT_TIME conversion
MONTH_MAP = {
    "JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06",
    "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"
}

def parse_event_time(event_time, timezone_offset=0):
    """
    Adjusts EVENT_TIME by subtracting the TIMEZONE value from the hour (%H).

    Parameters:
        event_time (str): Original event time in 'DDMMMYYYY:HH:MM:SS' format.
        timezone_offset (int): The timezone offset to subtract from the event time.

    Returns:
        str: Adjusted event time in the original format 'DDMMMYYYY:HH:MM:SS'.
    """
    try:
        # Convert string to datetime object
        dt = datetime.strptime(event_time, "%d%b%Y:%H:%M:%S")

        # Adjust the hour by subtracting the TIMEZONE offset
        dt = dt + timedelta(hours=int(timezone_offset))

        # Convert back to string in the original format
        return dt.strftime("%d%b%Y:%H:%M:%S")

    except Exception as e:
        print(f"❌ Error processing time {event_time} with timezone {timezone_offset}: {e}")
        return event_time  # Return original if error occurs

def build_user_history(csv_path):
    """
    Reads a CSV file and builds a historical profile for each USER_ID.
    The model uses:
        - Hidden Markov Models (HMM) to analyze sequential behavior patterns.
        - Long Short-Term Memory (LSTM) networks to predict user actions.

    Parameters:
        csv_path (str): Path to the CSV file.

    Returns:
        dict: A dictionary with USER_IDs as keys and their processed history as values.
    """

    # Load CSV data into a pandas DataFrame
    df = pd.read_csv(csv_path)

    # Select only the relevant columns needed for modeling
    features = ['USER_ID', 'USER_NAME', 'DATA_S_1', 'IP_ADDRESS', 'IP_CITY', 'TIMEZONE',
                'EVENT_TIME', 'DATA_S_4', 'DATA_S_34', 'RISK_SCORE', 'EVENT_TYPE']

    df = df[features]  # Keep only selected features

    # ✅ Ensure USER_NAME is treated as a string (important for identity tracking)
    df['USER_NAME'] = df['USER_NAME'].astype(str)

    # ✅ Keep IP_ADDRESS as a string (do not encode it into numbers)
    df['IP_ADDRESS'] = df['IP_ADDRESS'].astype(str)

    # ✅ Ensure TIMEZONE is a numeric integer (replace NaN with 0)
    df['TIMEZONE'] = pd.to_numeric(df['TIMEZONE'], errors='coerce').fillna(0).astype(int)

    # ✅ Adjust EVENT_TIME by subtracting the TIMEZONE offset from the hour
    df['EVENT_TIME'] = df.apply(lambda row: parse_event_time(str(row['EVENT_TIME']), row['TIMEZONE']), axis=1)

    # ✅ Ensure EVENT_TIME is kept in its original 'DDMMMYYYY:HH:MM:SS' format
    df['EVENT_TIME'] = df['EVENT_TIME'].apply(parse_event_time)

    # ✅ Ensure DATA_S_4 is an integer (device age)
    df['DATA_S_4'] = pd.to_numeric(df['DATA_S_4'], errors='coerce').fillna(0).astype(int)

    # ✅ Keep DATA_S_34 in its original form (e.g., hardware ID or unique identifier)
    df['DATA_S_34'] = df['DATA_S_34'].astype(str)

    # Debugging: Print first few records after preprocessing
    print("\n📊 DEBUG: First few records after preprocessing:")
    print(df.head())

    # Create an empty dictionary to store user history
    user_history = {}

    # Process each user separately by grouping data based on USER_ID
    for user_id, group in df.groupby('USER_ID'):
        group = group.drop(columns=['USER_ID'])  # Remove USER_ID from the data (anchor already known)

        # Convert history into a numerical sequence (excluding categorical features)
        sequence = group.select_dtypes(include=[np.number]).to_numpy()

        # Skip HMM training if the user has fewer than 3 login records (not enough data to model behavior)
        if len(sequence) < 3:
            print(f"⚠️ Skipping HMM training for {user_id} (Not enough data: {len(sequence)} records)")
            user_history[user_id] = {
                "hmm_model": None,  # No HMM model for this user due to lack of data
                "lstm_model": None,  # No LSTM model either
                "history_data": group,  # Store historical login data
                "hidden_states": [-1] * len(sequence)  # Default state for sparse users
            }
            continue  # Skip further processing for this user

        # Train Hidden Markov Model (HMM) to model user behavior
        hmm_model = hmm.GaussianHMM(n_components=min(3, len(sequence)), covariance_type="diag", n_iter=100)
        hmm_model.fit(sequence)  # Train the HMM on login data
        hidden_states = hmm_model.predict(sequence)  # Predict state transitions

        # Prepare data for LSTM model (shifted sequential input/output)
        X = sequence[:-1]  # Inputs (all but last record)
        y = sequence[1:]   # Outputs (shifted by one step)

        # Reshape data to match LSTM input format (samples, time steps, features)
        X = X.reshape((X.shape[0], X.shape[1], 1))
        y = y.reshape((y.shape[0], y.shape[1]))

        # Define the LSTM model for sequential pattern prediction
        lstm_model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(X.shape[1], 1)),  # First LSTM layer
            LSTM(32, return_sequences=False),  # Second LSTM layer
            Dense(y.shape[1])  # Fully connected output layer (same shape as target)
        ])

        lstm_model.compile(optimizer='adam', loss='mse')  # Compile the model with Mean Squared Error loss

        # Train LSTM model (predicts the next login event based on past behavior)
        lstm_model.fit(X, y, epochs=15, batch_size=1, verbose=1)

        # Store trained models & history for this user
        user_history[user_id] = {
            "hmm_model": hmm_model,  # Store trained HMM model
            "lstm_model": lstm_model,  # Store trained LSTM model
            "history_data": group,  # Store user's login data
            "hidden_states": hidden_states  # Store predicted HMM states
        }

    return user_history  # Pass user history to the next model in the pipeline

