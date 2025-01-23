import pandas as pd
import os
from datetime import datetime

# Directory containing CSV files
csv_folder = "path/to/your/csv/folder"  # Replace with the folder path
output_folder = "path/to/output/folder"  # Replace with your output folder path

# Get all CSV files in the folder
csv_files = [file for file in os.listdir(csv_folder) if file.endswith(".csv")]

# Dictionary to store data grouped by month
data_by_month = {}

# Loop through each CSV file and process
for csv_file in csv_files:
    file_path = os.path.join(csv_folder, csv_file)
    df = pd.read_csv(file_path)

    # Assuming there's a 'date' column, convert it to datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        # Extract the month and year
        df['month_year'] = df['date'].dt.to_period('M')
    else:
        raise ValueError(f"'date' column not found in {csv_file}")

    # Group data by month and store in the dictionary
    for month, group in df.groupby('month_year'):
        if month not in data_by_month:
            data_by_month[month] = group
        else:
            data_by_month[month] = pd.concat([data_by_month[month], group], ignore_index=True)

# Save combined data for each month to a new CSV file
for month, data in data_by_month.items():
    month_str = month.strftime('%Y-%m')  # Format as "YYYY-MM"
    output_file = os.path.join(output_folder, f"combined_{month_str}.csv")
    data.drop(columns=['month_year'], inplace=True)  # Drop temporary 'month_year' column
    data.to_csv(output_file, index=False)
    print(f"Saved combined data for {month_str} to {output_file}")
