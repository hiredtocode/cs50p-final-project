import time
import requests
import json
import os
import threading

# Constants for Colors
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_YELLOW = "\033[93m"
COLOR_WHITE = "\033[97m"
COLOR_DARK_GRAY = "\033[90m"

# API Endpoints and Headers
API_BASE_URL = "https://api.livecoinwatch.com"
API_STATUS_ENDPOINT = "/status"
API_CREDITS_ENDPOINT = "/credits"
API_COINS_LIST_ENDPOINT = "/coins/list"
API_KEY = "bd95c726-08ea-447d-94e5-00088cf86908"
HEADERS = {"content-type": "application/json", "x-api-key": API_KEY}


class ProgramState:
    def __init__(self):
        self.favorites = []
        self.total_balance = 0
        self.total_assets = {}
        self.coins_list = []
        self.populated_list = []
        self.deposit_history = []
        self.withdraw_history = []
        self.bought_history = []
        self.sold_history = []
        self.grand_total = 0

    @classmethod
    def reset_state(cls):
        # Create an instance first
        instance = cls()  # Create a new instance of ProgramState
        instance.load_state()  # Use the instance to call load_state
        instance.coins_list.clear()
        instance.coins_list.extend(UtilityFunctions.check_coins_list())
        instance.pre_populate_list()  # Use the instance to call pre_populate_list

    def save_state(self):
        # Create a dictionary containing the state data you want to save
        state_data = {
            "favorites": self.favorites,
            "total_balance": self.total_balance,
            "total_assets": self.total_assets,
            "coins_list": self.coins_list,
            "populated_list": self.populated_list,
            "deposit_history": self.deposit_history,
            "withdraw_history": self.withdraw_history,
            "bought_history": self.bought_history,
            "sold_history": self.sold_history,
            "grand_total": self.grand_total,
        }

        # Open the state.json file in write mode and save the state data
        with open("state.json", "w") as file:
            json.dump(state_data, file)

    def load_state(self):
        if os.path.isfile("state.json"):
            with open("state.json", "r") as file:
                state_dict = json.load(file)
        else:
            state_dict = {
                "favorites": [],
                "total_balance": 0,
                "total_assets": {},
                "coins_list": [],
                "populated_list": [],
                "deposit_history": [],
                "withdraw_history": [],
                "bought_history": [],
                "sold_history": [],
                "grand_total": 0,
            }

        # Assign the loaded state values to the class attributes
        self.favorites = state_dict["favorites"]
        self.total_balance = state_dict["total_balance"]
        self.total_assets = state_dict["total_assets"]
        self.coins_list = state_dict["coins_list"]
        self.populated_list = state_dict["populated_list"]
        self.deposit_history = state_dict["deposit_history"]
        self.withdraw_history = state_dict["withdraw_history"]
        self.bought_history = state_dict["bought_history"]
        self.sold_history = state_dict["sold_history"]
        self.grand_total = state_dict["grand_total"]

    def get_coin_list(self):
        self.coins_list = UtilityFunctions.check_coins_list()

    def pre_populate_list(self):
        print_color("Pre-populating the coins list...")

        # Debug: Print the initial coins_list
        # print("Initial coins_list:", self.coins_list)

        for coin in self.coins_list:
            code = coin["code"]
            self.populated_list.append(code)

        self.save_state()  # Save the state within the class
        print_color("\nSuccessfully pre-populated coins list.")


# Function to print_color text in color
def print_color(text, color=COLOR_GREEN):
    print(f"{color}{text}{COLOR_RESET}")


