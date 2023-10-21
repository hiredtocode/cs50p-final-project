import time
import requests
import json
import os
import threading
from tabulate import tabulate

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

# Function to print text in orange
def print_orange(text):
    print(f"\033[93m{text}\033[0m")

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

# Function to check the service status
def check_service_status():
    url = "https://api.livecoinwatch.com/status"
    payload = {}
    headers = {'content-type': 'application/json', 'x-api-key': 'bd95c726-08ea-447d-94e5-00088cf86908'}

    response = requests.request("POST", url, headers=headers, data=payload)
    return response.text

# Function to display "Online" in green or "Offline" in red
def display_status(status):
    if status == "{}":
        return "\033[92mOnline\033[0m"
    else:
        return "\033[91mOffline\033[0m {status}"

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

# Function to auto-update the coins list in the background every 60 seconds
def update_coins_list():
    global coins_list  # Make the coins_list variable global

    while True:
        coins_list = check_coins_list()
        # Sleep for a while before updating again
        time.sleep(60)  # Adjust the sleep duration as needed

# Function to add retrieved coins list to the state
def add_coins_list_to_state():
    coins_list = check_coins_list()
    state["coins_list"] = coins_list
    save_state(state)

# Pre-populate available list which gets triggered when option 12 is requested
def pre_populate_list():
    print_green("\nPre-populating the coins list...")
    for coin in coins_list:
        code = coin['code']
        populated_list.append(code)
        state["populated_list"] = populated_list
        save_state(state)
    print_green(f"Successfully pre-populated coins list.\n")
    return "Pre-population of coins list completed successfully."

# Option 1 - Function to display the coins list from the state
def display_coins_list():
    coins_list = state.get("coins_list", [])
    if coins_list:
        for i, coin in enumerate(coins_list[:10], 1):
            code = coin['code']
            rate = "{:,.2f}".format(coin['rate'])
            if code != "USDT":  # Skip displaying USDT
                print_green(f"{i}. {code} ${rate} USD")
    else:
        print_red("Coins list not available. Please update it.")

# Option 2 - Add coins to the favorites list
def add_to_favorites():
    print_orange("\nOption 2 selected - Add a cryptocurrency to my favorites.")
    print_green(f"\nYour current favorite list contains: {state['favorites']}\n")
    while True:
        print("Select a cryptocurrency to add to your favorites:")
        for i, coin in enumerate(populated_list, 1):
            print(f"{i}. {coin}")
        print("Enter the corresponding number, or press the Enter key to return to the main menu.")

        choice = input("Your choice: ")
        if choice == "":
            break  # Return to the main menu
        try:
            choice = int(choice)
            if 1 <= choice <= len(populated_list):
                coin_name = populated_list[choice - 1]
                if coin_name not in state["favorites"]:
                    state["favorites"].append(coin_name)  # Add the coin to favorites
                    save_state(state)
                    print_green(f"{coin_name} has been added to your favorites list.")
                    print_green(f"Updated favorites list: {state['favorites']}")
                else:
                    print_red(f"{coin_name} is already in your favorites list.")
            else:
                print_red("Invalid number. Please enter a valid number or press the Enter key to return to the main menu.")
        except ValueError:
            print_red("Invalid input. Please enter a valid number or press the Enter key to return to the main menu.")

# Option 3 - Remove selected cryptocurrency from favorites list
def remove_crypto_from_favorites():
    print_orange("\nOption 3 selected - Remove coin from my favorites.")
    if not state["favorites"]:
        print_red("\nYour favorites list is currently empty.\n")
    else:
        while True:
            print("Select a cryptocurrency to remove from your favorites:")
            for i, coin in enumerate(state["favorites"], 1):
                print_green(f"{i}. {coin}")
            print("Enter the corresponding number, or press enter to return to the main menu.")

            coin_choice = input("Your choice: ")
            if coin_choice == '':
                break  # Return to the main menu
            try:
                coin_choice = int(coin_choice)
                if 1 <= coin_choice <= len(state["favorites"]):
                    coin_name = state["favorites"][coin_choice - 1]
                    remove_from_favorites(coin_name)
                    if not state["favorites"]:
                        break
                    else:
                        press_any_key_to_continue()
                else:
                    print_red("Invalid number. Please enter a valid number or press the Enter key to return to the main menu.")
            except ValueError:
                print_red("Invalid input. Please enter a valid number or press the Enter key to return to the main menu.")


