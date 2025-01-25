import pandas as pd

def extract_columns(input_file, output_file, columns_to_extract):
    """
    Extract specified columns from a CSV file and save them to a new file.

    Args:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to save the output CSV file with extracted columns.
        columns_to_extract (list): List of column names to extract.
    """
    try:
        # Load the CSV file
        data = pd.read_csv(input_file)

        # Check if all required columns exist in the CSV
        missing_columns = [col for col in columns_to_extract if col not in data.columns]
        if missing_columns:
            print(f"Error: The following columns are missing in the input file: {missing_columns}")
            return

        # Extract the specified columns
        filtered_data = data[columns_to_extract]

        # Save the filtered data to a new CSV file
        filtered_data.to_csv(output_file, index=False)
        print(f"Filtered data saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Specify the columns to extract
columns = ["REPORT_DATE", "USER_ID", "USER_NAME", "TIMEZONE", "IP_ADDRESS", "IP_COUNTRY", "IP_CITY", "EVENT_TYPE"]

# Example usage
input_csv = "C:/Users/guill/Holberton_Machine_Learning/Fraude-Detection-Project/generated_loginsRSA.csv"   # Replace with the path to your input CSV file
output_csv = "C:/Users/guill/Holberton_Machine_Learning/Fraude-Detection-Project/cleaned_RSA.csv" # Replace with the desired path for the output CSV file

extract_columns(input_csv, output_csv, columns)
