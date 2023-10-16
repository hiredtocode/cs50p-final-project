import requests
import json
import os

# Function to print text in green
def print_green(text):
    print(f"\033[92m{text}\033[0m")

# Function to print text in red
def print_red(text):
    print(f"\033[91m{text}\033[0m")

# Function to load the entire state from a file
def load_state():
    if os.path.isfile("state.json"):
        with open("state.json", "r") as file:
            return json.load(file)
    return {"favorites": [], "total_balance": 0}

# Function to save the entire state to a file
def save_state(state):
    with open("state.json", "w") as file:
        json.dump(state, file)

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
    state["favorites"] = favorites_list
    save_state(state)
    print_green(f"Successfully added {code} to the favorites list.")

# Pre-populate available list
def pre_populate_list():
    coins_list = check_coins_list()
    print_green("\nPre-populating the coins list...")
    for coin in coins_list:
        code = coin['code']
        populated_list.append(code)
        state["populated_list"] = populated_list
        save_state(state)
    print_green(f"Successfully pre-populated coins list.\n")
    return "Pre-population of coins list completed successfully."

# Function to remove a cryptocurrency from favorites
def remove_from_favorites(code):
    if not favorites_list:
        print_green(f"Your favorites list is currently empty.")
        return
    elif code in favorites_list:
        favorites_list.remove(code)
        save_state(favorites_list)
        print_green(f" Successfully removed {code} from the favorites list.")
        print_green(f"Current favorite list contains: {favorites_list}")
    else:
        print_red(f"{code} is not in your favorites list.")
        return
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

# Function to display the current deposited balance
def display_deposited_balance(balance):
    if balance == 0:
        print_red(f"\nTotal balance: ${balance:.2f}\n")
    else:
        print_green(f"\nTotal balance: ${balance:.2f}\n")

# Function to make a deposit
def make_deposit(balance, amount):
    balance += amount
    state["total_balance"] = balance
    save_state(state)
    return balance

# Function to make a withdrawal
def make_withdrawal(balance, amount):
    balance -= amount
    state["total_balance"] = balance
    save_state(state)
    return balance

# Function to display "Online" in green or "Offline" in red
def display_status(status):
    if status == "{}":
        print("API status is \033[92mOnline\033[0m")
    else:
        print(f"API status is \033[91mOffline\033[0m {status}")

# Function to display remaining credits
def display_credit(credit):
    print(f"{credit} credits remaining.")

# Function to reset the state
def reset_state():
    global state, favorites_list, total_balance, populated_list

    if os.path.isfile("state.json"):
        os.remove("state.json")
        print_green("State reset. The program will continue running.")
        state = {"favorites": [], "total_balance": 0, "populated_list": []}
        favorites_list = state["favorites"]
        total_balance = state.get("total_balance", 0)
        populated_list = state["populated_list"]
        pre_populate_list()
        print_green(f"The total balance has been successfully resetted to ${total_balance}")
        print_green(f"The favorite list has been successfully resetted to {favorites_list}")
        save_state(state)
    else:
        print_red("No state file found. The program will continue running.")


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
    print("10. Make a deposit")
    print("11. Make a withdrawl")
    print("12. Reset data")

# Main program
if __name__ == "__main__":
    state = load_state()
    favorites_list = state["favorites"]
    populated_list = state.get("populated_list", [])
    total_balance = state.get("total_balance", 0)

    status = check_service_status()
    credit = check_service_credits()

    if not populated_list:
        pre_populate_list()

    display_credit(credit)
    display_status(status)


    while True:
        display_menu()
        choice = input("Select an option (1-12) or 0 to exit the program: ")

        try:
            choice = int(choice)
            if choice == 1:
                coins_list = check_coins_list()
                print("Top 10 coins list:")
                for coin in coins_list:
                    code = coin['code']
                    rate = "{:,.2f}".format(coin['rate'])
                    print_green(f"{code} ${rate} USD")
            elif choice == 2:
                while True:
                    try:
                        print("Option 2 selected.")
                        coin_name = input("What is the acronym of the coin name? ").strip().upper()
                        if coin_name == "Q":
                            break  # Return to the main menu
                        if not coin_name or not coin_name.isalpha():
                            print_red("Sorry, you must enter a valid acronym of the coin name or 'q' to quit.\n")
                        else:
                            add_to_favorites(coin_name)
                            print_green(f"Updated favorites list result is: {favorites_list}")
                            break  # Successfully added, return to the main menu
                    except ValueError:
                        print_red("Invalid input. Please enter a valid acronym of the coin name or 'q' to quit.\n")
            elif choice == 3:
                if not favorites_list:
                    print_red(f"Sorry, this option is not available since your favorites list is currently empty.")
                else:
                    while True:
                        print_green(f"Newly updated favorites list result is: {favorites_list}")
                        try:
                            print("Option 3 selected.")
                            coin_name = input("Which coin would you like to remove? q to quit: ").strip().upper()
                            if coin_name == "Q":
                                break  # Return to the main menu
                            if not coin_name or not coin_name.isalpha():
                                print_red("\nSorry, you must enter a valid acronym of the coin name or 'q' to quit.\n")
                                break
                            else:
                                remove_from_favorites(coin_name)
                                break  # Successfully added, return to the main menu
                        except ValueError:
                            print_red("Invalid input. Please enter a valid acronym of the coin name or 'q' to quit.\n")
            elif choice == 4:
                if not favorites_list:
                    print_red(f"\nSorry, your favorite list is empty.\n")
                else:
                    print_green(f"\nFavorites list: {favorites_list}\n")
            elif choice == 5:
                print("Option 5 selected.")
                # (Option to display the total deposited balance)
                display_deposited_balance(total_balance)
            elif choice == 6:
                print("Option 6 selected.")
            elif choice == 7:
                print("Option 7 selected.")
            elif choice == 8:
                print("Option 8 selected.")
            elif choice == 9:
                print("Option 9 selected.")
            elif choice == 10:
                # Make a deposit
                print_green(f"Current amount is ${total_balance:.2f}")
                deposit_amount = float(input("Enter the deposit amount: $"))
                if deposit_amount <= 0:
                    print_red("Invalid deposit amount.")
                else:
                    total_balance = make_deposit(total_balance, deposit_amount)
                    print_green(f"Successfully deposited ${deposit_amount:.2f}.")
                    print_green(f"The total balance is now: ${total_balance:.2f}.")
            elif choice == 11:
                print("Option 11 selected.") # Make a withdrawal
                print_green(f"Current amount is ${total_balance:.2f}")
                withdrawal_amount = float(input("Enter the withdrawal amount: $"))
                if withdrawal_amount <= 0 or withdrawal_amount > total_balance:
                    print_red("Invalid withdrawal amount.")
                else:
                    total_balance = make_withdrawal(total_balance, withdrawal_amount)
                    print_green(f"Successfully withdrew ${withdrawal_amount:.2f}.")
                    print_green(f"The total balance is now: ${total_balance:.2f}.")
            elif choice == 12:
                reset_state()
            elif choice == 0:
                print_green(f"\nYou selected Option {choice}. The program will now exit. Thank you.\n")
                break
            else:
                print_red("Invalid choice. Please select a number between 1 and 11 or 0 to exit the program.")
        except ValueError:
            print_red("Invalid input. Please enter a number.")
