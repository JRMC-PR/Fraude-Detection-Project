#!/usr/bin/env python3
import os
import time
import pyfiglet
import traceback  # For full error trace
from model import run_fraud_detection  # Import the function from model.py

# Function to display welcome message
def display_welcome():
    ascii_art = pyfiglet.figlet_format("WELCOME TO BBPR FRAUD DETECTION ML MODEL")
    print(ascii_art)

# Function to display menu options
def display_menu():
    print("\nOptions:")
    print("1. Run Fraud Detection Model")
    print("0. Exit")

# Main function
def main():
    os.system("clear" if os.name == "posix" else "cls")  # Clear terminal screen
    display_welcome()

    #Declare path variables
    RSA_FILE, AUTH_FILE = "", ""
    RSA_PATH, AUTH_PATH = "", ""


    while True:
        while True:
            print("\n📌 **Note:**"
                  "\n The name of the file MUST FOLLOW THIS FORMAT:"
                  "\n Month_Date_Year.csv\n ")
            print("Example: Agosto_13_2024\n"
                  "Diciembre_4_2025")
            # Ask the user to input the file paths
            RSA_FILE = input(" Enter the RSA file name: ")
            AUTH_FILE = input(" Enter the AUTH file name: ")
            # Ask the user to confirm the file paths
            print("\n📌 **Note:**"
                  "\n Are you sure these are the correct File Names?"
                  f"\n RSA_DATA:{RSA_FILE}\n"
                f" AUTH_DATA:{AUTH_FILE}")
            validation = input("Enter 'yes' to continue or 'no' to re-enter the file Names: ")
            if validation == "yes":
                break
            else:
                continue
        # Split the file names to build the path
        RSA_PARTS = RSA_FILE.split("_")
        AUTH_PARTS = AUTH_FILE.split("_")

        # Get the month first
        RSA_MONTH = RSA_PARTS[0]
        AUTH_MONTH = AUTH_PARTS[0]

        #Extract the year and remove the .csv extention form input
        RSA_YEAR = RSA_PARTS[2].split(".")[0]
        AUTH_YEAR = AUTH_PARTS[2].split(".")[0]

        # Build the path
        RSA_PATH = f"../Data/Raw_Data/RSA_DATA/{RSA_MONTH}_{RSA_YEAR}/{RSA_FILE}"
        AUTH_PATH = f"../Data/Raw_Data/AUTH_DATA/{AUTH_MONTH}_{AUTH_YEAR}/{AUTH_FILE}"

        print(f"\nRSA_PATH: {RSA_PATH}")
        print(f"\nAUTH_PATH: {AUTH_PATH}")



        display_menu()
        choice = input("\nEnter your choice (1-0): ")

        if choice == "1":
            print("\nRunning Fraud Detection Model...\n")
            time.sleep(2)

            try:
                run_fraud_detection()  # Call the model function
                print("\nDetection complete! Check REPORT.csv for results.\n")

            except ValueError as e:
                print("\n❌ **Data Processing Error** ❌")
                print(f"   → {str(e)}")
                print("\n📌 Possible Causes:")
                print("   - A non-numeric value was found where a number was expected.")
                print("   - Check if 'DATA_S_1' or 'DATA_S_4' contains text instead of numbers.")
                print("   - Ensure CSV formatting is correct.\n")

                print("🔎 **Full Error Details:**")
                traceback.print_exc()  # Print full traceback

            except FileNotFoundError as e:
                print("\n❌ **Missing File Error** ❌")
                print(f"   → {str(e)}")
                print("\n📌 Solution:")
                print("   - Ensure `user_activity.csv` is present in the script's directory.")
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
            print("\nInvalid choice. Please enter 1 or 0.")

if __name__ == "__main__":
    main()
