import sqlite3
import bcrypt

DB_NAME = "financeManager.db"

def Get_DB_Connection():
    return sqlite3.connect(DB_NAME)

def Register_User(username, email, password):
    # Hash Password
    hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = Get_DB_Connection()
        cursor = conn.cursor()
        cursor.execute("""
            insert into USER (USERNAME, EMAIL, PASSWORD_HASH)
                values (?, ?, ?)
        """, (username, email, hashedPassword))
        conn.commit()
        print("User Registered")
    except (sqlite3.IntegrityError):
        print("User already registered")
    finally:
        conn.close()

def Login_User(username, password):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    cursor.execute("""
        select 
                USER_ID
              , PASSWORD_HASH 
            from USER 
            where USERNAME = ?
    """, (username,))
    result = cursor.fetchone()
    conn.close()

    if (result):
        userID, storedHash = result
        if (bcrypt.checkpw(password.encode('utf-8'), storedHash)):
            print(f"Login Successful! Welcome, {username}.")
            return userID
        else:
            print("Incorrect Password")
    else:
        print("Incorrect Username")

    return None
