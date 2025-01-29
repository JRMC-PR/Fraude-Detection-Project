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

    while True:
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
