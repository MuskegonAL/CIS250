from datetime import datetime

from auth import Register_User, Login_User
from accounts import Create_Account, List_Accounts, Edit_Account, Delete_Account
from categories import Create_Category, List_Categories, Edit_Category, Delete_Category
from transactions import Add_Transaction, List_Transactions, Edit_Transaction, Delete_Transaction
#from getpass import getpass

def Account_Menu(userID):
    while True:
        print("\n--- Account Menu ---")
        print("1. List Accounts")
        print("2. Create Account")
        print("3. Edit Account")
        print("4. Delete Account")
        print("5. Back")
        choice = input("Choose: ")
        # List Accounts
        if (choice == "1"):
            List_Accounts(userID)
        # Create Account
        elif (choice == "2"):
            name = input("Account Name: ")
            accountType = input("Account Type: ")
            balance = float(input("Balance: "))
            institution = input("Institution: ")
            Create_Account(userID, name, accountType, balance, institution)
        # Edit Account
        elif (choice == "3"):
            List_Accounts(userID)
            accountID = input("Account ID to Edit: ")
            name = input("New Account Name (leave blank to keep current): ")
            accountType = input("New Account Type (leave blank to keep current): ")
            balance_str = input("New Account Balance (leave blank to keep current): ")
            institution = input("New Account Institution (leave blank to keep current): ")

            # Only pass non-empty values
            kwargs = {}
            if (name): kwargs["name"] = name
            if (accountType): kwargs["accountType"] = accountType
            if (balance_str):
                try:
                    kwargs["balance"] = float(balance_str)
                except (ValueError):
                    print("Invalid balance format. Skipping balance update.")
            if (institution): kwargs["institution"] = institution

            if (kwargs):  # Check if there is anything to update
                Edit_Account(accountID, **kwargs)  # Pass arguments using dictionary unpacking
            else:
                print("No changes specified.")
        # Delete Account
        elif (choice == "4"):
            accountID = int(input("Account ID: "))
            Delete_Account(accountID)
        # Leave
        elif (choice == "5"):
            break
        else:
            print("Invalid Choice")

def Category_Menu(userID):
    while True:
        print("\n--- Category Menu ---")
        print("1. List Categories")
        print("2. Create Category")
        print("3. Edit Category")
        print("4. Delete Category")
        print("5. Back")
        choice = input("Choose: ")
        # List Categories
        if (choice == "1"):
            List_Categories(userID)
        # Create Category
        elif (choice == "2"):
            name = input("Category Name: ")
            type = input("Category Type (income/expense): ")
            description = input("Description (Optional): ")
            description = description if description.strip() != "" else None
            parent = input("Parent Category ID (optional): ")
            parentID = int(parent) if parent.strip() != "" else None
            Create_Category(userID, name, type, description, parentID)
        # Edit Category
        elif (choice == "3"):
            List_Categories(userID)
            categoryID = input("Category ID to Edit: ")
            name = input("New Category Name (leave blank to keep current): ")
            type_str = input("New Category Type (income/expense, leave blank to keep current): ").lower()
            description = input("New Description (Optional, leave blank to keep current): ")
            parent_str = input("New Parent Category ID (optional, leave blank to keep current): ")

            kwargs = {}
            if (name): kwargs["name"] = name
            if (type_str):
                if (type_str in ["income", "expense"]):
                    kwargs["categoryType"] = type_str
                else:
                    print("Invalid type specified. Skipping type update.")
            if (description): kwargs["description"] = description
            if (parent_str):
                try:
                    kwargs["parentCategoryID"] = int(parent_str)
                except (ValueError):
                    print("Invalid Parent ID format. Skipping parent ID update.")
            elif (parent_str) == "":  # Allow setting parent to None
                kwargs["parentCategoryID"] = None

            if (kwargs):  # Check if there is anything to update
                Edit_Category(categoryID, **kwargs)
            else:
                print("No changes specified.")
        # Delete Category
        elif (choice == "4"):
            categoryID = int(input("Category ID: "))
            Delete_Category(categoryID)
        # Leave
        elif (choice == "5"):
            break
        else:
            print("Invalid Choice")