# Option 3.5 - Function to remove a cryptocurrency from favorites
def remove_from_favorites(code):
    global favorites_list
    favorites_set = set(state["favorites"])
    if code in favorites_set:
        favorites_set.remove(code)
        state["favorites"] = list(favorites_set)  # Convert back to a list
        favorites_list = state["favorites"]  # Update favorites_list
        save_state(state)
        print_green(f"Successfully removed {code} from the favorites list.")
        if not favorites_set:
            print_red(f"Your favorite list is empty.")
        else:
            print_green(f"Updated favorite list: {state['favorites']}")
    else:
        print_red(f"{code} is not in your favorites list.")
        return

# Option 4 - Display my favorites
def display_favorite_list():
    print_orange("\nOption 4 selected - Display favorites.")

    if not favorites_list:
        print_red("\nYour favorites list is empty.\n")
    else:
        print_green("Favorites list:")
        for i, coin_code in enumerate(favorites_list, 1):
            coin_info = [coin for coin in coins_list if coin['code'] == coin_code][0]
            rate = coin_info['rate']
            print_green(f"{i}. {coin_code} ${rate:.2f} USD")

        press_any_key_to_continue()

# Option 5 - Function to display the current deposited balance
def display_deposited_balance(balance):
    print_orange("\nOption 5 selected - My total amount of USD")
    if balance == 0:
        print_red(f"\nTotal balance is: ${balance:.2f} USD\n")
        press_any_key_to_continue()
    else:
        print_green(f"\nTotal balance is: ${balance:.2f} USD\n")
        press_any_key_to_continue()

# Option 6 - Function to check the total assets
def check_total_assets():
    total_assets = state.get("total_assets", {})
    total_balance = state.get("total_balance", 0)

    grand_total = total_balance  # Initialize grand total with the total balance

    if not total_assets and total_balance == 0:
        print_red("You currently own no cryptocurrencies.")
        print_red("You currently own no USD.")
        press_any_key_to_continue()
    elif not total_assets:
        total_value_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin['code'] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info['rate']
            total_value_in_usd += value_in_usd
            print_green(f"{code}: {formatted_quantity} {code} | Value in fiat: ${value_in_usd:.2f}")
        print_green(f"Total Value in fiat of all assets: ${total_value_in_usd:.2f} in cryptocurrency")
        print_green(f"Total Balance in fiat: ${total_balance:.2f}")
        grand_total += total_value_in_usd  # Add the total value of assets to the grand total
        state["grand_total"] = grand_total  # Update the state with the grand total
        print_green(f"Grand Total in fiat: ${grand_total:.2f}")
        press_any_key_to_continue()
    else:
        print_green("\nYour assets:")
        total_amount_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin['code'] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info['rate']
            total_amount_in_usd += value_in_usd
            print_green(f"{code}: {formatted_quantity} {code} | Quantity Value in fiat: ${value_in_usd:.2f}")
        print_green(f"Total Value in fiat of all assets: ${total_amount_in_usd:.2f} in cryptocurrency")
        print_green(f"Total Balance in fiat: ${total_balance:.2f}")
        grand_total += total_amount_in_usd  # Add the total value of assets to the grand total
        state["grand_total"] = grand_total  # Update the state with the grand total
        print_green(f"Grand Total in fiat (cryptocurrency + fiat): ${grand_total:.2f}")
        press_any_key_to_continue()

# Option 7 - Display profits and losses
def display_profit_loss():
    global total_balance

    print_orange("\nOption 7 selected - Display Profit / Loss")

    total_assets = state.get("total_assets", {})
    bought_history = state.get("bought_history", [])
    coins_list = state.get("coins_list", [])

    if not total_assets:
        print_red("You currently own no cryptocurrencies.")
        press_any_key_to_continue()  # Added to handle Enter key press
        return

    for code, quantity in total_assets.items():
        coin_info = [coin for coin in coins_list if coin['code'] == code][0]
        current_value = quantity * coin_info['rate']

        # Calculate the initial purchase price and total purchase cost
        total_purchase_cost = 0
        total_quantity_purchased = 0

        for history in bought_history:
            timestamp, coin, hist_quantity, price = history
            if coin == code:
                total_purchase_cost += price
                total_quantity_purchased += hist_quantity

        if total_quantity_purchased == 0:
            purchase_price = 0  # Avoid division by zero
        else:
            purchase_price = total_purchase_cost / total_quantity_purchased

        # Calculate the current value and profit/loss
        profit_loss = current_value - (purchase_price * quantity)

        # Determine whether it's a profit or loss
        if profit_loss >= 0:
            color = "\033[92m"  # Green for profit
        else:
            color = "\033[91m"  # Red for loss

        formatted_quantity = "{:.6f}".format(quantity)
        formatted_profit_loss = "{:.2f}".format(profit_loss)

        print(f"{code}: {formatted_quantity} {code} | Current Value: ${current_value:.2f} USD | "
              f"Average Purchase Price: ${purchase_price:.2f} USD | "
              f"Profit/Loss: {color}${formatted_profit_loss} USD\033[0m")

    press_any_key_to_continue()

