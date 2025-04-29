import unittest
import sqlite3
import os
import bcrypt
from datetime import date, datetime, timedelta
import calendar
import unittest.mock

# Test database
TEST_DB_NAME = "test_financeManager.db"

import accounts
import categories
import transactions
import recurring
import reports
import auth

accounts.DB_NAME = TEST_DB_NAME
categories.DB_NAME = TEST_DB_NAME
transactions.DB_NAME = TEST_DB_NAME
recurring.DB_NAME = TEST_DB_NAME
reports.DB_NAME = TEST_DB_NAME
auth.DB_NAME = TEST_DB_NAME

from initDB import initialize_database

# Run queries against test database
def run_db_query(query, params=(), fetch_one=False):
    conn = sqlite3.connect(TEST_DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if (fetch_one):
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    return result

# Class for testing user authentication
class TestAuth(unittest.TestCase):

    # Create test database schema
    @classmethod
    def setUpClass(cls):
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)
        initialize_database(db_name=TEST_DB_NAME)

    # Delete test database
    @classmethod
    def tearDownClass(cls):
        if (os.path.exists(TEST_DB_NAME)):
            os.remove(TEST_DB_NAME)

    # Clean user table
    def setUp(self):
        run_db_query("delete from USER")

    # Register a new user
    def test_AUTH_01_register_new_user(self):
        auth.Register_User("testuser", "test@test.com", "password")
        user = run_db_query("select USERNAME, EMAIL from USER where USERNAME = ?", ("testuser",), fetch_one=True)
        self.assertIsNotNone(user)
        self.assertEqual(user[0], "testuser")
        self.assertEqual(user[1], "test@test.com")

        # Verify password hash
        stored_hash = run_db_query("select PASSWORD_HASH from USER where USERNAME = ?", ("testuser",), fetch_one=True)[0]
        self.assertTrue(bcrypt.checkpw("password".encode('utf-8'), stored_hash))

    # Register a duplicate user
    def test_AUTH_02_register_duplicate_user(self):
        auth.Register_User("testuser", "test@test.com", "password")

        # Check no new user was added
        auth.Register_User("testuser", "another@test.com", "newpass")
        count = run_db_query("select count(*) from USER where USERNAME = ?", ("testuser",), fetch_one=True)[0]
        self.assertEqual(count, 1)

    # Login with correct credentials
    def test_AUTH_03_login_correct_credentials(self):
        auth.Register_User("testuser", "test@test.com", "password")
        user_id = auth.Login_User("testuser", "password")
        self.assertIsNotNone(user_id)
        self.assertIsInstance(user_id, int)

    # Login with incorrect password
    def test_AUTH_04_login_incorrect_password(self):
        auth.Register_User("testuser", "test@test.com", "password")
        user_id = auth.Login_User("testuser", "wrongpassword")
        self.assertIsNone(user_id)

    # Login with invalid user
    def test_AUTH_05_login_non_existent_user(self):
        user_id = auth.Login_User("nouser", "password")
        self.assertIsNone(user_id)


# Class for setting up test cases
class TestAccountsCategoriesBase(unittest.TestCase):

    TEST_USER_ID = None
    TEST_USERNAME = "baseuser"
    TEST_EMAIL = "base@test.com"
    TEST_PASSWORD = "password"

    # Create schema
    @classmethod
    def setUpClass(cls):
        """Create schema using initDB and a base user."""
        if (os.path.exists(TEST_DB_NAME)):
            os.remove(TEST_DB_NAME)

        initialize_database(db_name=TEST_DB_NAME)

        # Register the base user
        auth.Register_User(cls.TEST_USERNAME, cls.TEST_EMAIL, cls.TEST_PASSWORD)
        cls.TEST_USER_ID = auth.Login_User(cls.TEST_USERNAME, cls.TEST_PASSWORD)
        if (cls.TEST_USER_ID is None):
             raise Exception("Failed to create base user for tests")

    # Remove test database
    @classmethod
    def tearDownClass(cls):
        if os.path.exists(TEST_DB_NAME):
            os.remove(TEST_DB_NAME)

    # Cleanup relevant tables
    def setUp(self):
        run_db_query("delete from TRANSACTIONS where ACCOUNT_ID in (select ACCOUNT_ID from ACCOUNT where USER_ID = ?)", (self.TEST_USER_ID,))
        run_db_query("delete from RECURRING_TRANSACTION where ACCOUNT_ID in (select ACCOUNT_ID from ACCOUNT where USER_ID = ?)", (self.TEST_USER_ID,))
        run_db_query("delete from BUDGET where ACCOUNT_ID in (select ACCOUNT_ID from ACCOUNT where USER_ID = ?)", (self.TEST_USER_ID,))
        run_db_query("delete from CATEGORY where USER_ID = ?", (self.TEST_USER_ID,))
        run_db_query("delete from ACCOUNT where USER_ID = ?", (self.TEST_USER_ID,))

