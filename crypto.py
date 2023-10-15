import requests
import json

# Function to check coins list
def check_coins_list():
    url = "https://api.livecoinwatch.com/coins/list"

    payload = json.dumps({
    "currency": "USD",
    "sort": "rank",
    "order": "ascending",
    "offset": 0,
    "limit": 10,
    "meta": False
    })
    headers = {
    'content-type': 'application/json',
    'x-api-key': 'bd95c726-08ea-447d-94e5-00088cf86908'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = json.loads(response.text)
    return response_data

# Function to check the service status
def check_service_status():
    url = "https://api.livecoinwatch.com/status"
    payload = {}
    headers = {'content-type': 'application/json', 'x-api-key': 'bd95c726-08ea-447d-94e5-00088cf86908'}

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

# Function to check credits
def check_service_credits():
    url = "https://api.livecoinwatch.com/credits"
    payload={}
    headers = {
    'content-type': 'application/json',
    'x-api-key': 'bd95c726-08ea-447d-94e5-00088cf86908'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_data = json.loads(response.text)
    return response_data.get("dailyCreditsRemaining")

# Function to display "Online" in green or "Offline" in red
def display_status(status):
    if status == "{}":
        print("API status is \033[92mOnline\033[0m")
    else:
        print(f"API status is \033[91mOffline\033[0m {status}")

# Function to display remaining credits
def display_credit(credit):
    print(f"{credit} credits remaining.")

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
    status = check_service_status()
    credit = check_service_credits()
    display_credit(credit)
    display_status(status)
    display_menu()

    while True:
        choice = input("Select an option (1-9) or 0 to exit the program: ")

        try:
            choice = int(choice)
            if choice == 1:
                coins_list = check_coins_list()
                print("Top 10 coins list:")
                for coin in coins_list:
                    print(f"{coin['code']} ({coin['rate']})")
            elif choice == 2:
                print("Option 2 selected.")
            elif choice == 3:
                print("Option 3 selected.")
            elif choice == 4:
                print("Option 4 selected.")
            elif choice == 5:
                print("Option 5 selected.")
            elif choice == 6:
                print("Option 6 selected.")
            elif choice == 7:
                print("Option 7 selected.")
            elif choice == 8:
                print("Option 8 selected.")
            elif choice == 9:
                print("Option 9 selected.")
            elif choice == 0:
                print(f"You selected Option {choice}. The program will now exit. Thank you.")
                break
            else:
                print("Invalid choice. Please select a number between 1 and 9 or 0 to exit the program.")
        except ValueError:
            print("Invalid input. Please enter a number.")
