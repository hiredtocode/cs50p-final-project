import time
import requests
import json
import os
import threading

# Define the state variable
state = {}

# Function to print text in green
def print_green(text):
    print(f"\033[92m{text}\033[0m")

# Function to print text in red
def print_red(text):
    print(f"\033[91m{text}\033[0m")

# Function to print text in blue
def print_blue(text):
    print(f"\033[94m{text}\033[0m")

# Function to load the entire state from a file
def load_state():
    if os.path.isfile("state.json"):
        with open("state.json", "r") as file:
            state = json.load(file)
    else:
        state = {
            "favorites": [],
            "total_balance": 0,
            "coins_list": [],
            "bought_history": [],
            "sold_history": [],
            "total_assets": {},
            "grand_total": 0,
        }
    return state



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

    # Print the API response for debugging
    # print("API Response:")
    # print(response.text)

    response_data = json.loads(response.text)

    return response_data

# Function to add retrieved coins list to the state
def add_coins_list_to_state():
    coins_list = check_coins_list()
    state["coins_list"] = coins_list
    save_state(state)

# Function to display the coins list from the state
def display_coins_list():
    coins_list = state.get("coins_list", [])
    if coins_list:
        print("Top 10 coins list:")
        for i, coin in enumerate(coins_list[:10], 1):
            code = coin['code']
            rate = "{:,.2f}".format(coin['rate'])
            print_green(f"{i}. {code} ${rate} USD")
    else:
        print_red("Coins list not available. Please update it.")

# Add to the favorites list
def add_to_favorites(code):
    global favorites_list
    favorites_set = set(state["favorites"])
    if code in favorites_set:
        print_red(f"{code} is already in your favorites list.")
    else:
        favorites_set.add(code)
        state["favorites"] = list(favorites_set)  # Convert back to a list
        favorites_list = state["favorites"]  # Update favorites_list
        save_state(state)
        print_green(f"Successfully added {code} to the favorites list.")

# Pre-populate available list
def pre_populate_list():
    # coins_list = check_coins_list()
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
    global favorites_list
    favorites_set = set(state["favorites"])
    if code in favorites_set:
        favorites_set.remove(code)
        state["favorites"] = list(favorites_set)  # Convert back to a list
        favorites_list = state["favorites"]  # Update favorites_list
        save_state(state)
        print_green(f"Successfully removed {code} from the favorites list.")
        print_green(f"Current favorite list contains: {state['favorites']}")
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
    global state, favorites_list, total_balance, coins_list, populated_list  # Update these variables as global

    state = {
        "favorites": [],
        "total_balance": 0,
        "coins_list": [],
        "bought_history": [],  # Initialize bought history as an empty list
        "sold_history": [],    # Initialize sold history as an empty list
    }

    favorites_list = state["favorites"]
    coins_list = check_coins_list()  # Update coins_list by making an API call
    state["coins_list"] = coins_list
    total_balance = 0  # Reset total_balance to 0
    populated_list = []  # Reset populated_list
    pre_populate_list()  # Populate it again
    print_green("The state has been successfully reset to default values.")
    save_state(state)

# Function to update the coins list in the background
def update_coins_list():
    global coins_list  # Make the coins_list variable global

    while True:
        coins_list = check_coins_list()
        # Sleep for a while before updating again
        time.sleep(60)  # Adjust the sleep duration as needed

# Initialize total_assets as an empty dictionary
total_assets = {}

