import sqlite3
from datetime import datetime, timedelta

DB_NAME = "financeManager.db"

def Get_DB_Connection():
    return sqlite3.connect(DB_NAME)

# Add Recurring Transaction
def Add_Recurring_Transaction(accountID, categoryID, amount, frequency, nextDueDateStr, description=None):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        # Validate frequency
        if (frequency.lower() not in ["daily", "weekly", "monthly", "yearly"]):
            print("Invalid frequency. Must be 'daily', 'weekly', 'monthly', or 'yearly'.")
            return

        # Convert date string to datetime object (assuming YYYY-MM-DD format)
        try:
            nextDueDate = datetime.strptime(nextDueDateStr, "%Y-%m-%d").date()
        except (ValueError):
            print("Invalid date format. Please use YYYY-MM-DD.")
            return

        cursor.execute("""
            insert into RECURRING_TRANSACTION (ACCOUNT_ID, CATEGORY_ID, AMOUNT, FREQUENCY, NEXT_DUE_DATE, DESCRIPTION)
                values (?, ?, ?, ?, ?, ?)
        """, (accountID, categoryID, amount, frequency.lower(), nextDueDate, description))
        
        conn.commit()
        print("Recurring Transaction Added Successfully.")

    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
        conn.rollback()
    except (Exception) as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

# List existing Recurring Transactions
def List_Recurring_Transactions(accountID):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            select 
                r.RECURRING_ID,
                r.NEXT_DUE_DATE,
                c.NAME as CATEGORY_NAME,
                r.AMOUNT,
                r.FREQUENCY,
                r.DESCRIPTION
            from RECURRING_TRANSACTION r
            join CATEGORY c on r.CATEGORY_ID = c.CATEGORY_ID
            where r.ACCOUNT_ID = ?
            order by r.NEXT_DUE_DATE
        """, (accountID,))
        recurring = cursor.fetchall()

        if (recurring):
            print(f"\n--- Recurring Transactions for Account ID {accountID} ---")
            for r in recurring:
                print(f"ID: {r[0]}, Next Due: {r[1]}, Category: {r[2]}, Amount: {r[3]:.2f}, Frequency: {r[4]}, Desc: {r[5]}")
        else:
            print("No recurring transactions found for this account.")

    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
    except (Exception) as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Edit a recurring transaction
def Edit_Recurring_Transaction(recurringID, accountID=None, categoryID=None, amount=None, frequency=None, nextDueDateStr=None, description=None):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        # First, check if the recurring transaction exists
        cursor.execute("select RECURRING_ID from RECURRING_TRANSACTION where RECURRING_ID = ?", (recurringID,))
        if not cursor.fetchone():
            print("Recurring transaction not found.")
            return
            
        # Prepare update fields
        update_fields = []
        params = []
        
        if (accountID is not None):
            update_fields.append("ACCOUNT_ID = ?")
            params.append(accountID)
            
        if (categoryID is not None):
            update_fields.append("CATEGORY_ID = ?")
            params.append(categoryID)
            
        if (amount is not None):
            update_fields.append("AMOUNT = ?")
            params.append(amount)
            
        if (frequency is not None):
            if (frequency.lower() not in ["daily", "weekly", "monthly", "yearly"]):
                print("Invalid frequency. Must be 'daily', 'weekly', 'monthly', or 'yearly'.")
                return
            update_fields.append("FREQUENCY = ?")
            params.append(frequency.lower())
            
        if (nextDueDateStr is not None):
            try:
                nextDueDate = datetime.strptime(nextDueDateStr, "%Y-%m-%d").date()
                update_fields.append("NEXT_DUE_DATE = ?")
                params.append(nextDueDate)
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
            
        # Update the recurring transaction
        query = f"update RECURRING_TRANSACTION set {', '.join(update_fields)} where RECURRING_ID = ?"
        params.append(recurringID)
        cursor.execute(query, params)
        
        conn.commit()
        print("Recurring Transaction Updated Successfully.")
        
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
        conn.rollback()
    except (Exception) as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

# Delete Recurring Transaction
def Delete_Recurring_Transaction(recurringID):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        # Check if the recurring transaction exists
        cursor.execute("select RECURRING_ID from RECURRING_TRANSACTION where RECURRING_ID = ?", (recurringID,))
        if (not cursor.fetchone()):
            print("Recurring transaction not found.")
            return
            
        # Delete the recurring transaction
        cursor.execute("delete from RECURRING_TRANSACTION where RECURRING_ID = ?", (recurringID,))
        
        conn.commit()
        print("Recurring Transaction Deleted Successfully.")
        
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
        conn.rollback()
    except (Exception) as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

# Process due recurring transactions
def Process_Due_Recurring_Transactions():
    conn = Get_DB_Connection()
    cursor = conn.cursor()
    today = datetime.now().date()

    try:
        # Get all due recurring transactions
        cursor.execute("""
            select 
                RECURRING_ID,
                ACCOUNT_ID,
                CATEGORY_ID,
                AMOUNT,
                FREQUENCY,
                NEXT_DUE_DATE,
                DESCRIPTION
            from RECURRING_TRANSACTION
            where NEXT_DUE_DATE <= ?
        """, (today,))
        
        due_transactions = cursor.fetchall()
        
        if (not due_transactions):
            print("No recurring transactions due.")
            return
            
        processed_count = 0
        for tx in due_transactions:
            recurring_id, account_id, category_id, amount, frequency, next_due_date, description = tx
            
            # Create actual transaction
            cursor.execute("""
                insert into TRANSACTIONS (
                    ACCOUNT_ID, 
                    CATEGORY_ID, 
                    AMOUNT, 
                    TRANSACTION_TYPE, 
                    TRANSACTION_DATE, 
                    DESCRIPTION,
                    RECURRING_TRANSACTION_ID
                ) values (?, ?, ?, ?, ?, ?, ?)
            """, (account_id, category_id, amount, 'expense', next_due_date, description, recurring_id))
            
            # Update account balance (assuming recurring transactions are expenses)
            cursor.execute("""
                update ACCOUNT 
                    set BALANCE = BALANCE - ? 
                    where ACCOUNT_ID = ?
            """, (amount, account_id))
            
            # Calculate next due date
            next_date = datetime.strptime(str(next_due_date), "%Y-%m-%d").date()
            if (frequency == "daily"):
                next_date += timedelta(days=1)
            elif (frequency == "weekly"):
                next_date += timedelta(weeks=1)
            elif (frequency == "monthly"):
                # Simple approach: add same number of days as in a month
                if (next_date.month == 12):
                    next_date = next_date.replace(year=next_date.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=next_date.month + 1)
            elif (frequency == 'yearly'):
                next_date = next_date.replace(year=next_date.year + 1)
                
            # Update next due date
            cursor.execute("""
                update RECURRING_TRANSACTION
                    set NEXT_DUE_DATE = ?,
                        UPDATED_AT = CURRENT_TIMESTAMP
                    where RECURRING_ID = ?
            """, (next_date, recurring_id))
            
            processed_count += 1
            
        conn.commit()
        print(f"Processed {processed_count} recurring transactions.")
        
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
        conn.rollback()
    except (Exception) as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()
