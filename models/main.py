#!/usr/bin/env python3
import os
import time
import pyfiglet
import traceback  # For full error trace
from model import run_fraud_detection  # Import the function from model.py
import pickle
from history_model import build_user_history

# Function to display welcome message
def display_welcome():
    ascii_art = pyfiglet.figlet_format("WELCOME TO BBPR FRAUD DETECTION ML MODEL")
    print(ascii_art)

# Function to display menu options
def display_menu():
    print("\nOptions:")
    print("1. Run Fraud Detection Model for numerical values")
    print("0. Exit")

def show_skipped_users():
    """Load and display all skipped users along with their stored history."""
    SKIPPED_USERS_FILE = "skipped_users.pkl"

    try:
        # Load skipped users
        with open(SKIPPED_USERS_FILE, "rb") as f:
            skipped_users = pickle.load(f)

        # Check if there are any skipped users
        if not skipped_users:
            print("✅ No skipped users! All users have enough data.")
            return

        print("\n📌 Skipped Users and Their Stored Data:")
        for user_id, data in skipped_users.items():
            record_count = len(data["history_data"])
            print(f"  - User ID: {user_id} | Total Records: {record_count}")
            print(data["history_data"].head(), "\n")  # Show first few records

    except FileNotFoundError:
        print("❌ Skipped users file not found!")
    except Exception as e:
        print(f"❌ Error reading skipped users: {e}")

def format_month(month):
    """Ensures the month is capitalized properly (First letter uppercase, rest lowercase)."""
    return month.capitalize()

# Main function
def main():
    os.system("clear" if os.name == "posix" else "cls")  # Clear terminal screen
    display_welcome()

    while True:
        while True:
            print("\n📌 **Note:**"
                  "\n The name of the file MUST FOLLOW THIS FORMAT:"
                  "\n Month_Date_Year.csv\n ")
            print("Example: Agosto_13_2024\n"
                  "Diciembre_4_2025")

            # Ask the user to input the file names
            RSA_FILE = input(" Enter the RSA file name: ").strip()
            AUTH_FILE = input(" Enter the AUTH file name: ").strip()

            # Ask the user to confirm the file paths
            print("\n📌 **Note:**"
                  "\n Are you sure these are the correct File Names?"
                  f"\n RSA_DATA: {RSA_FILE}\n"
                  f" AUTH_DATA: {AUTH_FILE}")

            validation = input("Enter 'yes' to continue or 'no' to re-enter the file names: ").strip().lower()
            if validation == "yes":
                break
            else:
                continue

        # Split the file names to build the path
        try:
            RSA_PARTS = RSA_FILE.split("_")
            AUTH_PARTS = AUTH_FILE.split("_")

            # Ensure the month is properly formatted
            RSA_MONTH = format_month(RSA_PARTS[0])
            AUTH_MONTH = format_month(AUTH_PARTS[0])

            # Extract the year and remove the .csv extension
            RSA_YEAR = RSA_PARTS[2].split(".")[0]
            AUTH_YEAR = AUTH_PARTS[2].split(".")[0]

            # Build the path
            RSA_PATH = f"../Data/Raw_Data/RSA_DATA/{RSA_MONTH}_{RSA_YEAR}/{RSA_FILE}"
            AUTH_PATH = f"../Data/Raw_Data/AUTH_DATA/{AUTH_MONTH}_{AUTH_YEAR}/{AUTH_FILE}"

            print(f"\nRSA_PATH: {RSA_PATH}")
            print(f"\nAUTH_PATH: {AUTH_PATH}")

        except IndexError:
            print("\n❌ Invalid file name format. Please follow the required format (Month_Date_Year.csv).")
            continue

        display_menu()
        choice = input("\nEnter your choice (1-0): ").strip()

        if choice == "1":
            print("\nRunning Fraud Detection Model...\n")
            time.sleep(2)

            try:
                build_user_history(RSA_PATH)  # Call the model function
                print("\nDetection complete! Save user_history.pkl fedding into Brute force now.\n")
                run_fraud_detection(AUTH_PATH, "/home/vaiosos/Documents/Holberton/Fraude-Detection-Project/models/user_history.pkl")  # Call the model function
                print("\nDetection complete! Check detected_anomalies.csv for results. and processed_login_attempts.csv\n")

            except ValueError as e:
                print("\n❌ **Data Processing Error** ❌")
                print(f"   → {str(e)}\n")
                print("🔎 **Full Error Details:**")
                traceback.print_exc()  # Print full traceback

            except FileNotFoundError as e:
                print("\n❌ **Missing File Error** ❌")
                print(f"   → {str(e)}")
                print("\n📌 Solution:")
                print(f"   - Ensure `{RSA_FILE}` is present in the correct folder {RSA_PATH} directory.")
                print("   - Check if the filename is spelled correctly.\n")

                print("🔎 **Full Error Details:**")
                traceback.print_exc()

            except Exception as e:
                print("\n❌ **Unexpected Error Occurred!** ❌")
                print(f"   → {str(e)}\n")
                print("🔎 **Full Traceback:**")
                traceback.print_exc()

        elif choice == "0":
            print("\nExiting... Goodbye!")
            break

        else:
            print("\nInvalid choice. Please enter 1, 2, or 0.")

if __name__ == "__main__":
    main()