class UtilityFunctions:
    # Function to check the service status
    @staticmethod
    def check_service_status():
        url = f"{API_BASE_URL}{API_STATUS_ENDPOINT}"
        response = requests.post(url, headers=HEADERS)
        return response.text

    # Function to display "Online" in green or "Offline" in red
    @staticmethod
    def display_status(status):
        if status == "{}":
            return "\033[92mOnline\033[0m"
        else:
            return "\033[91mOffline\033[0m {status}"

    # Function to check credits
    @staticmethod
    def check_service_credits():
        url = f"{API_BASE_URL}{API_CREDITS_ENDPOINT}"
        response = requests.post(url, headers=HEADERS)
        response_data = json.loads(response.text)
        return response_data.get("dailyCreditsRemaining")

    # Function to check coins list
    @staticmethod
    def check_coins_list():
        url = f"{API_BASE_URL}{API_COINS_LIST_ENDPOINT}"
        payload = json.dumps(
            {
                "currency": "USD",
                "sort": "rank",
                "order": "ascending",
                "offset": 0,
                "limit": 10,
                "meta": False,
            }
        )
        response = requests.post(url, headers=HEADERS, data=payload)
        response_data = json.loads(response.text)
        return response_data

    # Function to auto-update the coins list in the background every 60 seconds
    @staticmethod
    def update_coins_list(coins_list):
        stop_background_thread = UtilityFunctions.stop_background_thread

        while not stop_background_thread:
            try:
                new_coins_list = UtilityFunctions.check_coins_list()

                # Acquire the lock before updating the coins_list
                with coins_list_lock:
                    coins_list.clear()
                    coins_list.extend(new_coins_list)

                # Sleep for a while before updating again
                time.sleep(60)  # Adjust the sleep duration as needed

            except KeyboardInterrupt:  # Handle Ctrl+C gracefully
                stop_background_thread = True
                break


# Option 1 - Function to display the coins list from the state
def display_coins_list():
    coins_list = state.coins_list
    if coins_list:
        for i, coin in enumerate(coins_list[:10], 1):
            code = coin["code"]
            rate = "{:,.2f}".format(coin["rate"])
            if code != "USDT":  # Skip displaying USDT
                print_color(f"{i}. {code} ${rate} USD")
    else:
        print_color("Coins list not available. Please update it.", COLOR_RED)


# Option 2 - Add coins to the favorites list
def add_to_favorites():
    print_color("\nOption 2 selected - Add a cryptocurrency to my favorites.")
    print_color(f"\nYour current favorite list contains: {state.favorites}\n")
    while True:
        print_color("Select a cryptocurrency to add to your favorites:", COLOR_YELLOW)
        for i, coin in enumerate(state.populated_list, 1):
            print_color(f"{i}. {coin}")
        print_color(
            "Enter the corresponding number, or press the Enter key to return to the main menu.",
            COLOR_YELLOW,
        )

        choice = input("Your choice: ")
        if choice == "":
            break  # Return to the main menu
        try:
            choice = int(choice)
            if 1 <= choice <= len(state.populated_list):
                coin_name = state.populated_list[choice - 1]
                if coin_name not in state.favorites:
                    state.favorites.append(coin_name)  # Add the coin to favorites
                    state.save_state()  # Save the updated state to state.json
                    print_color(
                        f"\n{coin_name} has been added to your favorites list.\n"
                    )
                    print_color(f"Updated favorites list: {state.favorites}")
                else:
                    print_color(
                        f"\n{coin_name} is already in your favorites list.\n", COLOR_RED
                    )
            else:
                print_color(
                    "Invalid number. Please enter a valid number or press the Enter key to return to the main menu.",
                    COLOR_RED,
                )
        except ValueError:
            print_color(
                "Invalid input. Please enter a valid number or press the Enter key to return to the main menu.",
                COLOR_RED,
            )