# Option 8 - Function to buy cryptocurrency
def buy_cryptocurrency():
    global total_balance
    total_balance = state.get("total_balance", 0)

    if "total_assets" not in state:
        state["total_assets"] = {}

    print_orange("\nOption 8 selected - Buy cryptocurrency\n")
    display_coins_list()
    total_amount_in_usd = 0
    while True:
        choice = int(input("Select a cryptocurrency to buy or press Enter to return to the main menu: "))
        if choice == "":
            break
        try:
            choice = int(choice)
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
                print_green(f"Your new total balance in fiat is: ${total_balance:.2f}")

                # Calculate and update the grand total
                grand_total = total_balance
                for code, quantity in state["total_assets"].items():
                    coin_info = [coin for coin in coins_list if coin['code'] == code][0]
                    grand_total += quantity * coin_info['rate']

                state["grand_total"] = grand_total
                print_green(f"Grand Total in fiat (cryptocurrency + fiat): ${grand_total:.2f}")

                return total_balance
            else:
                print_red("Insufficient balance. Please deposit more and try again. Loading main menu...")
                print("Returning to the main menu...")
                return
        except ValueError:
            print_red("Invalid input. Please enter a valid amount in USD.")

# Option 9 - Sell cryptocurrency
def sell_cryptocurrency():
    global total_balance
    print_orange("\nOption 9 selected - Sell cryptocurrency")

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
            print_green(f"{i}. {code} | Value in fiat: ${value_in_usd:.2f}")

        print("Enter the corresponding number or press Enter to return to the main menu: ")

        try:
            choice = input()
            if choice == "":
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
                            press_any_key_to_continue()
                            check_total_assets()
                            press_any_key_to_continue()
                            return  # Return to the main menu

                        else:
                            print_red("Insufficient balance. Please enter a lower amount.")
                    except ValueError:
                        print_red("Invalid input. Please enter a valid number.")
            else:
                print_red("Invalid choice. Please select a valid number.")
        except ValueError:
            print_red("Invalid input. Please enter a number or press the Enter key to return to the main menu.")

# Option 10 - Make a deposit
def make_a_deposit():
    # Make a deposit
    global total_balance
    print_green(f"Current balance is ${total_balance:.2f}")
    deposit_amount = float(input("Enter the deposit amount or press the Enter key to cancel: $"))
    if deposit_amount <= 0:
        print_red("Invalid deposit amount.")
        press_any_key_to_continue()

    else:
        total_balance = make_deposit(total_balance, deposit_amount)
        print_green(f"Successfully deposited ${deposit_amount:.2f}.")
        print_green(f"The total balance is now: ${total_balance:.2f}.")
        press_any_key_to_continue()

# Option 10.5 - Function to make a deposit
def make_deposit(balance, amount):
    print_orange("\nOption 10 selected - Make a deposit")
    balance += amount
    state["total_balance"] = balance

    # Record the deposit in the transaction history
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    deposit_history = state.get("deposit_history", [])
    deposit_history.append((timestamp, amount))
    state["deposit_history"] = deposit_history

    save_state(state)
    return balance

# Option 11 - withdrawal
def make_a_withdraw():
    global total_balance
    print_orange("\nOption 11 selected.") # Make a withdrawal
    print_green(f"Current amount is ${total_balance:.2f}")
    withdrawal_amount = float(input("Enter the withdrawal amount or press the Enter key to cancel: $"))
    if withdrawal_amount <= 0 or withdrawal_amount > total_balance:
        print_red("Insufficient fund.")
        press_any_key_to_continue()
    else:
        total_balance = make_withdrawal(total_balance, withdrawal_amount)
        print_green(f"Successfully withdrew ${withdrawal_amount:.2f}.")
        print_green(f"The total balance is now: ${total_balance:.2f}.")
        press_any_key_to_continue()

