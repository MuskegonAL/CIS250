import sqlite3
from datetime import datetime

DB_NAME = "financeManager.db"

def Get_DB_Connection():
    return sqlite3.connect(DB_NAME)

# Add new Trasnaction
def Add_Transaction(accountID, categoryID, amount, transactionType, transactionDateStr, description=None):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        # Validate transaction type
        if (transactionType.lower() not in ["income", "expense"]):
            print("Invalid transaction type. Must be 'income' or 'expense'.")
            return

        # Convert date string to datetime object
        try:
            transactionDate = datetime.strptime(transactionDateStr, "%Y-%m-%d").date()
        except (ValueError):
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        cursor.execute("""
            insert into TRANSACTIONS (ACCOUNT_ID, CATEGORY_ID, AMOUNT, TRANSACTION_TYPE, TRANSACTION_DATE, DESCRIPTION)
                values (?, ?, ?, ?, ?, ?)
        """, (accountID, categoryID, amount, transactionType.lower(), transactionDate, description))
        
        # Update account balance
        if (transactionType.lower() == "income"):
            cursor.execute("""
                update ACCOUNT 
                    set BALANCE = BALANCE + ? 
                    where ACCOUNT_ID = ?
            """, (amount, accountID))
        elif (transactionType.lower() == "expense"):
             cursor.execute("""
                update ACCOUNT 
                    set BALANCE = BALANCE - ? 
                    where ACCOUNT_ID = ?
            """, (amount, accountID))

        conn.commit()
        print("Transaction Added Successfully and Account Balance Updated.")

    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
        conn.rollback() # Rollback changes if any error occurs
    except (Exception) as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

# List Transactions on an Account
def List_Transactions(accountID):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            select 
                t.TRANSACTION_ID,
                t.TRANSACTION_DATE,
                c.NAME as CATEGORY_NAME,
                t.TRANSACTION_TYPE,
                t.AMOUNT,
                t.DESCRIPTION
            from TRANSACTIONS t
            join CATEGORY c on t.CATEGORY_ID = c.CATEGORY_ID
            where t.ACCOUNT_ID = ?
            order by t.TRANSACTION_DATE desc
        """, (accountID,))
        transactions = cursor.fetchall()

        if (transactions):
            print(f"\n--- Transactions for Account ID {accountID} ---")
            for tx in transactions:
                print(f"ID: {tx[0]}, Date: {tx[1]}, Category: {tx[2]}, Type: {tx[3]}, Amount: {tx[4]:.2f}, Desc: {tx[5]}")
        else:
            print("No transactions found for this account.")

    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
    except (Exception) as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Edit an existing Transaction
def Edit_Transaction(transactionID, accountID=None, categoryID=None, amount=None, transactionType=None, transactionDateStr=None, description=None):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        # First, get the Current Transaction Details
        cursor.execute("""
            select 
                ACCOUNT_ID, 
                AMOUNT, 
                TRANSACTION_TYPE
            from TRANSACTIONS 
            where TRANSACTION_ID = ?
        """, (transactionID,))
        
        current = cursor.fetchone()
        if (not current):
            print("Transaction not found.")
            return
            
        current_account_id, current_amount, current_type = current
        
        # Prepare update fields
        update_fields = []
        params = []
        
        if (accountID is not None):
            update_fields.append("ACCOUNT_ID = ?")
            params.append(accountID)
        else:
            accountID = current_account_id
            
        if (categoryID is not None):
            update_fields.append("CATEGORY_ID = ?")
            params.append(categoryID)
            
        if (amount is not None):
            update_fields.append("AMOUNT = ?")
            params.append(amount)
        else:
            amount = current_amount
            
        if (transactionType is not None):
            if (transactionType.lower() not in ["income", "expense"]):
                print("Invalid transaction type. Must be 'income' or 'expense'.")
                return
            update_fields.append("TRANSACTION_TYPE = ?")
            params.append(transactionType.lower())
        else:
            transactionType = current_type
            
        if (transactionDateStr is not None):
            try:
                transactionDate = datetime.strptime(transactionDateStr, "%Y-%m-%d").date()
                update_fields.append("TRANSACTION_DATE = ?")
                params.append(transactionDate)
            except (ValueError):
                print("Invalid date format. Please use YYYY-MM-DD.")
                return
                
        if (description is not None):
            update_fields.append("DESCRIPTION = ?")
            params.append(description)
            
        update_fields.append("UPDATED_AT = CURRENT_TIMESTAMP")
        
        # If no fields to update, exit
        if (not update_fields):
            print("No fields to update.")
            return
            
        # Update the transaction
        query = f"update TRANSACTIONS set {', '.join(update_fields)} where TRANSACTION_ID = ?"
        params.append(transactionID)
        cursor.execute(query, params)
        
        # Update account balance if necessary
        if (amount != current_amount or 
            transactionType != current_type or 
            accountID != current_account_id):
            
            # Reverse the effect of the old transaction
            if (current_type == "income"):
                cursor.execute("""
                    update ACCOUNT 
                        set BALANCE = BALANCE - ? 
                        where ACCOUNT_ID = ?
                """, (current_amount, current_account_id))
            else:  # expense
                cursor.execute("""
                    update ACCOUNT 
                        set BALANCE = BALANCE + ? 
                        where ACCOUNT_ID = ?
                """, (current_amount, current_account_id))
                
            # Apply the effect of the new transaction
            if (transactionType.lower() == "income"):
                cursor.execute("""
                    update ACCOUNT 
                        set BALANCE = BALANCE + ? 
                        where ACCOUNT_ID = ?
                """, (amount, accountID))
            else:  # expense
                cursor.execute("""
                    update ACCOUNT 
                        set BALANCE = BALANCE - ? 
                        where ACCOUNT_ID = ?
                """, (amount, accountID))
        
        conn.commit()
        print("Transaction Updated Successfully and Account Balance Adjusted.")
        
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
        conn.rollback()
    except (Exception) as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

# Delete a Transaction
def Delete_Transaction(transactionID):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        # First, get the transaction details
        cursor.execute("""
            select 
                ACCOUNT_ID, 
                AMOUNT, 
                TRANSACTION_TYPE
            from TRANSACTIONS 
            where TRANSACTION_ID = ?
        """, (transactionID,))
        
        transaction = cursor.fetchone()
        if (not transaction):
            print("Transaction not found.")
            return
            
        account_id, amount, transaction_type = transaction
        
        # Update the account balance
        if (transaction_type == "income"):
            cursor.execute("""
                update ACCOUNT 
                    set BALANCE = BALANCE - ? 
                    where ACCOUNT_ID = ?
            """, (amount, account_id))
        else:  # expense
            cursor.execute("""
                update ACCOUNT 
                    set BALANCE = BALANCE + ? 
                    where ACCOUNT_ID = ?
            """, (amount, account_id))
            
        # Delete the transaction
        cursor.execute("delete from TRANSACTIONS where TRANSACTION_ID = ?", (transactionID,))
        
        conn.commit()
        print("Transaction Deleted Successfully and Account Balance Adjusted.")
        
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
        conn.rollback()
    except (Exception) as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()