# Option 3 - Remove selected cryptocurrency from favorites list
def remove_crypto_from_favorites():
    print_color("\nOption 3 selected - Remove coin from my favorites.")
    favorites = state.favorites  # Retrieve the favorites list
    if not favorites:
        print_color(
            "\nYour favorites list is currently empty. Returning to the main menu...\n",
            COLOR_RED,
        )

    else:
        while True:
            # print_color(f"\nFavorites list currently contains: {favorites}\n")
            print_color(
                "Select a cryptocurrency to remove from your favorites:", COLOR_YELLOW
            )
            for i, coin in enumerate(favorites, 1):
                print_color(f"{i}. {coin}")
            print_color(
                "Enter the corresponding number, or press enter to return to the main menu.",
                COLOR_YELLOW,
            )

            coin_choice = input("Your choice: ")
            if coin_choice == "":
                break  # Return to the main menu
            try:
                coin_choice = int(coin_choice)
                if 1 <= coin_choice <= len(favorites):
                    coin_name = favorites[coin_choice - 1]
                    remove_from_favorites(coin_name)
                    favorites = state.favorites

                    if not favorites:
                        break
                    else:
                        press_any_key_to_continue()
                else:
                    print_color(
                        "Invalid number. Please enter a valid number or press the Enter key to return to the main menu.",
                        COLOR_RED,
                    )
            except ValueError:
                print_color(
                    "Invalid input. Please enter a valid number or press the Enter key to return to the main menu.",
                    COLOR_RED,
                )


# Option 3.5 - Function to remove a cryptocurrency from favorites
def remove_from_favorites(code):
    favorites_set = set(state.favorites)
    if code in favorites_set:
        favorites_set.remove(code)
        state.favorites = list(favorites_set)  # Convert back to a list
        state.save_state()
        print_color(
            f"\nSuccessfully removed {code} from the favorites list.\n", COLOR_RED
        )
        if not favorites_set:
            print_color(f"Your favorite list is empty.", COLOR_RED)
        else:
            print_color(f"Updated favorite list: {state.favorites}")
    else:
        print_color(f"{code} is not in your favorites list.", COLOR_RED)
        return


# Option 4 - Display my favorites
def display_favorite_list():
    print_color("\nOption 4 selected - Display favorites.")

    # Access the favorites list from the state
    favorites = state.favorites

    if not favorites:
        print_color("\nYour favorites list is empty.\n", COLOR_RED)
    else:
        print_color("Favorites list:")
        for i, coin_code in enumerate(favorites, 1):
            # Access coin info from the coins_list in the state
            coin_info = [
                coin for coin in state.coins_list if coin["code"] == coin_code
            ][0]
            rate = coin_info["rate"]
            print_color(f"{i}. {coin_code} ${rate:.2f} USD")

        press_any_key_to_continue()


# Option 5 - Function to display the current deposited balance
def display_deposited_balance():
    balance = state.total_balance
    print_color("\nOption 5 selected - My total amount of USD")
    if balance == 0:
        print_color(f"\nTotal balance is: ${balance:.2f} USD\n", COLOR_RED)
        press_any_key_to_continue()
    else:
        print_color(f"\nTotal balance is: ${balance:.2f} USD\n")
        press_any_key_to_continue()


# Option 6 - Function to check the total assets
def check_total_assets():
    total_assets = state.total_assets
    total_balance = state.total_balance

    grand_total = total_balance  # Initialize grand total with the total balance

    if not total_assets and total_balance == 0:
        print_color("You currently own no cryptocurrencies.", COLOR_RED)
        print_color("You currently own no USD.", COLOR_RED)
        press_any_key_to_continue()
    elif not total_assets:
        total_value_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin["code"] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info["rate"]
            total_value_in_usd += value_in_usd
            print_color(
                f"{code}: {formatted_quantity} {code} | Value in fiat: ${value_in_usd:.2f}"
            )
        if total_value_in_usd == 0:
            print_color(f"Total Balance in fiat: ${total_balance:.2f}")
            grand_total += (
                total_value_in_usd  # Add the total value of assets to the grand total
            )
            state.grand_total = grand_total  # Update the state with the grand total
            print_color(f"Grand Total in fiat: ${grand_total:.2f}")
        else:
            print_color(f"Total Balance in fiat: ${total_balance:.2f}")
            print_color(
                f"Total Value in fiat of all assets: ${total_value_in_usd:.2f} in cryptocurrency"
            )
            grand_total += (
                total_value_in_usd  # Add the total value of assets to the grand total
            )
            state.grand_total = grand_total  # Update the state with the grand total
            print_color(f"Grand Total in fiat: ${grand_total:.2f}")
    else:
        print_color("\nYour assets:")
        total_amount_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin["code"] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info["rate"]
            total_amount_in_usd += value_in_usd
            print_color(
                f"{code}: {formatted_quantity} {code} | Quantity Value in fiat: ${value_in_usd:.2f}"
            )
        print_color(
            f"Total Value in fiat of all assets: ${total_amount_in_usd:.2f} in cryptocurrency"
        )
        print_color(f"Total Balance in fiat: ${total_balance:.2f}")
        grand_total += (
            total_amount_in_usd  # Add the total value of assets to the grand total
        )
        state.grand_total = grand_total  # Update the state with the grand total
        print_color(f"Grand Total in fiat (cryptocurrency + fiat): ${grand_total:.2f}")


