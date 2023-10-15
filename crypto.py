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

# Add to the favorites list
def add_to_favorites(code):
    favorites_list.append(code)
    print(f"\n\033[92m Successfully added {code} to the favorites list.\033[0m\n")

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
    print("1. Show all available cryptocurrency coins")
    print("2. Add a cryptocurrency to my favorites")
    print("3. Remove a cryptocurrency from my favorites")
    print("4. Display my favorites")
    print("5. My total amount of USD")
    print("6. My total amount of USD invested in coins")
    print("7. Current status of my Profit / Loss")
    print("8. Buy cryptocurrency")
    print("9. Sell cryptocurrency")

# Main program
if __name__ == "__main__":
    favorites_list = []

    status = check_service_status()
    credit = check_service_credits()
    display_credit(credit)
    display_status(status)



    while True:
        display_menu()
        choice = input("Select an option (1-9) or 0 to exit the program: ")

        try:
            choice = int(choice)
            if choice == 1:
                coins_list = check_coins_list()
                print("Top 10 coins list:")
                for coin in coins_list:
                    code = coin['code']
                    rate = "{:,.2f}".format(coin['rate'])
                    print(f"\033[92m{code} ${rate} USD\033[0m")
            elif choice == 2:
                while True:
                    try:
                        print("Option 2 selected.")
                        coin_name = input("What is the acronym of the coin name? ").strip().upper()
                        if coin_name == "Q":
                            break  # Return to the main menu
                        if not coin_name or not coin_name.isalpha():
                            print("\nSorry, you must enter a valid acronym of the coin name or 'q' to quit.\n")
                        else:
                            add_to_favorites(coin_name)
                            print(f"Updated favorites list result is: {favorites_list}")
                            break  # Successfully added, return to the main menu
                    except ValueError:
                        print("\nInvalid input. Please enter a valid acronym of the coin name or 'q' to quit.\n")
            elif choice == 3:
                print("Option 3 selected.")
            elif choice == 4:
                print(f"\n\033[92mFavorites list: {favorites_list}\033[0m\n")
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
                print(f"\nYou selected Option {choice}. The program will now exit. Thank you.\n")
                break
            else:
                print("\nInvalid choice. Please select a number between 1 and 9 or 0 to exit the program.\n")
        except ValueError:
            print("\nInvalid input. Please enter a number.\n")
