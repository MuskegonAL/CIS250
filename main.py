from auth import Register_User, Login_User
#from getpass import getpass

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
            Login_User(username, password)
        elif (choice == '3'):
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()