# Option 7 - Function to display profit and loss
def display_profit_loss():
    # Calculate the current value of your cryptocurrency holdings

    total_assets = state.total_assets
    total_balance = state.total_balance
    grand_total = state.grand_total

    if not total_assets and total_balance == 0:
        print_color("You currently own no cryptocurrencies.", COLOR_RED)
        print_color("You currently own no USD.", COLOR_RED)
        press_any_key_to_continue()
    elif not total_assets:
        print_color("You currently own no cryptocurrencies.", COLOR_RED)
        print_color(f"Total Balance in fiat: ${total_balance:.2f}")
        print_color(f"Grand Total in fiat: ${grand_total:.2f}")
        press_any_key_to_continue()
    else:
        print_color("\nYour assets:")
        total_amount_in_usd = 0
        for code, quantity in total_assets.items():
            coin_info = [coin for coin in coins_list if coin["code"] == code][0]
            formatted_quantity = "{:.6f}".format(quantity)
            value_in_usd = quantity * coin_info["rate"]
            total_amount_in_usd += value_in_usd
            print_color(
                f"{code}: {formatted_quantity} {code} | Quantity Value in fiat: ${value_in_usd:.2f}"
            )
        print_color(
            f"Total Value in fiat of all assets: ${total_amount_in_usd:.2f} in cryptocurrency"
        )
        print_color(f"Total Balance in fiat: ${total_balance:.2f}")
        grand_total += (
            total_amount_in_usd  # Add the total value of assets to the grand total
        )
        state.grand_total = grand_total  # Update the state with the grand total
        print_color(f"Grand Total in fiat (cryptocurrency + fiat): ${grand_total:.2f}")
        press_any_key_to_continue()


# Option 8 - Function to buy cryptocurrency
def buy_cryptocurrency():
    total_balance = state.total_balance

    print_color("\nOption 8 selected - Buy cryptocurrency\n")
    display_coins_list()
    while True:
        choice = int(
            input(
                "Select a cryptocurrency to buy or press Enter to return to the main menu: "
            )
        )
        if choice == "":
            break
        try:
            choice = int(choice)
            if 1 <= choice <= len(coins_list):
                selected_coin = coins_list[choice - 1]
                break
            else:
                print_color("Invalid choice. Please select a valid number.", COLOR_RED)
        except ValueError:
            print_color("Invalid input. Please enter a number.", COLOR_RED)

    while True:
        try:
            amount_to_buy = float(
                input(f"Enter the amount of {selected_coin['code']} to buy (USD): $")
            )
            if amount_to_buy <= 0:
                print_color("Invalid amount. Please enter a positive value.", COLOR_RED)
                continue

            if amount_to_buy <= total_balance:
                coin_name = selected_coin["code"]
                quantity = amount_to_buy / selected_coin["rate"]

                if coin_name in state.total_assets:
                    state.total_assets[coin_name] += quantity
                else:
                    state.total_assets[coin_name] = quantity

                total_balance -= amount_to_buy
                state.total_balance = total_balance

                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

                state.bought_history.append(
                    (timestamp, coin_name, quantity, amount_to_buy)
                )
                state.save_state()

                print_color(
                    f"Successfully bought ${amount_to_buy:.2f} worth of {coin_name}."
                )
                print_color(
                    f"The new total amount of owned {coin_name} is: {state.total_assets[coin_name]:.6f}"
                )
                print_color(f"Your new total balance in fiat is: ${total_balance:.2f}")

                # Calculate and update the grand total
                grand_total = total_balance
                for code, quantity in state.total_assets.items():
                    coin_info = [coin for coin in coins_list if coin["code"] == code][0]
                    grand_total += quantity * coin_info["rate"]

                state.grand_total = grand_total
                print_color(
                    f"Grand Total in fiat (cryptocurrency + fiat): ${grand_total:.2f}"
                )

                return total_balance
            else:
                print_color(
                    "Insufficient balance. Please deposit more and try again. Loading main menu...",
                    COLOR_RED,
                )
                print_color(
                    f"Your current fiat balance is: ${total_balance:.2f}", COLOR_RED
                )
                pass
        except ValueError:
            print_color("Invalid input. Please enter a valid amount in USD.", COLOR_RED)


