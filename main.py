from auth import Register_User, Login_User
from accounts import Create_Account, List_Accounts, Edit_Account, Delete_Account
from categories import Create_Category, List_Categories, Edit_Category, Delete_Category
#from getpass import getpass

def Account_Menu(userID):
    while (True):
        choice = input("\n--- Account Menu ---\n1. List Accounts\n2. Create Account\n3. Edit Account\n4. Delete Account\n5. Back\nChoose: ")
        if (choice == "1"):
            List_Accounts(userID)
        elif (choice == "2"):
            name = input("Account Name: ")
            accountType = input("Account Type: ")
            balance = float(input("Balance: "))
            institution = input("Institution: ")
            Create_Account(userID, name, accountType, balance, institution)
        elif (choice == "3"):
            accountID = int(input("Account ID: "))
            name = input("New Account Name: ")
            accountType = input("New Account Type: ")
            balance = float(input("New Account Balance: "))
            institution = input("New Account Institution: ")
            Edit_Account(accountID, name, accountType, balance, institution)
        elif (choice == "4"):
            accountID = int(input("Account ID: "))
            Delete_Account(accountID)
        elif (choice == "5"):
            break
        else:
            print("Invalid Choice")

def Category_Menu(userID):
    while (True):
        choice = input("\n--- Category Menu ---\n1. List Categories\n2. Create Category\n3. Edit Category\n4. DeleteCategory\n5. Back\nChoose: ")
        if (choice == "1"):
            List_Categories(userID)
        elif (choice == "2"):
            name = input("Category Name: ")
            type = input("Category Type (income/expense): ")
            description = input("Description (Optional): ")
            description = description if description.strip() != "" else None
            parent = input("Parent Category ID (optional): ")
            parentID = int(parent) if parent.strip() != "" else None
            Create_Category(userID, name, type, description, parentID)
        elif (choice == "3"):
            categoryID = int(input("Category ID: "))
            name = input("New Category Name: ")
            type = input("New Category Type (income/expense): ")
            description = input("New Description (Optional): ")
            description = description if description.strip() != "" else None
            parent = input("Parent Category ID (optional): ")
            parentID = int(parent) if parent.strip() != "" else None
            Edit_Category(categoryID, name, type, description, parentID)
        elif (choice == "4"):
            categoryID = int(input("Category ID: "))
            Delete_Category(categoryID)
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
            #password = getpass("Password: ")
            password = input("Password: ")
            userID = Login_User(username, password)
            if (userID):
                print(f"Welcome, {username}!")
                subChoice = input("\n--- Main Menu ---\n1. Account Management\n2. Category Management\n3. Logout\nChoose: ")
                if (subChoice == '1'):
                    Account_Menu(userID)
                elif (subChoice == '2'):
                    Category_Menu(userID)
                elif (subChoice == '3'):
                    break;
                else:
                    print("Invalid Choice")
        elif (choice == '3'):
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()