def Transaction_Menu(userID):
    List_Accounts(userID)  # Show accounts first
    accountID = input("Enter Account ID to manage transactions for: ")
    while (True):
        print(f"\n--- Transaction Menu (Account ID: {accountID}) ---")
        print("1. List Transactions")
        print("2. Add Transaction")
        print("3. Edit Transaction")
        print("4. Delete Transaction")
        print("5. Back to Main Menu")
        choice = input("Choose: ")

        # List Transactions
        if (choice == "1"):
            List_Transactions(accountID)
        # Add Transaction
        elif (choice == "2"):
            List_Categories(userID)  # Show categories to help user choose ID
            categoryID = input("Category ID: ")
            amount = input("Amount: ")
            type = input("Transaction Type (income/expense): ").lower()
            while (type not in ["income", "expense"]):
                print("Invalid type. Must be 'income' or 'expense'.")
                type = input("Transaction Type (income/expense): ").lower()
            dateStr = input("Transaction Date (YYYY-MM-DD): ")
            description = input("Description (Optional): ")
            Add_Transaction(accountID, categoryID, amount, type, dateStr, description if description else None)
        # Edit Transaction
        elif (choice == "3"):
            List_Transactions(accountID)  # Show transactions to help user choose ID
            transactionID = input("Transaction ID to Edit: ")
            print("Enter new details (leave blank to keep current value):")

            new_account_str = input(f"New Account ID (current account is {accountID}): ")
            new_category_str = input("New Category ID: ")
            new_amount_str = input("New Amount: ")
            new_type = input("New Transaction Type (income/expense): ").lower()
            new_dateStr = input("New Transaction Date (YYYY-MM-DD): ")
            new_description = input("New Description: ")

            # Try check with keyword arguments? TODO: Modify others using this method
            kwargs = {}
            if (new_account_str):
                try:
                    kwargs["accountID"] = int(new_account_str)
                except (ValueError):
                    print("Invalid Account ID format. Skipping.")
            if (new_category_str):
                try:
                    kwargs["categoryID"] = int(new_category_str)
                except (ValueError):
                    print("Invalid Category ID format. Skipping.")
            if (new_amount_str):
                try:
                    kwargs["amount"] = float(new_amount_str)
                except (ValueError):
                    print("Invalid Amount format. Skipping.")
            if (new_type):
                if (new_type in ["income", "expense"]):
                    kwargs["transactionType"] = new_type
                else:
                    print("Invalid type specified. Skipping type update.")
            if (new_dateStr):
                try:
                    datetime.strptime(new_dateStr, "%Y-%m-%d")
                    kwargs["transactionDateStr"] = new_dateStr
                except (ValueError):
                    print("Invalid Date format. Skipping.")
            if (new_description): kwargs["description"] = new_description

            # If any keywords passed, THEN call function
            if (kwargs):
                Edit_Transaction(transactionID, **kwargs)
            else:
                print("No changes specified.")
        # List Transactions
        elif (choice == "4"):
            List_Transactions(accountID)  # Show transactions to help user choose ID
            transactionID = input("Transaction ID to Delete: ")
            confirm = input(
                f"Are you sure you want to delete transaction {transactionID}? This will adjust account balance. (yes/no): ")
            if (confirm.lower() == "yes"):
                Delete_Transaction(transactionID)
            else:
                print("Deletion cancelled.")
        # Leave
        elif (choice == "5"):
            break
        else:
            print("Invalid Choice")

def main():
    while (True):
        choice = input("\n1. Register\n2. Login\n3. Exit\nChoose an option: ")
        if (choice == '1'):
            username = input("Username: ")
            email = input("Email: ")
            #password = getpass("Password: ")
            password = input("Password: ")
            Register_User(username, email, password)
        elif (choice == '2'):
            username = input("Username: ")
            password = input("Password: ")  # TODO: Get Pass?
            userID = Login_User(username, password)

            if (userID):
                print(f"\nWelcome, {username}!")

                while True:  # Logged in menu loop
                    print("\n--- Main Menu ---")
                    print("1. Account Management")
                    print("2. Category Management")
                    print("3. Transaction Management")
                    print("4. Logout")
                    subChoice = input("Choose: ")

                    if (subChoice == "1"):
                        Account_Menu(userID)
                    elif (subChoice == "2"):
                        Category_Menu(userID)
                    elif (subChoice == "3"):
                        Transaction_Menu(userID)
                    elif (subChoice == "4"):
                        print("Logging out.")
                        break
                    else:
                        print("Invalid Choice")
        elif (choice == '3'):
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()