# Class for testing accounts
class TestAccounts(TestAccountsCategoriesBase):

    # Create account test
    def test_ACC_02_create_account(self):
        accounts.Create_Account(self.TEST_USER_ID, "Savings", "Checking", 1000.0, "Bank A")
        acc = run_db_query("select NAME, ACCOUNT_TYPE, BALANCE, INSTITUTION from ACCOUNT where USER_ID = ? AND NAME = ?",
                           (self.TEST_USER_ID, "Savings"), fetch_one=True)
        self.assertIsNotNone(acc)
        self.assertEqual(acc[0], "Savings")
        self.assertEqual(acc[1], "Checking")
        self.assertAlmostEqual(acc[2], 1000.0)
        self.assertEqual(acc[3], "Bank A")

    # List non-existing accounts
    def test_ACC_01_list_accounts_empty(self):
        acc_list = run_db_query("select 1 from ACCOUNT where USER_ID = ?", (self.TEST_USER_ID,))
        self.assertEqual(len(acc_list), 0)

    # List existing accounts
    def test_ACC_03_list_accounts_existing(self):
        accounts.Create_Account(self.TEST_USER_ID, "Savings", "Checking", 1000.0, "Bank A")
        accounts.Create_Account(self.TEST_USER_ID, "Credit", "Card", -50.0, "Bank B")
        acc_list = run_db_query("select NAME from ACCOUNT where USER_ID = ?", (self.TEST_USER_ID,))
        self.assertEqual(len(acc_list), 2)
        self.assertIn(('Savings',), acc_list)
        self.assertIn(('Credit',), acc_list)

    # Edit an account
    def test_ACC_04_edit_account(self):
        accounts.Create_Account(self.TEST_USER_ID, "Savings", "Checking", 1000.0, "Bank A")
        acc_id = run_db_query("select ACCOUNT_ID from ACCOUNT where NAME = ?", ("Savings",), fetch_one=True)[0]

        accounts.Edit_Account(acc_id, "Everyday", "Checking", 1200.50, "Bank B")
        acc = run_db_query("select NAME, ACCOUNT_TYPE, BALANCE, INSTITUTION from ACCOUNT where ACCOUNT_ID = ?",
                           (acc_id,), fetch_one=True)
        self.assertEqual(acc[0], "Everyday")
        self.assertEqual(acc[1], "Checking")
        self.assertAlmostEqual(acc[2], 1200.50)
        self.assertEqual(acc[3], "Bank B")

    # Edit a non-existant account
    def test_ACC_07_edit_non_existent_account(self):
        accounts.Edit_Account(999, "No Account", "N/A", 0, "N/A")
        acc = run_db_query("select 1 from ACCOUNT where ACCOUNT_ID = ?", (999,))
        self.assertEqual(len(acc), 0)

    # Delete an account
    def test_ACC_08_delete_account(self):
        accounts.Create_Account(self.TEST_USER_ID, "ToDelete", "Temp", 10.0, "Bank C")
        acc_id = run_db_query("select ACCOUNT_ID from ACCOUNT where NAME = ?", ("ToDelete",), fetch_one=True)[0]
        accounts.Delete_Account(acc_id)
        acc = run_db_query("select 1 from ACCOUNT where ACCOUNT_ID = ?", (acc_id,))
        self.assertEqual(len(acc), 0)

    # Delete a non-existant account
    def test_ACC_09_delete_non_existent_account(self):
        accounts.Delete_Account(999)
        # Just ensure no crash

