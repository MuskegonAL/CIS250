import sqlite3

DB_NAME = "financeManager.db"

def Get_DB_Connection():
    return sqlite3.connect(DB_NAME)

def Create_Account(userID, name, accountType, balance, institution):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            insert into ACCOUNT (USER_ID, NAME, ACCOUNT_TYPE, BALANCE, INSTITUTION)
                values (?, ?, ?, ?, ?)
        """, (userID, name, accountType, balance, institution))
        conn.commit()
        print("Account Created")
    except Exception as e:
        print(f"Failed to create account: {e}")
    finally:
        conn.close()

def List_Accounts(userID):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    cursor.execute("""
        select
                ACCOUNT_ID
              , NAME
              , ACCOUNT_TYPE
              , BALANCE
              , INSTITUTION
            from ACCOUNT
            where USER_ID = ?
    """, (userID,))
    accounts = cursor.fetchall()
    conn.close()

    if (accounts):
        print("\nYour Accounts:")
        for account in accounts:
            print(f"ID: {account[0]}, Name: {account[1]}, Type: {account[2]}, Balance: {account[3]}, Institution: {account[4]}")
    else:
        print("No Accounts Found")

def Edit_Account(accountID, name, accountType, balance, institution):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            update ACCOUNT
                set NAME = ?
                  , ACCOUNT_TYPE = ?
                  , BALANCE = ?
                  , INSTITUTION = ?
                  , UPDATED_AT = CURRENT_TIMESTAMP
                where ACCOUNT_ID = ?
        """, (name, accountType, balance, institution, accountID))

        if (cursor.rowcount == 0):
            print("Account not found")
        else:
            conn.commit()
            print("Account Updated")
    except Exception as e:
        print(f"Failed to update account: {e}")
    finally:
        conn.close()

def Delete_Account(accountID):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            delete from ACCOUNT
                where ACCOUNT_ID = ?
        """, (accountID,))
        if (cursor.rowcount == 0):
            print("Account not found")
        else:
            conn.commit()
            print("Account Deleted")
    except Exception as e:
        print(f"Failed to delete account: {e}")
    finally:
        conn.close()