# Option 11.5 - Function to make a withdrawal
def make_withdrawal(balance, amount):
    print_orange("\nOption 11 selected - Make a withdraw")
    balance -= amount
    state["total_balance"] = balance

    # Record the withdrawal in the transaction history
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    withdraw_history = state.get("withdraw_history", [])
    withdraw_history.append((timestamp, amount))
    state["withdraw_history"] = withdraw_history

    save_state(state)
    return balance

# Option 12 - Function to reset the state
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

# Option 13 - Function to display transaction history
def display_transaction_history():
    bought_history = state.get("bought_history", [])
    sold_history = state.get("sold_history", [])
    deposit_history = state.get("deposit_history", [])
    withdraw_history = state.get("withdraw_history", [])

    if not bought_history and not sold_history and not deposit_history and not withdraw_history:
        print_red("\nPlease make a transaction first to view the transaction history.\n")
    else:
        print("Transaction History:")

        # Display bought histories
        if bought_history:
            print("Bought Histories:")
            for history in bought_history:
                timestamp, coin, quantity, price = history
                print_blue(f"Bought: {quantity} {coin} | Price: ${price:.2f} USD | Timestamp: {timestamp}")

        # Display sold histories
        if sold_history:
            print("Sold Histories:")
            for history in sold_history:
                timestamp, coin, quantity, price = history
                print_red(f"Sold: {quantity} {coin} | Price: ${price:.2f} USD | Timestamp: {timestamp}")

        # Display deposit histories
        if deposit_history:
            print("Deposit Histories:")
            for history in deposit_history:
                timestamp, amount = history
                print("\033[94m", end="")  # Dark blue
                print(f"Deposit: ${amount:.2f} USD | Timestamp: {timestamp}")
                print("\033[0m", end="")  # Reset color

        # Display withdraw histories
        if withdraw_history:
            print("Withdraw Histories:")
            for history in withdraw_history:
                timestamp, amount = history
                print("\033[91m", end="")  # Red
                print(f"Withdraw: ${amount:.2f} USD | Timestamp: {timestamp}")
                print("\033[0m", end="")  # Reset color

# Function to display the menu
def display_menu():
    print_orange("\nWhat would you like to do?")
    print("1. Show all available cryptocurrency coins.")
    print("2. Add a cryptocurrency to my favorites.")
    print("3. Remove cryptocurrency from my favorites.")
    print("4. Display my favorites list.")
    print("5. Total fiat balance.")
    print("6. Total assets.")
    print("7. Profit / Loss status.")
    print("8. Buy cryptocurrency.")
    print("9. Sell cryptocurrency.")
    print("10. Make a deposit.")
    print("11. Make a withdrawal.")
    print("12. Reset all data.")
    print("13. Transaction History.\n")

def press_any_key_to_continue():
    input("Press any key to continue...")

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

    online_status = display_status(status)

    print(f"\nThe API status is {online_status} and you have {credit} credit(s) remaining.\n")

    # Start the background thread to update the coins list
    coins_thread = threading.Thread(target=update_coins_list)
    coins_thread.daemon = True  # This allows the thread to exit when the main program exits
    coins_thread.start()

    while True:
        display_menu()
        choice = input("Select an option (1-13) or press the Ctrl+C to exit the program: ")

        try:
            choice = int(choice)

            if choice == 1:
                display_coins_list()
                press_any_key_to_continue()
            elif choice == 2:
                add_to_favorites()
            elif choice == 3:
                remove_crypto_from_favorites()
            elif choice == 4:
                display_favorite_list()
            elif choice == 5:
                display_deposited_balance(total_balance)
            elif choice == 6:
                check_total_assets()
            elif choice == 7:
                display_profit_loss()
            elif choice == 8:
                buy_cryptocurrency()
                press_any_key_to_continue()
            elif choice == 9:
                sell_cryptocurrency()
            elif choice == 10:
                make_a_deposit()
            elif choice == 11:
                make_a_withdraw()
            elif choice == 12:
                reset_state()
                press_any_key_to_continue()
            elif choice == 13:
                display_transaction_history()
                press_any_key_to_continue()
            elif choice == 0:
                print_green(f"\nYou selected Option {choice}. The program will now exit. Thank you.\n")
                break
            else:
                print_red("Invalid choice. Please select a number between 1 and 13 or press ctrl+C to exit the program.")
        except ValueError:
            print_red("Enter pressed, returning to the main menu.")

