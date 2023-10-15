import sys
import requests
import json

# Define a function to display the menu
def display_menu():
    print("Please input your selection number:")
    print("1. Show all available crypto coins")
    print("2. Add a crypto to my favorites")
    print("3. Remove a crypto from my favorites")
    print("4. Show the list of coins and current prices that are in my favorites")
    print("5. My total amount of USD")
    print("6. My total amount of USD invested in coins")
    print("7. Current status of my Loss / Profit")
    print("8. Buy crypto")
    print("9. Sell crypto")

# Main program
if __name__ == "__main__":
    display_menu()

    while True:
        choice = input("Select an option (1-9): ")

        try:
            choice = int(choice)
            if 1 <= choice <= 9:
                print(f"You selected Option {choice}.")
                break  # Exit the loop when a valid choice is made
            else:
                print("Invalid choice. Please select a number between 1 and 9.")
        except ValueError:
            print("Invalid input. Please enter a number.")