# Function to buy cryptocurrency
def buy_cryptocurrency():
    global total_balance

    if "total_assets" not in state:
        state["total_assets"] = {}

    print("Option 8 selected - Buy cryptocurrency")
    display_coins_list()

    while True:
        try:
            choice = int(input("Select a cryptocurrency to buy (enter the corresponding number): "))
            if 1 <= choice <= len(coins_list):
                selected_coin = coins_list[choice - 1]
                break
            else:
                print_red("Invalid choice. Please select a valid number.")
        except ValueError:
            print_red("Invalid input. Please enter a number.")

    while True:
        try:
            amount_to_buy = float(input(f"Enter the amount of {selected_coin['code']} to buy (USD): $"))
            if amount_to_buy <= 0:
                print_red("Invalid amount. Please enter a positive value.")
                continue

            if amount_to_buy <= total_balance:
                coin_name = selected_coin['code']
                quantity = amount_to_buy / selected_coin['rate']

                if coin_name in state["total_assets"]:
                    state["total_assets"][coin_name] += quantity
                else:
                    state["total_assets"][coin_name] = quantity

                total_balance -= amount_to_buy
                state["total_balance"] = total_balance

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                state["bought_history"].append((timestamp, coin_name, quantity, amount_to_buy))
                save_state(state)

                print_green(f"Successfully bought ${amount_to_buy:.2f} worth of {coin_name}.")
                print_green(f"The new total amount of owned {coin_name} is: {state['total_assets'][coin_name]:.6f}")
                print_green(f"Your new total balance in USD is {total_balance}")
                return total_balance
            else:
                print_red("Insufficient balance. Please deposit more and try again. Loading main menu...")
                print("Returning to the main menu...")
                return
        except ValueError:
            print_red("Invalid input. Please enter a valid number.")

def check_total_assets():
    total_assets = state.get("total_assets", {})
    total_balance = state.get("total_balance", 0)

    grand_total = total_balance  # Initialize grand total with the total balance

    if not total_assets and total_balance == 0:
        print_red("You currently own no cryptocurrencies.")
        print_red("You currently own no USD.")
    elif not total_assets:
        total_value_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin['code'] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info['rate']
            total_value_in_usd += value_in_usd
            print_green(f"{code}: {formatted_quantity} {code} | Value in USD: ${value_in_usd:.2f}")
        print_green(f"Total Value in USD of all assets: ${total_value_in_usd:.2f} in cryptocurrency")
        print_green(f"Total Balance in USD: ${total_balance:.2f}")
        grand_total += total_value_in_usd  # Add the total value of assets to the grand total
        state["grand_total"] = grand_total  # Update the state with the grand total
        print_green(f"Grand Total in USD: ${grand_total:.2f}")
    else:
        print_green("\nYour assets:")
        total_amount_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin['code'] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info['rate']
            total_amount_in_usd += value_in_usd
            print_green(f"{code}: {formatted_quantity} {code} | Quantity Value in USD: ${value_in_usd:.2f}")
        print_green(f"Total Value in USD of all assets: ${total_amount_in_usd:.2f} in cryptocurrency")
        print_green(f"Total Balance in USD: ${total_balance:.2f}")
        grand_total += total_amount_in_usd  # Add the total value of assets to the grand total
        state["grand_total"] = grand_total  # Update the state with the grand total
        print_green(f"Grand Total in USD: ${grand_total:.2f}")



def display_total_assets():
    total_assets = state.get("total_assets", {})
    if not total_assets:
        print_red("You currently own no cryptocurrencies.")
        print_red("You currently own no USD.")
    else:
        print_green("Your total assets:")
        total_balance = state.get("total_balance", 0)

        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin['code'] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info['rate']
            print_green(f"{code}: {formatted_quantity} {code} | Value in USD: ${value_in_usd:.2f}")

        print_green(f"Total Value in USD of all assets: ${total_balance:.2f} in cryptocurrency")
        print_green(f"Total Balance in USD: ${total_balance:.2f}")

# Initialize total_assets as an empty dictionary
if "total_assets" not in state:
    state["total_assets"] = {}

