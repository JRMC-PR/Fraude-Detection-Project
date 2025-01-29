import pandas as pd
import numpy as np
import hdbscan
import re
from sklearn.preprocessing import StandardScaler
from datetime import datetime

def run_fraud_detection():
    try:
        # Load data from CSV
        df = pd.read_csv("../Data/generated_loginsRSA.csv")

        # Step 1: Create PROXI_ID for Each User
        def create_proxi_id(row):
            return f"{row['USER_ID']}_{row['USER_NAME']}_{row['DATA_S_1']}_{row['DATA_S_4']}"

        df["PROXI_ID"] = df.apply(create_proxi_id, axis=1)

        # Step 2: Select Numerical Features for Clustering
        numerical_features = ["DATA_S_4"]  # Only cluster based on valid numeric columns

        # Check for non-numeric values in `DATA_S_4`
        if not pd.to_numeric(df["DATA_S_4"], errors="coerce").notna().all():
            print("\n🚨 **Warning: `DATA_S_4` contains non-numeric values!**")
            bad_values = df[pd.to_numeric(df["DATA_S_4"], errors="coerce").isna()]
            print(bad_values[["DATA_S_4"]].head())  # Show problematic rows
            raise ValueError(f"Column `DATA_S_4` contains invalid values. Example: {bad_values.iloc[0]['DATA_S_4']}")

        # Step 3: Standardize Features
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df[numerical_features])

        # Step 4: Apply HDBSCAN Clustering
        clusterer = hdbscan.HDBSCAN(min_cluster_size=5, min_samples=2, gen_min_span_tree=True)
        df["cluster"] = clusterer.fit_predict(df_scaled)

        # Identify anomalies
        df["is_anomaly"] = df["cluster"] == -1

        # Step 5: Report Anomalies
        anomaly_report = df[df["is_anomaly"]]

        # Initialize empty DataFrame for the report
        report_df = pd.DataFrame(columns=["Event Type", "Count", "Timestamp", "PROXI_ID", "DATA_S_1"])

        for _, row in anomaly_report.iterrows():
            new_row = pd.DataFrame([{
                "Event Type": "HDBSCAN Anomaly Detection",
                "Count": len(anomaly_report),
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "PROXI_ID": row["PROXI_ID"],
                "DATA_S_1": row["DATA_S_1"]
            }])

            # ✅ Correct way to append rows in Pandas 2.x
            report_df = pd.concat([report_df, new_row], ignore_index=True)

        report_df.to_csv("REPORT.csv", index=False)
        print("\n✅ Anomaly detection complete. Results saved in REPORT.csv")

    except Exception as e:
        print(f"\n❌ **Error in model.py**: {e}")
        raise  # Re-raise the error for `main.py` to catch it