# Option 9 - Sell cryptocurrency
def sell_cryptocurrency():
    total_balance = state.total_balance
    print_color("\nOption 9 selected - Sell cryptocurrency")

    while True:
        # Display the list of assets the user owns
        check_total_assets()

        assets = state.total_assets
        asset_codes = list(assets.keys())

        if not assets:
            print_color("You currently own no cryptocurrencies.", COLOR_RED)
            return  # Return to the main menu

        print_color("\nSelect a cryptocurrency to sell:", COLOR_YELLOW)
        for i, code in enumerate(asset_codes, 1):
            coin_info = [coin for coin in coins_list if coin["code"] == code][0]
            value_in_usd = assets[code] * coin_info["rate"]
            print_color(f"{i}. {code} | Value in fiat: ${value_in_usd:.2f}")

        print_color(
            "\nChoose the coin you'd like to sell or press Enter to return to the main menu: ",
            COLOR_YELLOW,
        )

        try:
            choice = input()
            if choice == "":
                return  # Return to the main menu
            choice = int(choice)

            if 1 <= choice <= len(asset_codes):
                selected_code = asset_codes[choice - 1]
                coin_info = [
                    coin for coin in coins_list if coin["code"] == selected_code
                ][0]

                # Calculate the current value of the selected cryptocurrency
                current_value = assets[selected_code] * coin_info["rate"]

                print_color(
                    f"You currently own {assets[selected_code]:.6f} {selected_code} valued at ${current_value:.2f} USD"
                )
                while True:
                    try:
                        amount_to_sell = float(
                            input(
                                f"{COLOR_YELLOW}Enter the amount of {selected_code} to sell (USD): ${COLOR_RESET}"
                            )
                        )
                        if amount_to_sell <= 0:
                            print_color(
                                "Invalid amount. Please enter a positive value.",
                                COLOR_RED,
                            )
                            continue

                        if amount_to_sell <= current_value:
                            # Update the total balance by adding the selling amount
                            total_balance += amount_to_sell
                            state.total_balance = total_balance

                            # Update the total_assets dictionary with the newly sold coin and quantity
                            assets[selected_code] -= amount_to_sell / coin_info["rate"]
                            state.total_assets = assets

                            # Get the current timestamp
                            timestamp = time.strftime("%Y-%m-d %H:%M:%S")

                            # Append the transaction details to the sold history
                            state.sold_history.append(
                                (
                                    timestamp,
                                    selected_code,
                                    amount_to_sell / coin_info["rate"],
                                    amount_to_sell,
                                )
                            )
                            state.save_state()

                            print_color(
                                f"\nSuccessfully sold ${amount_to_sell:.2f} worth of {selected_code}.\n"
                            )
                            press_any_key_to_continue()
                            check_total_assets()
                            press_any_key_to_continue()
                            return  # Return to the main menu

                        else:
                            print_color(
                                "Insufficient balance. Please enter a lower amount.",
                                COLOR_RED,
                            )
                    except ValueError:
                        print_color(
                            "Invalid input. Please enter a valid number.", COLOR_RED
                        )
            else:
                print_color("Invalid choice. Please select a valid number.", COLOR_RED)
        except ValueError:
            print_color(
                "Invalid input. Please enter a number or press the Enter key to return to the main menu.",
                COLOR_RED,
            )