# Test categories class
class TestCategories(TestAccountsCategoriesBase):

    # Create parent income category
    def test_CAT_02_create_toplevel_income(self):
        categories.Create_Category(self.TEST_USER_ID, "Salary", "income", "Monthly Pay")
        cat = run_db_query("select NAME, TYPE, DESCRIPTION, PARENT_CATEGORY_ID from CATEGORY where NAME = ?",
                           ("Salary",), fetch_one=True)
        self.assertIsNotNone(cat)
        self.assertEqual(cat[0], "Salary")
        self.assertEqual(cat[1], "income")
        self.assertEqual(cat[2], "Monthly Pay")
        self.assertIsNone(cat[3])

    # Create parent expense category
    def test_CAT_03_create_toplevel_expense(self):
        categories.Create_Category(self.TEST_USER_ID, "Groceries", "expense")
        cat = run_db_query("select NAME, TYPE from CATEGORY where NAME = ?", ("Groceries",), fetch_one=True)
        self.assertEqual(cat[0], "Groceries")
        self.assertEqual(cat[1], "expense")

    # Create subcategory
    def test_CAT_04_create_subcategory(self):
        categories.Create_Category(self.TEST_USER_ID, "Groceries", "expense")
        parent_id = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Groceries",), fetch_one=True)[0]
        categories.Create_Category(self.TEST_USER_ID, "Snacks", "expense", parentCategoryID=parent_id)
        cat = run_db_query("select NAME, PARENT_CATEGORY_ID from CATEGORY where NAME = ?", ("Snacks",), fetch_one=True)
        self.assertEqual(cat[0], "Snacks")
        self.assertEqual(cat[1], parent_id)

    # Create invalid type of category
    def test_CAT_05_create_invalid_type(self):
        # Expecting CHECK constraint violation
        with self.assertRaises(sqlite3.IntegrityError):
             conn = sqlite3.connect(TEST_DB_NAME)
             cursor = conn.cursor()
             cursor.execute("""
                 insert into CATEGORY (USER_ID, NAME, TYPE) values (?, ?, ?)
             """, (self.TEST_USER_ID, "Misc", "other"))
             conn.commit()
             conn.close()
        # Verify category was not added
        cat = run_db_query("select 1 from CATEGORY where NAME = ?", ("Misc",))
        self.assertEqual(len(cat), 0)

    # Edit a cateogry
    def test_CAT_07_edit_category(self):
        categories.Create_Category(self.TEST_USER_ID, "Groceries", "expense")
        cat_id = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Groceries",), fetch_one=True)[0]
        categories.Edit_Category(cat_id, "Food", "expense", "All food items", None)
        cat = run_db_query("select NAME, TYPE, DESCRIPTION, PARENT_CATEGORY_ID from CATEGORY where CATEGORY_ID = ?",
                           (cat_id,), fetch_one=True)
        self.assertEqual(cat[0], "Food")
        self.assertEqual(cat[1], "expense")
        self.assertEqual(cat[2], "All food items")
        self.assertIsNone(cat[3])

    # Delete a category with no transactions
    def test_CAT_10_delete_category_no_transactions(self):
        categories.Create_Category(self.TEST_USER_ID, "Unused", "expense")
        cat_id = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Unused",), fetch_one=True)[0]
        categories.Delete_Category(cat_id)
        cat = run_db_query("select 1 from CATEGORY where CATEGORY_ID = ?", (cat_id,))
        self.assertEqual(len(cat), 0)

    # Delete a category with transactions
    def test_CAT_11_delete_category_with_transactions(self):
        accounts.Create_Account(self.TEST_USER_ID, "TestAcc", "Checking", 100.0, "TestBank")
        acc_id = run_db_query("select ACCOUNT_ID from ACCOUNT where NAME = ?", ("TestAcc",), fetch_one=True)[0]
        categories.Create_Category(self.TEST_USER_ID, "UsedCat", "expense")
        cat_id = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("UsedCat",), fetch_one=True)[0]
        # Add transaction using the category
        transactions.Add_Transaction(acc_id, cat_id, 5.0, "expense", "2023-01-15")
        # Attempt delete - function should print and return without deleting
        categories.Delete_Category(cat_id)
        # Verify category still exists
        cat = run_db_query("select 1 from CATEGORY where CATEGORY_ID = ?", (cat_id,))
        self.assertEqual(len(cat), 1)


