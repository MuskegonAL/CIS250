from auth import Register_User, Login_User
from accounts import Create_Account, List_Accounts, Edit_Account, Delete_Account
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
                Account_Menu(userID)
        elif (choice == '3'):
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()