# Existing code for sell_cryptocurrency
# Existing code for sell_cryptocurrency
def sell_cryptocurrency():
    global total_balance
    print("Option 9 selected - Sell cryptocurrency")

    while True:
        # Display the list of assets the user owns
        check_total_assets()

        assets = state.get("total_assets", {})
        asset_codes = list(assets.keys())

        if not assets:
            print_red("You currently own no cryptocurrencies.")
            return  # Return to the main menu

        print("Select a cryptocurrency to sell:")
        for i, code in enumerate(asset_codes, 1):
            coin_info = [coin for coin in coins_list if coin['code'] == code][0]
            value_in_usd = assets[code] * coin_info['rate']
            print_green(f"{i}. {code} | Value in USD: ${value_in_usd:.2f}")

        print("Enter the corresponding number or 0 to return to the main menu: ")

        try:
            choice = input()
            if choice == "0":
                return  # Return to the main menu
            choice = int(choice)

            if 1 <= choice <= len(asset_codes):
                selected_code = asset_codes[choice - 1]
                coin_info = [coin for coin in coins_list if coin['code'] == selected_code][0]

                # Calculate the current value of the selected cryptocurrency
                current_value = assets[selected_code] * coin_info['rate']

                print_green(f"You currently own {assets[selected_code]:.6f} {selected_code} valued at ${current_value:.2f} USD")

                while True:
                    try:
                        amount_to_sell = float(input(f"Enter the amount of {selected_code} to sell (USD): $"))
                        if amount_to_sell <= 0:
                            print_red("Invalid amount. Please enter a positive value.")
                            continue

                        if amount_to_sell <= current_value:
                            # Update the total balance by adding the selling amount
                            total_balance += amount_to_sell
                            state["total_balance"] = total_balance

                            # Update the total_assets dictionary with the newly sold coin and quantity
                            assets[selected_code] -= amount_to_sell / coin_info['rate']
                            state["total_assets"] = assets

                            # Get the current timestamp
                            timestamp = time.strftime("%Y-%m-d %H:%M:%S")

                            # Append the transaction details to the sold history
                            state["sold_history"].append((timestamp, selected_code, amount_to_sell / coin_info['rate'], amount_to_sell))
                            save_state(state)

                            print_green(f"\nSuccessfully sold ${amount_to_sell:.2f} worth of {selected_code}.\n")
                            check_total_assets()
                            return  # Return to the main menu

                        else:
                            print_red("Insufficient balance. Please enter a lower amount.")
                    except ValueError:
                        print_red("Invalid input. Please enter a valid number.")
            else:
                print_red("Invalid choice. Please select a valid number.")
        except ValueError:
            print_red("Invalid input. Please enter a number or 0 to return to the main menu.")

# Function to check the total assets
def check_total_assets():
    total_assets = state.get("total_assets", {})
    total_balance = state.get("total_balance", 0)

    grand_total = total_balance  # Initialize grand total with the total balance

    if not total_assets and total_balance == 0:
        print_red("You currently own no cryptocurrencies.")
        print_red("You currently own no USD.")
    elif not total_assets:
        total_value_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin['code'] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info['rate']
            total_value_in_usd += value_in_usd
            print_green(f"{code}: {formatted_quantity} {code} | Value in USD: ${value_in_usd:.2f}")
        print_green(f"Total Value in USD of all assets: ${total_value_in_usd:.2f} in cryptocurrency")
        print_green(f"Total Balance in USD: ${total_balance:.2f}")
        grand_total += total_value_in_usd  # Add the total value of assets to the grand total
        state["grand_total"] = grand_total  # Update the state with the grand total
        print_green(f"Grand Total in USD: ${grand_total:.2f}")
    else:
        print_green("\nYour assets:")
        total_amount_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin['code'] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info['rate']
            total_amount_in_usd += value_in_usd
            print_green(f"{code}: {formatted_quantity} {code} | Quantity Value in USD: ${value_in_usd:.2f}")
        print_green(f"Total Value in USD of all assets: ${total_amount_in_usd:.2f} in cryptocurrency")
        print_green(f"Total Balance in USD: ${total_balance:.2f}")
        grand_total += total_amount_in_usd  # Add the total value of assets to the grand total
        state["grand_total"] = grand_total  # Update the state with the grand total
        print_green(f"Grand Total in USD (cryptocurrency + USD): ${grand_total:.2f}")