# Test transactions
class TestTransactions(TestAccountsCategoriesBase):

    # Function to create accounts and categories for tests
    def setUp(self):
        super().setUp()
        # Create account
        accounts.Create_Account(self.TEST_USER_ID, "Checking", "Debit", 1000.00, "Test Bank")
        self.acc_id = run_db_query("select ACCOUNT_ID from ACCOUNT where NAME = ?", ("Checking",), fetch_one=True)[0]
        # Create categories
        categories.Create_Category(self.TEST_USER_ID, "Salary", "income")
        self.income_cat_id = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Salary",), fetch_one=True)[0]
        categories.Create_Category(self.TEST_USER_ID, "Food", "expense")
        self.expense_cat_id = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Food",), fetch_one=True)[0]

    # Add an income transaction
    def test_TXN_01_add_income(self):
        initial_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        amount = 2000.50
        transactions.Add_Transaction(self.acc_id, self.income_cat_id, amount, "income", "2023-10-26", "Paycheck")
        # Verify transaction
        txn = run_db_query("select AMOUNT, TRANSACTION_TYPE, DESCRIPTION from TRANSACTIONS where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)
        self.assertIsNotNone(txn)
        self.assertAlmostEqual(txn[0], amount)
        self.assertEqual(txn[1], "income")
        self.assertEqual(txn[2], "Paycheck")
        # Verify balance update
        final_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        self.assertAlmostEqual(final_balance, initial_balance + amount)

    # Add an expense transaction
    def test_TXN_03_add_expense(self):
        initial_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        amount = 75.50
        transactions.Add_Transaction(self.acc_id, self.expense_cat_id, amount, "expense", "2023-10-27", "Lunch")
         # Verify transaction
        txn = run_db_query("select AMOUNT, TRANSACTION_TYPE, DESCRIPTION from TRANSACTIONS where ACCOUNT_ID = ? AND CATEGORY_ID = ?", (self.acc_id, self.expense_cat_id), fetch_one=True)
        self.assertIsNotNone(txn)
        self.assertAlmostEqual(txn[0], amount)
        self.assertEqual(txn[1], "expense")
        self.assertEqual(txn[2], "Lunch")
        # Verify balance update
        final_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        self.assertAlmostEqual(final_balance, initial_balance - amount)

    # Add transaction with an invalid date
    def test_TXN_05_add_invalid_date(self):
        initial_count = run_db_query("select count(*) from TRANSACTIONS", fetch_one=True)[0]
        initial_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        transactions.Add_Transaction(self.acc_id, self.expense_cat_id, 10.0, "expense", "invalid-date")
        final_count = run_db_query("select count(*) from TRANSACTIONS", fetch_one=True)[0]
        final_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        self.assertEqual(initial_count, final_count)
        self.assertAlmostEqual(initial_balance, final_balance)

    # Add an invalid transaction type
    def test_TXN_06_add_invalid_type(self):
        initial_count = run_db_query("select count(*) from TRANSACTIONS", fetch_one=True)[0]
        initial_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        transactions.Add_Transaction(self.acc_id, self.expense_cat_id, 10.0, "transfer", "2023-10-28")
        final_count = run_db_query("select count(*) from TRANSACTIONS", fetch_one=True)[0]
        final_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        self.assertEqual(initial_count, final_count)
        self.assertAlmostEqual(initial_balance, final_balance)

    # Edit a transaction's amount
    def test_TXN_08_edit_transaction_amount_type(self):
        amount = 75.50
        transactions.Add_Transaction(self.acc_id, self.expense_cat_id, amount, "expense", "2023-10-27", "Lunch")
        txn_id = run_db_query("select TRANSACTION_ID from TRANSACTIONS where DESCRIPTION = ?", ("Lunch",), fetch_one=True)[0]
        initial_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0] # Should be 1000 - 75.50 = 924.50

        new_amount = 80.00
        transactions.Edit_Transaction(txn_id, amount=new_amount, transactionType="income")

        # Verify transaction update
        txn = run_db_query("select AMOUNT, TRANSACTION_TYPE from TRANSACTIONS where TRANSACTION_ID = ?", (txn_id,), fetch_one=True)
        self.assertAlmostEqual(txn[0], new_amount)
        self.assertEqual(txn[1], "income")

        # Verify balance adjustment
        # Old removed: +75.50, New added: +80.00. Net change: +155.50
        final_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        self.assertAlmostEqual(final_balance, initial_balance + amount + new_amount)

    # Edit a transaction's account
    def test_TXN_10_edit_transaction_change_account(self):
        # Add another account
        accounts.Create_Account(self.TEST_USER_ID, "Savings", "Savings", 500.00, "Test Bank")
        acc2_id = run_db_query("select ACCOUNT_ID from ACCOUNT where NAME = ?", ("Savings",), fetch_one=True)[0]

        # Add income transaction to first account
        amount = 2000.00
        transactions.Add_Transaction(self.acc_id, self.income_cat_id, amount, "income", "2023-10-26", "Paycheck")
        txn_id = run_db_query("select TRANSACTION_ID from TRANSACTIONS where DESCRIPTION = ?", ("Paycheck",), fetch_one=True)[0]

        initial_bal1 = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0] # 1000 + 2000 = 3000
        initial_bal2 = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (acc2_id,), fetch_one=True)[0] # 500

        # Edit transaction to move to second account
        transactions.Edit_Transaction(txn_id, accountID=acc2_id)

        # Verify transaction update
        txn_acc = run_db_query("select ACCOUNT_ID from TRANSACTIONS where TRANSACTION_ID = ?", (txn_id,), fetch_one=True)[0]
        self.assertEqual(txn_acc, acc2_id)

        # Verify balance adjustments
        final_bal1 = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        final_bal2 = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (acc2_id,), fetch_one=True)[0]
        self.assertAlmostEqual(final_bal1, initial_bal1 - amount) # 3000 - 2000 = 1000
        self.assertAlmostEqual(final_bal2, initial_bal2 + amount) # 500 + 2000 = 2500

    # Delete a transaction
    def test_TXN_12_delete_transaction(self):
        amount = 75.50
        transactions.Add_Transaction(self.acc_id, self.expense_cat_id, amount, "expense", "2023-10-27", "Lunch")
        txn_id = run_db_query("select TRANSACTION_ID from TRANSACTIONS where DESCRIPTION = ?", ("Lunch",), fetch_one=True)[0]
        initial_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0] # 1000 - 75.50 = 924.50

        transactions.Delete_Transaction(txn_id)

        # Verify transaction deleted
        txn = run_db_query("select 1 from TRANSACTIONS where TRANSACTION_ID = ?", (txn_id,))
        self.assertEqual(len(txn), 0)

        # Verify balance adjustment (expense removed, so balance increases)
        final_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
        self.assertAlmostEqual(final_balance, initial_balance + amount) # 924.50 + 75.50 = 1000.00

