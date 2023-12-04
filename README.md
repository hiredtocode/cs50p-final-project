# CRYPTOCURRENCY PORTFOLIO

#### Video Demo:

#### Description:

    This system is for managing cryptocurrency portfolios, with features for tracking various transactions, viewing real-time data, and maintaining a personalized list of favorite coins. Coded in class-based organization, modular function design, and use of external APIs.

**Libraries and Constants**: Uses time, requests, json, os, and threading. Defines color constants for console output.

**API Configuration**: Connects to the Livecoinwatch API, with endpoints for status, credits, and coin list, and an API key for authentication.

**Program State Management**: ProgramState class manages user state, including favorites, balances, histories, and coin lists. It includes methods for saving and loading state from a JSON file, resetting the state, and pre-populating the coin list.

**Utility Functions**: Contains static methods for service status checks, credit checks, coin list retrieval, and automatic background updates of the coin list.

**User Interaction Functions**: Functions to display the coin list, add/remove favorites, display balance and assets, and calculate profit/loss. Includes options to buy or sell cryptocurrency, make deposits/withdrawals, reset state, and display transaction history.

**Main Menu and Execution Flow**: Presents a menu to the user, handles menu option selection, and maintains the main loop. The main menu offers various actions like viewing coins, managing favorites, handling transactions, and viewing balances and assets.

**Threading for Background Updates**: Utilizes threading to update the coin list in the background every 60 seconds, ensuring the information is up-to-date.

**Initial Setup and Loop**: On program start, it loads the current state, fetches the API status and credit information, initializes the coin list, and enters the main menu loop.

    Available main-menu will be shown in white and disabled menu is in gray. When the criteria meets, the menu will turn white notifiying the user that it's available.

    You should make a deposit first in order to buy the cryptocurrency of your choice and once you purchase a coin that's not manually added to your favorites, it'll automatically add it for you.

    There are still a lot of edge cases that needs to be addressed but I've spent way longer than I've expected and so I'll submit it.

#### Error handling and exceptions includes but not limited to:

1. When menu is grayed out and the user selects it, it should show the right error message and loop back to the main menu.
2. The caclulation and displayed amount should be more accurate and fine-tuned.
3. There should be exceptions and error handling for all options.