# Function to display transaction history
def display_transaction_history():
    bought_history = state.get("bought_history", [])
    sold_history = state.get("sold_history", [])

    if not bought_history and not sold_history:
        print_red("\nPlease make a transaction first to view the transaction history.\n")
    else:
        print("Transaction History:")
        if bought_history:
            print("Bought Histories:")
            for history in bought_history:
                timestamp, coin, quantity, price = history
                print_blue(f"Timestamp: {timestamp} | Bought: {quantity} {coin} | Price: ${price:.2f} USD")

        if sold_history:
            print("Sold Histories:")
            for history in sold_history:
                timestamp, coin, quantity, price = history
                print_red(f"Timestamp: {timestamp} | Sold: {quantity} {coin} | Price: ${price:.2f} USD")


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
    print("13. Total assets")
    print("14. Transaction History")


# Main program
if __name__ == "__main__":
    state = load_state()
    favorites_list = state["favorites"]
    populated_list = state.get("populated_list", [])
    total_balance = state.get("total_balance", 0)

    # Make the initial API request to get the coins list
    coins_list = check_coins_list()
    state["coins_list"] = coins_list
    save_state(state)

    status = check_service_status()
    credit = check_service_credits()

    if not populated_list:
        pre_populate_list()

    display_credit(credit)
    display_status(status)

    # Start the background thread to update the coins list
    coins_thread = threading.Thread(target=update_coins_list)
    coins_thread.daemon = True  # This allows the thread to exit when the main program exits
    coins_thread.start()

    while True:
        display_menu()
        choice = input("Select an option (1-14) or 0 to exit the program: ")

        try:
            choice = int(choice)

            if choice == 1:
                display_coins_list()
            elif choice == 2:
                while True:
                    print("Option 2 selected.")
                    print("Select a cryptocurrency to add to your favorites:")
                    for i, coin in enumerate(populated_list, 1):
                        print(f"{i}. {coin}")
                    print("Enter the corresponding number, or 'q' to quit.")

                    coin_choice = input("Your choice: ")
                    if coin_choice == "q":
                        break  # Return to the main menu
                    try:
                        coin_choice = int(coin_choice)
                        if 1 <= coin_choice <= len(populated_list):
                            coin_name = populated_list[coin_choice - 1]
                            add_to_favorites(coin_name)
                            print_green(f"Updated favorites list result is: {state['favorites']}")
                            break  # Successfully added, return to the main menu
                        else:
                            print_red("Invalid number. Please enter a valid number or 'q' to quit.")
                    except ValueError:
                        print_red("Invalid input. Please enter a valid number or 'q' to quit.")
            elif choice == 3:
                if not state["favorites"]:
                    print_red("Your favorites list is currently empty.")
                else:
                    while True:
                        print("Option 3 selected.")
                        print("Select a cryptocurrency to remove from your favorites:")
                        for i, coin in enumerate(state["favorites"], 1):
                            print_green(f"{i}. {coin}")
                        print("Enter the corresponding number, or 'q' to quit.")

                        coin_choice = input("Your choice: ")
                        if coin_choice == "q":
                            break  # Return to the main menu
                        try:
                            coin_choice = int(coin_choice)
                            if 1 <= coin_choice <= len(state["favorites"]):
                                coin_name = state["favorites"][coin_choice - 1]
                                remove_from_favorites(coin_name)
                                break  # Successfully removed, return to the main menu
                            else:
                                print_red("Invalid number. Please enter a valid number or 'q' to quit.")
                        except ValueError:
                            print_red("Invalid input. Please enter a valid number or 'q' to quit.")
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
                buy_cryptocurrency()
            elif choice == 9:
                sell_cryptocurrency()
            elif choice == 10:
                # Make a deposit
                print_green(f"Current balance is ${total_balance:.2f}")
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
            elif choice == 13:
                check_total_assets()
            elif choice == 14:
                display_transaction_history()
            elif choice == 0:
                print_green(f"\nYou selected Option {choice}. The program will now exit. Thank you.\n")
                break
            else:
                print_red("Invalid choice. Please select a number between 1 and 12 or 0 to exit the program.")
        except ValueError:
            print_red("Invalid input. Please enter a number.")