# Option 10 - Make a deposit
def make_a_deposit():
    # Make a deposit
    total_balance = state.total_balance
    print_color(f"Current balance is ${total_balance:.2f}")
    deposit_amount = float(
        input("Enter the deposit amount or press the Enter key to cancel: $")
    )
    if deposit_amount <= 0:
        print_color("Invalid deposit amount.", COLOR_RED)
        press_any_key_to_continue()

    else:
        total_balance = make_deposit(total_balance, deposit_amount)
        print_color(f"Successfully deposited ${deposit_amount:.2f}.")
        print_color(f"The total balance is now: ${total_balance:.2f}.")
        press_any_key_to_continue()


# Option 10.5 - Function to make a deposit
def make_deposit(balance, amount):
    deposit_history = state.deposit_history
    balance += amount
    state.total_balance = balance

    # Record the deposit in the transaction history
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    deposit_history.append((timestamp, amount))
    state.deposit_history = deposit_history

    state.save_state()
    return balance


# Option 11 - withdrawal
def make_a_withdraw():
    total_balance = state.total_balance
    print_color("\nOption 11 selected.")  # Make a withdrawal
    print_color(f"Current amount is ${total_balance:.2f}")
    withdrawal_amount = float(
        input("Enter the withdrawal amount or press the Enter key to cancel: $")
    )
    if withdrawal_amount <= 0 or withdrawal_amount > total_balance:
        print_color("Insufficient fund.", COLOR_RED)
        press_any_key_to_continue()
    else:
        total_balance = make_withdrawal(total_balance, withdrawal_amount)
        print_color(f"Successfully withdrew ${withdrawal_amount:.2f}.")
        print_color(f"The total balance is now: ${total_balance:.2f}.")
        press_any_key_to_continue()


# Option 11.5 - Function to make a withdrawal
def make_withdrawal(balance, amount):
    print_color("\nOption 11 selected - Make a withdraw")
    balance -= amount
    state.total_balance = balance

    # Record the withdrawal in the transaction history
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    withdraw_history = state.withdraw_history
    withdraw_history.append((timestamp, amount))
    state.withdraw_history = withdraw_history

    state.save_state()
    return balance


# Option 12 - Function to reset the state
def reset_state():
    state.reset_state()
    state.save_state()  # Save the reset state to the state.json file
    print_color("State reset successfully.", COLOR_GREEN)


# Option 13 - Function to display transaction history
def display_transaction_history():
    bought_history = state.bought_history
    sold_history = state.sold_history
    deposit_history = state.deposit_history
    withdraw_history = state.withdraw_history

    total_amount_bought = 0
    total_amount_sold = 0
    total_amount_deposited = 0
    total_amount_withdrew = 0

    if (
        not bought_history
        and not sold_history
        and not deposit_history
        and not withdraw_history
    ):
        print_color(
            "\nPlease make a transaction first to view the transaction history.\n",
            COLOR_RED,
        )
    else:
        print_color("Transaction History:")

        # Display bought histories
        if bought_history:
            print_color("Bought Histories:")
            for history in bought_history:
                timestamp, coin, quantity, price = history
                print_color(
                    f"Bought: {quantity} {coin} | Price: ${price:.2f} USD | Timestamp: {timestamp}",
                    COLOR_BLUE,
                )

                total_amount_bought += price
        print_color(f"Total bought amount: ${total_amount_bought:.2f}", COLOR_WHITE)

        # Display sold histories
        if sold_history:
            print_color("Sold Histories:")
            for history in sold_history:
                timestamp, coin, quantity, price = history
                print_color(
                    f"Sold: {quantity} {coin} | Price: ${price:.2f} USD | Timestamp: {timestamp}"
                )
                total_amount_sold += price
        print_color(f"Total sold amount: ${total_amount_sold:.2f}", COLOR_WHITE)

        # Display deposit histories
        if deposit_history:
            print_color("Deposit Histories:")
            for history in deposit_history:
                timestamp, amount = history
                print_color(f"Deposit: ${amount:.2f} USD | Timestamp: {timestamp}")
                total_amount_deposited += amount
        print_color(
            f"Total deposited amount: ${total_amount_deposited:.2f}", COLOR_WHITE
        )

        # Display withdraw histories
        if withdraw_history:
            print_color("Withdraw Histories:", COLOR_RED)
            for history in withdraw_history:
                timestamp, amount = history
                print_color(
                    f"Withdraw: ${amount:.2f} USD | Timestamp: {timestamp}", COLOR_RED
                )
                total_amount_withdrew += amount
        print_color(f"Total withdrew amount: ${total_amount_withdrew:.2f}", COLOR_WHITE)