# Test recurring transactions class
class TestRecurring(TestAccountsCategoriesBase):

     # Setup account and category
     def setUp(self):
        super().setUp()
        accounts.Create_Account(self.TEST_USER_ID, "Checking", "Debit", 5000.00, "Test Bank")
        self.acc_id = run_db_query("select ACCOUNT_ID from ACCOUNT where NAME = ?", ("Checking",), fetch_one=True)[0]
        categories.Create_Category(self.TEST_USER_ID, "Rent", "expense")
        self.cat_id = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Rent",), fetch_one=True)[0]

     # Add a recurring transaction
     def test_REC_01_add_recurring(self):
         next_due = "2023-11-01"
         recurring.Add_Recurring_Transaction(self.acc_id, self.cat_id, 1200.00, "monthly", next_due, "Monthly Rent")
         rec = run_db_query("select AMOUNT, FREQUENCY, NEXT_DUE_DATE, DESCRIPTION from RECURRING_TRANSACTION where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)
         self.assertIsNotNone(rec)
         self.assertAlmostEqual(rec[0], 1200.00)
         self.assertEqual(rec[1], "monthly")
         self.assertEqual(rec[2], next_due)
         self.assertEqual(rec[3], "Monthly Rent")

     # Edit a recurring transaction
     def test_REC_04_edit_recurring(self):
         recurring.Add_Recurring_Transaction(self.acc_id, self.cat_id, 1200.00, "monthly", "2023-11-01", "Monthly Rent")
         rec_id = run_db_query("select RECURRING_ID from RECURRING_TRANSACTION where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
         new_amount = 1250.00
         new_due = "2023-12-01"
         recurring.Edit_Recurring_Transaction(rec_id, amount=new_amount, nextDueDateStr=new_due)
         rec = run_db_query("select AMOUNT, NEXT_DUE_DATE from RECURRING_TRANSACTION where RECURRING_ID = ?", (rec_id,), fetch_one=True)
         self.assertAlmostEqual(rec[0], new_amount)
         self.assertEqual(rec[1], new_due)

     # Process a due transaction using a mock datetime
     @unittest.mock.patch('recurring.datetime')
     def test_REC_07_process_due_transaction(self, mock_datetime):
         initial_balance = 5000.00
         amount_due = 1200.00
         due_date_str = "2023-11-01"
         due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d").date()

         # Mock 'today' to be on or after the due date
         mock_datetime.now.return_value.date.return_value = due_date_obj
         mock_datetime.strptime = datetime.strptime

         recurring.Add_Recurring_Transaction(self.acc_id, self.cat_id, amount_due, "monthly", due_date_str, "Monthly Rent")
         rec_id = run_db_query("select RECURRING_ID from RECURRING_TRANSACTION where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]

         recurring.Process_Due_Recurring_Transactions()

         # 1. Check new transaction created
         txn = run_db_query("select AMOUNT, TRANSACTION_DATE, RECURRING_TRANSACTION_ID from TRANSACTIONS where RECURRING_TRANSACTION_ID = ?", (rec_id,), fetch_one=True)
         self.assertIsNotNone(txn)
         self.assertAlmostEqual(txn[0], amount_due)
         self.assertEqual(txn[1], due_date_str)
         self.assertEqual(txn[2], rec_id)

         # 2. Check account balance updated
         final_balance = run_db_query("select BALANCE from ACCOUNT where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
         self.assertAlmostEqual(final_balance, initial_balance - amount_due)

         # 3. Check recurring transaction next due date updated
         next_due_db = run_db_query("select NEXT_DUE_DATE from RECURRING_TRANSACTION where RECURRING_ID = ?", (rec_id,), fetch_one=True)[0]
         expected_next_due = "2023-12-01"
         self.assertEqual(next_due_db, expected_next_due)

     # Ensure no trasnaction is due
     @unittest.mock.patch('recurring.datetime')
     def test_REC_06_process_no_transactions_due(self, mock_datetime):
        amount_due = 100.00
        future_due_date_str = "2024-01-01"
        today_date_obj = date(2023, 11, 15)

        mock_datetime.now.return_value.date.return_value = today_date_obj
        mock_datetime.strptime = datetime.strptime

        recurring.Add_Recurring_Transaction(self.acc_id, self.cat_id, amount_due, "yearly", future_due_date_str, "Annual Fee")
        initial_txn_count = run_db_query("select count(*) from TRANSACTIONS", fetch_one=True)[0]

        recurring.Process_Due_Recurring_Transactions()

        # 1. No new transaction created
        final_txn_count = run_db_query("select count(*) from TRANSACTIONS", fetch_one=True)[0]
        self.assertEqual(initial_txn_count, final_txn_count)

        # 2. Recurring date unchanged
        rec_date = run_db_query("select NEXT_DUE_DATE from RECURRING_TRANSACTION where ACCOUNT_ID=?", (self.acc_id,), fetch_one=True)[0]
        self.assertEqual(rec_date, future_due_date_str)

     # Delete a recurring transaction
     def test_REC_09_delete_recurring(self):
         recurring.Add_Recurring_Transaction(self.acc_id, self.cat_id, 1200.00, "monthly", "2023-11-01", "Monthly Rent")
         rec_id = run_db_query("select RECURRING_ID from RECURRING_TRANSACTION where ACCOUNT_ID = ?", (self.acc_id,), fetch_one=True)[0]
         recurring.Delete_Recurring_Transaction(rec_id)
         rec = run_db_query("select 1 from RECURRING_TRANSACTION where RECURRING_ID = ?", (rec_id,))
         self.assertEqual(len(rec), 0)

# Test reports class
class TestReports(TestAccountsCategoriesBase):

    # Setup data for reports
    def setUp(self):
        super().setUp()
        # Accounts
        accounts.Create_Account(self.TEST_USER_ID, "Checking", "Debit", 1000.00, "Bank A")
        self.acc1_id = run_db_query("select ACCOUNT_ID from ACCOUNT where NAME = ?", ("Checking",), fetch_one=True)[0]
        accounts.Create_Account(self.TEST_USER_ID, "Savings", "Savings", 5000.00, "Bank B")
        self.acc2_id = run_db_query("select ACCOUNT_ID from ACCOUNT where NAME = ?", ("Savings",), fetch_one=True)[0]

        # Categories
        categories.Create_Category(self.TEST_USER_ID, "Salary", "income")
        self.cat_income1 = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Salary",), fetch_one=True)[0]
        categories.Create_Category(self.TEST_USER_ID, "Freelance", "income")
        self.cat_income2 = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Freelance",), fetch_one=True)[0]
        categories.Create_Category(self.TEST_USER_ID, "Groceries", "expense")
        self.cat_expense1 = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Groceries",), fetch_one=True)[0]
        categories.Create_Category(self.TEST_USER_ID, "Utilities", "expense")
        self.cat_expense2 = run_db_query("select CATEGORY_ID from CATEGORY where NAME = ?", ("Utilities",), fetch_one=True)[0]

        # Transactions (October 2023)
        transactions.Add_Transaction(self.acc1_id, self.cat_income1, 2500.00, "income", "2023-10-05") # Bal: 3500
        transactions.Add_Transaction(self.acc1_id, self.cat_expense1, 150.50, "expense", "2023-10-10") # Bal: 3349.50
        transactions.Add_Transaction(self.acc1_id, self.cat_expense2, 85.00, "expense", "2023-10-15") # Bal: 3264.50
        transactions.Add_Transaction(self.acc2_id, self.cat_income2, 300.00, "income", "2023-10-20") # Bal: 5300
        transactions.Add_Transaction(self.acc1_id, self.cat_expense1, 60.00, "expense", "2023-10-25") # Bal: 3204.50

        # Transactions (November 2023)
        transactions.Add_Transaction(self.acc1_id, self.cat_income1, 2500.00, "income", "2023-11-05")

    # Ensure monthly summary data exists
    def test_REP_01_monthly_summary_data_exists(self):
         year, month = 2023, 10
         start_date = f"{year}-{month:02d}-01"
         _, last_day = calendar.monthrange(year, month)
         end_date = f"{year}-{month:02d}-{last_day}"

         # Expected values for Oct 2023
         expected_total_income = 2500.00 + 300.00
         expected_total_expense = 150.50 + 85.00 + 60.00

         # Query for total income
         db_income = run_db_query("""
             select sum(t.AMOUNT) from TRANSACTIONS t
             join ACCOUNT a on t.ACCOUNT_ID = a.ACCOUNT_ID
             where a.USER_ID = ? and t.TRANSACTION_TYPE = 'income'
             and date(t.TRANSACTION_DATE) between date(?) and date(?)
         """, (self.TEST_USER_ID, start_date, end_date), fetch_one=True)[0]

         # Query for total expense
         db_expense = run_db_query("""
             select sum(t.AMOUNT) from TRANSACTIONS t
             join ACCOUNT a on t.ACCOUNT_ID = a.ACCOUNT_ID
             where a.USER_ID = ? and t.TRANSACTION_TYPE = 'expense'
             and date(t.TRANSACTION_DATE) between date(?) and date(?)
         """, (self.TEST_USER_ID, start_date, end_date), fetch_one=True)[0]

         self.assertAlmostEqual(db_income, expected_total_income)
         self.assertAlmostEqual(db_expense, expected_total_expense)

    # Ensure no monthly summary data
    def test_REP_02_monthly_summary_no_data(self):
        year, month = 2023, 12
        start_date = f"{year}-{month:02d}-01"
        _, last_day = calendar.monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day}"

        # Query for total income
        income_result = run_db_query("""
            select sum(t.AMOUNT) from TRANSACTIONS t
            join ACCOUNT a on t.ACCOUNT_ID = a.ACCOUNT_ID
            where a.USER_ID = ? and t.TRANSACTION_TYPE = 'income'
            and date(t.TRANSACTION_DATE) between date(?) and date(?)
        """, (self.TEST_USER_ID, start_date, end_date), fetch_one=True)

        # Query for total expense
        expense_result = run_db_query("""
            select sum(t.AMOUNT) from TRANSACTIONS t
            join ACCOUNT a on t.ACCOUNT_ID = a.ACCOUNT_ID
            where a.USER_ID = ? and t.TRANSACTION_TYPE = 'expense'
            and date(t.TRANSACTION_DATE) between date(?) and date(?)
        """, (self.TEST_USER_ID, start_date, end_date), fetch_one=True)

        # db_income/db_expense will be None if the query result itself is None or if the first element is None
        db_income = income_result[0] if income_result else None
        db_expense = expense_result[0] if expense_result else None

        self.assertIsNone(db_income)
        self.assertIsNone(db_expense)

    # Ensure category expense data exists
    def test_REP_03_category_expense_data_exists(self):
        year, month = 2023, 10
        start_date = f"{year}-{month:02d}-01"
        _, last_day = calendar.monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day}"

        # Expected: Groceries = 150.50 + 60.00 = 210.50, Utilities = 85.00
        results = run_db_query("""
            select c.NAME, sum(t.AMOUNT) as TOTAL from TRANSACTIONS t
            join CATEGORY c on t.CATEGORY_ID = c.CATEGORY_ID
            join ACCOUNT a on t.ACCOUNT_ID = a.ACCOUNT_ID
            where a.USER_ID = ? and t.TRANSACTION_TYPE = 'expense'
            and date(t.TRANSACTION_DATE) between date(?) and date(?)
            group by c.NAME order by c.NAME
        """, (self.TEST_USER_ID, start_date, end_date))

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "Groceries")
        self.assertAlmostEqual(results[0][1], 210.50)
        self.assertEqual(results[1][0], "Utilities")
        self.assertAlmostEqual(results[1][1], 85.00)

    # Ensure category income data exists
    def test_REP_05_category_income_data_exists(self):
        year, month = 2023, 10
        start_date = f"{year}-{month:02d}-01"
        _, last_day = calendar.monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day}"

        # Expected: Salary = 2500.00, Freelance = 300.00
        results = run_db_query("""
            select c.NAME, sum(t.AMOUNT) as TOTAL from TRANSACTIONS t
            join CATEGORY c on t.CATEGORY_ID = c.CATEGORY_ID
            join ACCOUNT a on t.ACCOUNT_ID = a.ACCOUNT_ID
            where a.USER_ID = ? and t.TRANSACTION_TYPE = 'income'
            and date(t.TRANSACTION_DATE) between date(?) and date(?)
            group by c.NAME order by c.NAME
        """, (self.TEST_USER_ID, start_date, end_date))

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "Freelance")
        self.assertAlmostEqual(results[0][1], 300.00)
        self.assertEqual(results[1][0], "Salary")
        self.assertAlmostEqual(results[1][1], 2500.00)

# Run all those tests!
if __name__ == '__main__':
    unittest.main(verbosity=2)