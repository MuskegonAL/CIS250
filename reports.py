import sqlite3
from datetime import datetime, timedelta
import calendar

DB_NAME = "financeManager.db"

def Get_DB_Connection():
    return sqlite3.connect(DB_NAME)

# Generate montly income/expense summary
def Generate_Monthly_Summary(userID, year, month):
    conn = Get_DB_Connection()
    cursor = conn.cursor()
    
    try:
        # Calculate start and end dates for the month
        start_date = f"{year}-{month:02d}-01"
        
        # Get the last day of the month
        _, last_day = calendar.monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day}"
        
        # Get all accounts for this user
        cursor.execute("""
            select ACCOUNT_ID, NAME
            from ACCOUNT
            where USER_ID = ?
        """, (userID,))
        
        accounts = cursor.fetchall()
        if (not accounts):
            print("No accounts found for this user.")
            return
            
        print(f"\n=== Monthly Summary for {calendar.month_name[month]} {year} ===\n")
        
        total_income = 0
        total_expenses = 0
        
        for account_id, account_name in accounts:
            # Get income for this account in the specified month
            cursor.execute("""
                select sum(AMOUNT)
                from TRANSACTIONS
                where ACCOUNT_ID = ?
                  and TRANSACTION_TYPE = 'income'
                  and date(TRANSACTION_DATE) between date(?) and date(?)
            """, (account_id, start_date, end_date))
            
            income = cursor.fetchone()[0] or 0
            total_income += income
            
            # Get expenses for this account in the specified month
            cursor.execute("""
                select sum(AMOUNT)
                from TRANSACTIONS
                where ACCOUNT_ID = ?
                  and TRANSACTION_TYPE = 'expense'
                  and date(TRANSACTION_DATE) between date(?) and date(?)
            """, (account_id, start_date, end_date))
            
            expenses = cursor.fetchone()[0] or 0
            total_expenses += expenses
            
            print(f"Account: {account_name}")
            print(f"  Income:  ${income:.2f}")
            print(f"  Expenses: ${expenses:.2f}")
            print(f"  Net:      ${income - expenses:.2f}")
            print()
            
        print("=== Summary Across All Accounts ===")
        print(f"Total Income:  ${total_income:.2f}")
        print(f"Total Expenses: ${total_expenses:.2f}")
        print(f"Net:            ${total_income - total_expenses:.2f}")
        
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
    except (Exception) as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Generate expense by category for month report
def Generate_Category_Report(userID, year, month):
    conn = Get_DB_Connection()
    cursor = conn.cursor()
    
    try:
        # Calculate start and end dates for the month
        start_date = f"{year}-{month:02d}-01"
        
        # Get the last day of the month
        _, last_day = calendar.monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day}"
        
        print(f"\n=== Expense Categories for {calendar.month_name[month]} {year} ===\n")
        
        # Get expenses grouped by category
        cursor.execute("""
            select 
                c.NAME,
                sum(t.AMOUNT) as TOTAL
            from TRANSACTIONS t
            join CATEGORY c on t.CATEGORY_ID = c.CATEGORY_ID
            join ACCOUNT a on t.ACCOUNT_ID = a.ACCOUNT_ID
            where a.USER_ID = ?
              and t.TRANSACTION_TYPE = 'expense'
              and date(t.TRANSACTION_DATE) between date(?) and date(?)
            group by c.NAME
            order by TOTAL desc
        """, (userID, start_date, end_date))
        
        categories = cursor.fetchall()
        
        if (not categories):
            print("No expenses found for this period.")
            return
            
        total_expenses = 0
        for category, amount in categories:
            total_expenses += amount
            
        # Display each category with amount and percentage
        for category, amount in categories:
            percentage = (amount / total_expenses) * 100
            print(f"{category}: ${amount:.2f} ({percentage:.1f}%)")
            
        print(f"\nTotal Expenses: ${total_expenses:.2f}")
        
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
    except (Exception) as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Generate income by category for specific month
def Generate_Income_Report(userID, year, month):
    conn = Get_DB_Connection()
    cursor = conn.cursor()
    
    try:
        # Calculate start and end dates for the month
        start_date = f"{year}-{month:02d}-01"
        
        # Get the last day of the month
        _, last_day = calendar.monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day}"
        
        print(f"\n=== Income Categories for {calendar.month_name[month]} {year} ===\n")
        
        # Get income grouped by category
        cursor.execute("""
            select 
                c.NAME,
                sum(t.AMOUNT) as TOTAL
            from TRANSACTIONS t
            join CATEGORY c on t.CATEGORY_ID = c.CATEGORY_ID
            join ACCOUNT a on t.ACCOUNT_ID = a.ACCOUNT_ID
            where a.USER_ID = ?
              and t.TRANSACTION_TYPE = 'income'
              and date(t.TRANSACTION_DATE) between date(?) and date(?)
            group by c.NAME
            order by TOTAL desc
        """, (userID, start_date, end_date))
        
        categories = cursor.fetchall()
        
        if (not categories):
            print("No income found for this period.")
            return
            
        total_income = 0
        for category, amount in categories:
            total_income += amount
            
        # Display each category with amount and percentage
        for category, amount in categories:
            percentage = (amount / total_income) * 100
            print(f"{category}: ${amount:.2f} ({percentage:.1f}%)")
            
        print(f"\nTotal Income: ${total_income:.2f}")
        
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
    except (Exception) as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