# Function to display the menu
def display_menu(state):
    menu_options = [
        ("Show all available cryptocurrency coins.", True),
        ("Add a cryptocurrency to my favorites.", True),
        ("Remove cryptocurrency from my favorites.", bool(state.favorites)),
        ("Display my favorites list.", bool(state.favorites)),
        ("Total fiat balance.", bool(state.total_balance)),
        ("Total assets.", bool(state.total_assets or state.total_balance > 0)),
        ("Profit / Loss status.", bool(state.total_assets)),
        ("Buy cryptocurrency.", bool(state.total_balance)),
        ("Sell cryptocurrency.", bool(state.total_assets)),
        ("Make a deposit.", True),
        ("Make a withdrawal.", bool(state.total_balance)),
        (
            "Reset all data.",
            bool(
                state.favorites
                or state.total_balance
                or state.bought_history
                or state.sold_history
                or state.deposit_history
                or state.withdraw_history
            ),
        ),
        (
            "Transaction History.",
            bool(
                state.bought_history
                or state.sold_history
                or state.deposit_history
                or state.withdraw_history
            ),
        ),
    ]

    print_color("\nWhat would you like to do?", COLOR_YELLOW)

    for option_number, (option_text, condition) in enumerate(menu_options, start=1):
        text_color = COLOR_WHITE if condition else COLOR_DARK_GRAY
        print_color(f"{option_number}. {option_text}", text_color)

    print()  # Add an extra line for better formatting


def press_any_key_to_continue():
    # input(f"{COLOR_YELLOW}Press any key to continue...{COLOR_RESET}")
    ...


def main_menu_loop():
    global state
    while True:
        display_menu(state)
        choice = input(
            f"{COLOR_YELLOW}Select an option (1-13) or press the Ctrl+C to exit the program: {COLOR_RESET}"
        ).strip()

        try:
            choice = int(choice)
            print("Choice after conversion:", choice)

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
                display_deposited_balance()
            elif choice == 6:
                check_total_assets()
                press_any_key_to_continue()
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
                print_color(
                    f"\nYou selected Option {choice}. The program will now exit. Thank you.\n",
                    COLOR_YELLOW,
                )
                break
            else:
                print_color(
                    "Invalid choice. Please select a number between 1 and 13 or press ctrl+C to exit the program.",
                    COLOR_RED,
                )
        except ValueError:
            print_color(
                "Invalid input. Please enter a valid number between 1 and 13.",
                COLOR_RED,
            )


# Main program
if __name__ == "__main__":
    state = ProgramState()
    state.load_state()
    populated_list = state.populated_list

    status = UtilityFunctions.check_service_status()
    credit = UtilityFunctions.check_service_credits()

    online_status = UtilityFunctions.display_status(status)

    print(
        f"\nThe API status is {online_status} and you have {credit} credit(s) remaining.\n"
    )

    # Make the initial API request to get the coins list
    coins_list = UtilityFunctions.check_coins_list()
    state.save_state()

    if not populated_list:
        state.pre_populate_list()

    main_menu_loop()

    # Start the background thread to update the coins list
    coins_thread = threading.Thread(
        target=UtilityFunctions.update_coins_list, args=(coins_list,)
    )
    coins_thread.daemon = (
        True  # This allows the thread to exit when the main program exits
    )
    coins_thread.start()

    coins_list_lock = threading.Lock()
    stop_background_thread = False
