#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
import calendar

# Import backend functions
from auth import Register_User, Login_User, Get_DB_Connection
from accounts import Create_Account, List_Accounts, Edit_Account, Delete_Account
from categories import Create_Category, List_Categories, Edit_Category, Delete_Category
from transactions import Add_Transaction, List_Transactions, Edit_Transaction, Delete_Transaction
from recurring import Add_Recurring_Transaction, List_Recurring_Transactions, Edit_Recurring_Transaction, Delete_Recurring_Transaction, Process_Due_Recurring_Transactions
from reports import Generate_Monthly_Summary, Generate_Category_Report, Generate_Income_Report

# Class for main applictation. This creates the root window and manages the overall application state
# such as the current user and display of different frames.
class FinanceApp(tk.Tk):
    # Main window initialization - title, geometry, user state, styling, ect
    def __init__(self):
        super().__init__() # Inherit from tk.Tk parent
        self.title("Personal Finance Manager - GUI")
        self.geometry("800x700")  # Larger size for main application
        self.user_id = None
        self.username = None

        # Style configuration
        self.style = ttk.Style(self)
        self.style.theme_use("clam")  # Using a modern theme

        # Container frame
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {} # Stores references to different frames
        self.show_frame("LoginFrame") # Display First Login Frame

    # Show specified frame in main container
    def show_frame(self, frame_name):
        # Destroy existing frame if switching between login/register and main app
        if (frame_name == "MainFrame") and ("LoginFrame" in self.frames):
            self.frames["LoginFrame"].destroy()
            if ("RegisterFrame" in self.frames):
                self.frames["RegisterFrame"].destroy()
            self.geometry("800x700")  # Resize for main app

        # Frame switching logic
        if (frame_name in self.frames):
            frame = self.frames[frame_name]
            frame.tkraise()
        # Dynamically create frame if it doesn't exist
        else:
            # Login Frame
            if (frame_name == "LoginFrame"):
                frame = LoginFrame(parent=self.container, controller=self)
                self.geometry("400x300")  # Smaller size for login
            # Registration frame
            elif (frame_name == "RegisterFrame"):
                frame = RegisterFrame(parent=self.container, controller=self)
                self.geometry("400x400")  # Slightly larger for registration
            # Main frame
            elif (frame_name == "MainFrame"):
                frame = MainFrame(parent=self.container, controller=self)
            # Unknown frame
            else:
                print(f"Error: Frame {frame_name} not defined")
                return
                
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    # Successful login - Store data, welcome message, process due recurring transactions, ivew MainFrame
    def login_success(self, user_id, username):
        self.user_id = user_id
        self.username = username
        messagebox.showinfo("Login Success", f"Welcome, {self.username}!")
        
        # Process recurring transactions
        try:
            Process_Due_Recurring_Transactions()  # TODO: Still need to fix recurring transactions posting for all users!!!
        except (Exception) as e:
            print(f"Error processing recurring transactions: {e}")
        
        # Transition to the main application frame
        self.show_frame("MainFrame")

    # Logout - returning to login screen
    def logout(self):
        self.user_id = None
        self.username = None

        # Destroy any existing frames
        if ("MainFrame" in self.frames):
            self.frames["MainFrame"].destroy()
            del self.frames["MainFrame"]

        # Attempt to destroy LoginFrame in-case it already exists
        if ("LoginFrame" in self.frames):
             try:
                 self.frames["LoginFrame"].destroy()
             except (tk.TclError): # Ignore error if already destroyed
                 pass
             del self.frames["LoginFrame"]
        if ("RegisterFrame" in self.frames):
             try:
                 self.frames["RegisterFrame"].destroy()
             except (tk.TclError): # Ignore error if already destroyed
                 pass
             del self.frames["RegisterFrame"]

        # Create and show login frame
        self.geometry("400x300")  # Resize for login screen
        # Create a new instance
        login_frame = LoginFrame(parent=self.container, controller=self)
        # Store it in the dictionary
        self.frames["LoginFrame"] = login_frame
        # Grid and raise the new frame
        login_frame.grid(row=0, column=0, sticky="nsew")
        login_frame.tkraise()

# Login frame class
# TODO: Reset password? Maybe too involved right now
class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Title/sub title
        ttk.Label(self, text="Personal Finance Manager", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self, text="Login", font=("Arial", 14)).pack(pady=5)

        # Username
        ttk.Label(self, text="Username:").pack(pady=(10,0))
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        # Password (masked)
        ttk.Label(self, text="Password:").pack(pady=(10,0))
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)
        
        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

        login_button = ttk.Button(self, text="Login", command=self.attempt_login)
        login_button.pack(pady=20)

        # Register frame bind
        register_label = ttk.Label(self, text="Don't have an account?", foreground="blue", cursor="hand2")
        register_label.pack()
        register_label.bind("<Button-1>", lambda e: controller.show_frame("RegisterFrame"))

    # Attempt to log user in with Login_User function
    def attempt_login(self):
        # Retreive values from input fields
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Validate
        if (not username) or (not password):
            messagebox.showerror("Login Error", "Username and Password cannot be empty.")
            return

        # Attempt to login
        try:
            # Use the backend Login_User function
            user_id = Login_User(username, password)
            if (user_id):
                self.controller.login_success(user_id, username)
            else:
                # Login_User prints error messages to console, show a generic one in GUI
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except (Exception) as e:
            messagebox.showerror("Login Error", f"An unexpected error occurred: {e}")

# Registration frame class
class RegisterFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Titles and labels
        ttk.Label(self, text="Personal Finance Manager", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self, text="Register", font=("Arial", 14)).pack(pady=5)

        # Username
        ttk.Label(self, text="Username:").pack(pady=(10,0))
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        # Email (no real use right now)
        ttk.Label(self, text="Email:").pack(pady=(10,0))
        self.email_entry = ttk.Entry(self)
        self.email_entry.pack(pady=5)

        # Password
        ttk.Label(self, text="Password:").pack(pady=(10,0))
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5)

        # Password confirmation
        ttk.Label(self, text="Confirm Password:").pack(pady=(10,0))
        self.confirm_password_entry = ttk.Entry(self, show="*")
        self.confirm_password_entry.pack(pady=5)
        
        # Bind Enter key to register
        self.confirm_password_entry.bind("<Return>", lambda e: self.attempt_register())

        register_button = ttk.Button(self, text="Register", command=self.attempt_register)
        register_button.pack(pady=20)

        # Check for existing account
        login_label = ttk.Label(self, text="Already have an account? Login", foreground="blue", cursor="hand2")
        login_label.pack()
        login_label.bind("<Button-1>", lambda e: controller.show_frame("LoginFrame"))

    # Attempt to register user using Register_User function
    def attempt_register(self):
        # Get input fields
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        # Validation
        if (not username) or (not email) or (not password) or (not confirm_password):
            messagebox.showerror("Registration Error", "All fields are required.")
            return

        if (password != confirm_password):
            messagebox.showerror("Registration Error", "Passwords do not match.")
            return
        
        # Basic email format check
        if ("@" not in email) or ("." not in email):
             messagebox.showerror("Registration Error", "Invalid email format.")
             return

        try:
            # Use the backend Register_User function
            Register_User(username, email, password)
            messagebox.showinfo("Registration Success", "User registered successfully! Please login.")
            self.controller.show_frame("LoginFrame")  # Go back to login screen
        except (Exception) as e:
            # Catch potential IntegrityError (username exists) or other issues
            messagebox.showerror("Registration Failed", f"Could not register user. It might already exist. Error: {e}")

# Main frame when successful login
class MainFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Create a notebook (tabbed interface) for different functions
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs for different sections
        self.accounts_tab = AccountsTab(self.notebook, controller)
        self.categories_tab = CategoriesTab(self.notebook, controller)
        self.transactions_tab = TransactionsTab(self.notebook, controller)
        self.recurring_tab = RecurringTab(self.notebook, controller)
        self.reports_tab = ReportsTab(self.notebook, controller)
        
        # Add tabs to notebook
        self.notebook.add(self.accounts_tab, text="Accounts")
        self.notebook.add(self.categories_tab, text="Categories")
        self.notebook.add(self.transactions_tab, text="Transactions")
        self.notebook.add(self.recurring_tab, text="Recurring")
        self.notebook.add(self.reports_tab, text="Reports")
        
        # Status bar with user info and logout button
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(status_frame, text=f"Logged in as: {controller.username}").pack(side="left")
        ttk.Button(status_frame, text="Logout", command=controller.logout).pack(side="right")

# Accounts Tab - starting Tab
class AccountsTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Split into two frames - list on left, form on right
        list_frame = ttk.LabelFrame(self, text="Your Accounts")
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        form_frame = ttk.LabelFrame(self, text="Account Details")
        form_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Account list (Treeview)
        columns = ("id", "name", "type", "balance", "institution")
        self.account_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.account_tree.heading("id", text="ID")
        self.account_tree.heading("name", text="Name")
        self.account_tree.heading("type", text="Type")
        self.account_tree.heading("balance", text="Balance")
        self.account_tree.heading("institution", text="Institution")
        
        # Define columns
        self.account_tree.column("id", width=30)
        self.account_tree.column("name", width=100)
        self.account_tree.column("type", width=80)
        self.account_tree.column("balance", width=80)
        self.account_tree.column("institution", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.account_tree.yview)
        self.account_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.account_tree.pack(fill="both", expand=True)
        
        # Bind selection event
        self.account_tree.bind("<<TreeviewSelect>>", self.on_account_select)
        
        # Buttons under list
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_accounts).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_account).pack(side="right", padx=5)
        
        # Form fields
        ttk.Label(form_frame, text="Account Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Account Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.type_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.type_var, 
                     values=["Checking", "Savings", "Credit Card", "Investment", "Other"]).grid(
                     row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Balance:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.balance_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.balance_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Institution:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.institution_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.institution_var).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Hidden field for account ID (for updates)
        self.account_id_var = tk.StringVar()
        
        # Form buttons
        form_btn_frame = ttk.Frame(form_frame)
        form_btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(form_btn_frame, text="New", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(form_btn_frame, text="Save", command=self.save_account).pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Load accounts when tab is shown
        self.bind("<Visibility>", lambda e: self.load_accounts())

    # Load accounts for tree view
    def load_accounts(self):
        # Clear existing items
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
            
        try:
            # Get accounts using backend function
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
            """, (self.controller.user_id,))
            accounts = cursor.fetchall()
            conn.close()
            
            # Insert into treeview
            for account in accounts:
                self.account_tree.insert("", "end", values=account)
                
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to load accounts: {e}")

    # When an account is selected
    def on_account_select(self, event):
        selected_items = self.account_tree.selection()
        if (not selected_items):
            return
            
        # Get values of selected item
        item = self.account_tree.item(selected_items[0])
        account_id, name, acc_type, balance, institution = item["values"]
        
        # Update form fields
        self.account_id_var.set(account_id)
        self.name_var.set(name)
        self.type_var.set(acc_type)
        self.balance_var.set(balance)
        self.institution_var.set(institution)

    # Clear account form
    def clear_form(self):
        self.account_id_var.set("")
        self.name_var.set("")
        self.type_var.set("")
        self.balance_var.set("")
        self.institution_var.set("")
        
        # Deselect any selected item
        for selected_item in self.account_tree.selection():
            self.account_tree.selection_remove(selected_item)

    # Create/update an account
    def save_account(self):
        name = self.name_var.get()
        acc_type = self.type_var.get()
        
        # Validate required fields
        if (not name) or (not acc_type):
            messagebox.showerror("Error", "Name and Type are required.")
            return
            
        # Validate balance
        try:
            balance = float(self.balance_var.get())
        except (ValueError):
            messagebox.showerror("Error", "Balance must be a number.")
            return
            
        institution = self.institution_var.get()
        account_id = self.account_id_var.get()
        
        try:
            if (account_id):  # Update existing
                Edit_Account(account_id, name, acc_type, balance, institution)
                messagebox.showinfo("Success", "Account updated successfully.")
            else:  # Create new
                Create_Account(self.controller.user_id, name, acc_type, balance, institution)
                messagebox.showinfo("Success", "Account created successfully.")
                
            # Refresh the list
            self.load_accounts()
            self.clear_form()
            
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to save account: {e}")

    # Delete an account
    def delete_account(self):
        selected_items = self.account_tree.selection()
        if (not selected_items):
            messagebox.showinfo("Info", "Please select an account to delete.")
            return
            
        # Get account ID
        item = self.account_tree.item(selected_items[0])
        account_id = item["values"][0]
        
        # Confirm deletion
        if (messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this account? This will also delete all associated transactions.")):
            try:
                Delete_Account(account_id)
                messagebox.showinfo("Success", "Account deleted successfully.")
                self.load_accounts()
                self.clear_form()
            except (Exception) as e:
                messagebox.showerror("Error", f"Failed to delete account: {e}")

# Categories tab class - displays categories in treeview for adding/editing
class CategoriesTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Split into two frames - list on left, form on right
        list_frame = ttk.LabelFrame(self, text="Your Categories")
        list_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        form_frame = ttk.LabelFrame(self, text="Category Details")
        form_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Category list (Treeview)
        columns = ("id", "name", "type", "description", "parent")
        self.category_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.category_tree.heading("id", text="ID")
        self.category_tree.heading("name", text="Name")
        self.category_tree.heading("type", text="Type")
        self.category_tree.heading("description", text="Description")
        self.category_tree.heading("parent", text="Parent ID")
        
        # Define columns
        self.category_tree.column("id", width=30)
        self.category_tree.column("name", width=100)
        self.category_tree.column("type", width=80)
        self.category_tree.column("description", width=150)
        self.category_tree.column("parent", width=60)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.category_tree.pack(fill="both", expand=True)
        
        # Bind selection event
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)
        
        # Buttons under list
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_categories).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_category).pack(side="right", padx=5)
        
        # Form fields
        ttk.Label(form_frame, text="Category Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Category Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.type_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.type_var, 
                     values=["income", "expense"]).grid(
                     row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.description_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Parent Category ID:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.parent_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.parent_var).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Hidden field for category ID (for updates)
        self.category_id_var = tk.StringVar()
        
        # Form buttons
        form_btn_frame = ttk.Frame(form_frame)
        form_btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(form_btn_frame, text="New", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(form_btn_frame, text="Save", command=self.save_category).pack(side="left", padx=5)
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        # Load categories when tab is shown
        self.bind("<Visibility>", lambda e: self.load_categories())

    # Load categories into tree view
    def load_categories(self):
        # Clear existing items
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
            
        try:
            # Get categories using backend function
            conn = Get_DB_Connection()
            cursor = conn.cursor()
            cursor.execute("""
                select 
                        CATEGORY_ID
                      , NAME
                      , TYPE
                      , DESCRIPTION
                      , PARENT_CATEGORY_ID
                    from CATEGORY
                    where USER_ID = ?
            """, (self.controller.user_id,))
            categories = cursor.fetchall()
            conn.close()
            
            # Insert into treeview
            for category in categories:
                self.category_tree.insert("", "end", values=category)
                
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to load categories: {e}")

    # When selecting a category
    def on_category_select(self, event):
        selected_items = self.category_tree.selection()
        if (not selected_items):
            return
            
        # Get values of selected item
        item = self.category_tree.item(selected_items[0])
        category_id, name, cat_type, description, parent_id = item["values"]
        
        # Update form fields
        self.category_id_var.set(category_id)
        self.name_var.set(name)
        self.type_var.set(cat_type)
        self.description_var.set(description if description else "")
        self.parent_var.set(parent_id if parent_id else "")

    # Clear category form
    def clear_form(self):
        self.category_id_var.set("")
        self.name_var.set("")
        self.type_var.set("")
        self.description_var.set("")
        self.parent_var.set("")
        
        # Deselect any selected item
        for selected_item in self.category_tree.selection():
            self.category_tree.selection_remove(selected_item)

    # Create/Save a category
    def save_category(self):
        name = self.name_var.get()
        cat_type = self.type_var.get()
        
        # Validate required fields
        if (not name) or (not cat_type):
            messagebox.showerror("Error", "Name and Type are required.")
            return
            
        # Validate type
        if (cat_type not in ["income", "expense"]):
            messagebox.showerror("Error", "Type must be 'income' or 'expense'.")
            return
            
        description = self.description_var.get() if self.description_var.get() else None
        
        # Validate parent ID if provided
        parent_id = None
        if (self.parent_var.get()):
            try:
                parent_id = int(self.parent_var.get())
            except (ValueError):
                messagebox.showerror("Error", "Parent ID must be a number.")
                return
                
        category_id = self.category_id_var.get()
        
        try:
            if (category_id):  # Update existing
                Edit_Category(category_id, name, cat_type, description, parent_id)
                messagebox.showinfo("Success", "Category updated successfully.")
            else:  # Create new
                Create_Category(self.controller.user_id, name, cat_type, description, parent_id)
                messagebox.showinfo("Success", "Category created successfully.")
                
            # Refresh the list
            self.load_categories()
            self.clear_form()
            
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to save category: {e}")

    # Delete a category
    def delete_category(self):
        selected_items = self.category_tree.selection()
        if (not selected_items):
            messagebox.showinfo("Info", "Please select a category to delete.")
            return
            
        # Get category ID
        item = self.category_tree.item(selected_items[0])
        category_id = item["values"][0]
        
        # Confirm deletion
        if (messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this category? This will fail if transactions use it.")):
            try:
                Delete_Category(category_id)
                messagebox.showinfo("Success", "Category deleted successfully.")
                self.load_categories()
                self.clear_form()
            except (Exception) as e:
                messagebox.showerror("Error", f"Failed to delete category: {e}")

# Transactions tab class
class TransactionsTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Account selection at top
        account_frame = ttk.Frame(self)
        account_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(account_frame, text="Select Account:").pack(side="left", padx=5)
        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(account_frame, textvariable=self.account_var, state="readonly")
        self.account_combo.pack(side="left", padx=5)
        self.account_combo.bind("<<ComboboxSelected>>", self.on_account_change)
        
        ttk.Button(account_frame, text="Refresh Accounts", command=self.load_accounts).pack(side="left", padx=5)
        
        # Split into two frames - list on top, form on bottom
        list_frame = ttk.LabelFrame(self, text="Transactions")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        form_frame = ttk.LabelFrame(self, text="Transaction Details")
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # Transaction list (Treeview)
        columns = ("id", "date", "category", "type", "amount", "description")
        self.transaction_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.transaction_tree.heading("id", text="ID")
        self.transaction_tree.heading("date", text="Date")
        self.transaction_tree.heading("category", text="Category")
        self.transaction_tree.heading("type", text="Type")
        self.transaction_tree.heading("amount", text="Amount")
        self.transaction_tree.heading("description", text="Description")
        
        # Define columns
        self.transaction_tree.column("id", width=30)
        self.transaction_tree.column("date", width=80)
        self.transaction_tree.column("category", width=100)
        self.transaction_tree.column("type", width=60)
        self.transaction_tree.column("amount", width=80)
        self.transaction_tree.column("description", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.transaction_tree.yview)
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.transaction_tree.pack(fill="both", expand=True)
        
        # Bind selection event
        self.transaction_tree.bind("<<TreeviewSelect>>", self.on_transaction_select)
        
        # Buttons under list
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_transactions).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_transaction).pack(side="right", padx=5)
        
        # Form fields - use grid layout for better alignment
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        # Row 0
        ttk.Label(form_frame, text="Category:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Amount:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.amount_var).grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Row 1
        ttk.Label(form_frame, text="Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.type_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.type_var, values=["income", "expense"], state="readonly").grid(
                     row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.date_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.date_var).grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        ttk.Label(form_frame, text="(YYYY-MM-DD)").grid(row=1, column=4, sticky="w", padx=0, pady=5)
        
        # Row 2
        ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.description_var).grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Hidden field for transaction ID (for updates)
        self.transaction_id_var = tk.StringVar()
        
        # Form buttons
        form_btn_frame = ttk.Frame(form_frame)
        form_btn_frame.grid(row=3, column=0, columnspan=5, pady=10)
        
        ttk.Button(form_btn_frame, text="New", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(form_btn_frame, text="Save", command=self.save_transaction).pack(side="left", padx=5)
        
        # Load accounts when tab is shown
        self.bind("<Visibility>", lambda e: self.load_accounts())
        
        # Load categories
        self.load_categories()
        
        # Set default date to today
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))

    # Load accounts for drop-down
    def load_accounts(self):
        try:
            # Get accounts using backend function
            # ... (existing code to fetch accounts) ...
            conn = Get_DB_Connection()
            cursor = conn.cursor()
            cursor.execute("""
                select
                        ACCOUNT_ID
                      , NAME
                    from ACCOUNT
                    where USER_ID = ?
            """, (self.controller.user_id,))
            accounts = cursor.fetchall()
            conn.close()

            self.accounts = {f"{account[0]}: {account[1]}": account[0] for account in accounts}
            self.account_combo["values"] = list(self.accounts.keys())

            # --- ADD THIS LINE ---
            self.load_categories() # Refresh categories whenever accounts are loaded/refreshed

            # Select first account if available
            if (self.accounts) and (not self.account_var.get()):
                self.account_combo.current(0)
                self.load_transactions() # Load transactions for the newly selected account

        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to load accounts: {e}")

    # Load categories for drop-down
    def load_categories(self):
        # --- Ensure controller.user_id is valid ---
        if not self.controller or not self.controller.user_id:
             print("Warning: Cannot load categories, user_id not available.")
             self.category_combo["values"] = [] # Clear the list if no user
             return

        try:
            # ... (existing code to fetch categories) ...
            conn = Get_DB_Connection()
            cursor = conn.cursor()
            cursor.execute("""
                select
                        CATEGORY_ID
                      , NAME
                      , TYPE
                    from CATEGORY
                    where USER_ID = ?
            """, (self.controller.user_id,)) # Use the controller's user_id
            categories = cursor.fetchall()
            conn.close()

            # Store category mapping for later use
            self.categories = {f"{cat[0]}: {cat[1]} ({cat[2]})": cat[0] for cat in categories}

            # Update combobox
            self.category_combo["values"] = list(self.categories.keys())

            # --- Optional: Select first if list is not empty and nothing is selected ---
            # if self.categories and not self.category_var.get():
            #    self.category_combo.current(0)

        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to load categories: {e}")
            self.category_combo["values"] = [] # Clear list on error

    # When changing accounts - reload transactions
    def on_account_change(self, event):
        self.load_transactions()
        self.clear_form()

    # Load transactions for selected account
    def load_transactions(self):
        # Clear existing items
        for item in self.transaction_tree.get_children():
            self.transaction_tree.delete(item)
            
        # Check if account is selected
        if (not self.account_var.get()):
            return
            
        try:
            # Get account ID from selection
            account_id = self.accounts[self.account_var.get()]
            
            # Get transactions using direct database query (could be modified to use List_Transactions)
            conn = Get_DB_Connection()
            cursor = conn.cursor()
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
            """, (account_id,))
            transactions = cursor.fetchall()
            conn.close()
            
            # Insert into treeview
            for tx in transactions:
                self.transaction_tree.insert("", "end", values=tx)
                
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to load transactions: {e}")

    # When selecting a transaction
    def on_transaction_select(self, event):
        selected_items = self.transaction_tree.selection()
        if (not selected_items):
            return
            
        # Get values of selected item
        item = self.transaction_tree.item(selected_items[0])
        tx_id, date, category_name, tx_type, amount, description = item["values"]
        
        # Get category ID for this transaction
        conn = Get_DB_Connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CATEGORY_ID FROM TRANSACTIONS WHERE TRANSACTION_ID = ?", (tx_id,))
        category_id = cursor.fetchone()[0]
        conn.close()
        
        # Find the category in our mapping
        category_key = None
        for key, value in self.categories.items():
            if value == category_id:
                category_key = key
                break
        
        # Update form fields
        self.transaction_id_var.set(tx_id)
        if (category_key):
            self.category_var.set(category_key)
        self.type_var.set(tx_type)
        self.amount_var.set(amount)
        self.date_var.set(date)
        self.description_var.set(description if description else "")

    # Clear transaction form
    def clear_form(self):
        self.transaction_id_var.set("")
        self.category_var.set("")
        self.type_var.set("")
        self.amount_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))  # Default to today
        self.description_var.set("")
        
        # Deselect any selected item
        for selected_item in self.transaction_tree.selection():
            self.transaction_tree.selection_remove(selected_item)

    # Create/Save a transaction
    def save_transaction(self):
        # Validate required fields
        if (not self.account_var.get()) or (not self.category_var.get()) or (not self.type_var.get()):
            messagebox.showerror("Error", "Account, Category and Type are required.")
            return
            
        # Validate amount
        try:
            amount = float(self.amount_var.get())
            if amount <= 0:
                messagebox.showerror("Error", "Amount must be greater than zero.")
                return
        except (ValueError):
            messagebox.showerror("Error", "Amount must be a number.")
            return
            
        # Validate date
        date_str = self.date_var.get()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError):
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return
            
        # Get IDs from selections
        account_id = self.accounts[self.account_var.get()]
        category_id = self.categories[self.category_var.get()]
        tx_type = self.type_var.get()
        description = self.description_var.get() if self.description_var.get() else None
        transaction_id = self.transaction_id_var.get()
        
        try:
            if (transaction_id):  # Update existing
                Edit_Transaction(transaction_id, account_id, category_id, amount, tx_type, date_str, description)
                messagebox.showinfo("Success", "Transaction updated successfully.")
            else:  # Create new
                Add_Transaction(account_id, category_id, amount, tx_type, date_str, description)
                messagebox.showinfo("Success", "Transaction added successfully.")
                
            # Refresh the list
            self.load_transactions()
            self.clear_form()
            
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to save transaction: {e}")

    # Delete a transaction
    def delete_transaction(self):
        selected_items = self.transaction_tree.selection()
        if (not selected_items):
            messagebox.showinfo("Info", "Please select a transaction to delete.")
            return
            
        # Get transaction ID
        item = self.transaction_tree.item(selected_items[0])
        transaction_id = item["values"][0]
        
        # Confirm deletion
        if (messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction? This will adjust account balance.")):
            try:
                Delete_Transaction(transaction_id)
                messagebox.showinfo("Success", "Transaction deleted successfully.")
                self.load_transactions()
                self.clear_form()
            except (Exception) as e:
                messagebox.showerror("Error", f"Failed to delete transaction: {e}")

# Recurring transactions tab class
class RecurringTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Top buttons
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(top_frame, text="Process Due Recurring Transactions", 
                  command=self.process_recurring).pack(side="left", padx=5)
        
        # Split into two frames - list on top, form on bottom
        list_frame = ttk.LabelFrame(self, text="Recurring Transactions")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        form_frame = ttk.LabelFrame(self, text="Recurring Transaction Details")
        form_frame.pack(fill="x", padx=10, pady=10)
        
        # Recurring list (Treeview)
        columns = ("id", "account", "category", "amount", "frequency", "next_due", "description")
        self.recurring_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Define headings
        self.recurring_tree.heading("id", text="ID")
        self.recurring_tree.heading("account", text="Account")
        self.recurring_tree.heading("category", text="Category")
        self.recurring_tree.heading("amount", text="Amount")
        self.recurring_tree.heading("frequency", text="Frequency")
        self.recurring_tree.heading("next_due", text="Next Due")
        self.recurring_tree.heading("description", text="Description")
        
        # Define columns
        self.recurring_tree.column("id", width=30)
        self.recurring_tree.column("account", width=100)
        self.recurring_tree.column("category", width=100)
        self.recurring_tree.column("amount", width=80)
        self.recurring_tree.column("frequency", width=80)
        self.recurring_tree.column("next_due", width=80)
        self.recurring_tree.column("description", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.recurring_tree.yview)
        self.recurring_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.recurring_tree.pack(fill="both", expand=True)
        
        # Bind selection event
        self.recurring_tree.bind("<<TreeviewSelect>>", self.on_recurring_select)
        
        # Buttons under list
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="Refresh", command=self.load_recurring).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", command=self.delete_recurring).pack(side="right", padx=5)
        
        # Form fields - use grid layout for better alignment
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)
        
        # Row 0
        ttk.Label(form_frame, text="Account:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(form_frame, textvariable=self.account_var, state="readonly")
        self.account_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Category:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=0, column=3, sticky="ew", padx=5, pady=5)
        
        # Row 1
        ttk.Label(form_frame, text="Amount:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.amount_var).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(form_frame, text="Frequency:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.frequency_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.frequency_var, 
                    values=["daily", "weekly", "monthly", "yearly"], state="readonly").grid(
                    row=1, column=3, sticky="ew", padx=5, pady=5)
        
        # Row 2
        ttk.Label(form_frame, text="Next Due Date:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.next_due_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.next_due_var).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_frame, text="(YYYY-MM-DD)").grid(row=2, column=2, sticky="w", padx=0, pady=5)
        
        # Row 3
        ttk.Label(form_frame, text="Description:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.description_var).grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        # Hidden field for recurring ID (for updates)
        self.recurring_id_var = tk.StringVar()
        
        # Form buttons
        form_btn_frame = ttk.Frame(form_frame)
        form_btn_frame.grid(row=4, column=0, columnspan=4, pady=10)
        
        ttk.Button(form_btn_frame, text="New", command=self.clear_form).pack(side="left", padx=5)
        ttk.Button(form_btn_frame, text="Save", command=self.save_recurring).pack(side="left", padx=5)
        
        # Load data when tab is shown
        self.bind("<Visibility>", lambda e: self.on_visibility())
        
        # Set default date to today
        self.next_due_var.set(datetime.now().strftime("%Y-%m-%d"))

    # When tab becomes visible, load information
    def on_visibility(self):
        self.load_accounts()
        self.load_categories()
        self.load_recurring()

    # Load accounts for recurring transactions drop-down
    def load_accounts(self):
        try:
            # Get accounts using backend function
            conn = Get_DB_Connection()
            cursor = conn.cursor()
            cursor.execute("""
                select
                        ACCOUNT_ID
                      , NAME
                    from ACCOUNT
                    where USER_ID = ?
            """, (self.controller.user_id,))
            accounts = cursor.fetchall()
            conn.close()
            
            # Store account mapping for later use
            self.accounts = {f"{account[0]}: {account[1]}": account[0] for account in accounts}
            
            # Update combobox
            self.account_combo["values"] = list(self.accounts.keys())
                
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to load accounts: {e}")

    # Load categories for recurring transaction drop-down
    def load_categories(self):
        try:
            # Get categories using backend function
            conn = Get_DB_Connection()
            cursor = conn.cursor()
            cursor.execute("""
                select 
                        CATEGORY_ID
                      , NAME
                    from CATEGORY
                    where USER_ID = ? and TYPE = 'expense'
            """, (self.controller.user_id,))
            categories = cursor.fetchall()
            conn.close()
            
            # Store category mapping for later use
            self.categories = {f"{cat[0]}: {cat[1]}": cat[0] for cat in categories}
            
            # Update combobox
            self.category_combo["values"] = list(self.categories.keys())
                
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to load categories: {e}")

    # Load recurring transactions
    def load_recurring(self):
        # Clear existing items
        for item in self.recurring_tree.get_children():
            self.recurring_tree.delete(item)
            
        try:
            # Get recurring transactions for all user accounts
            conn = Get_DB_Connection()
            cursor = conn.cursor()
            cursor.execute("""
                select 
                    r.RECURRING_ID,
                    a.NAME as ACCOUNT_NAME,
                    c.NAME as CATEGORY_NAME,
                    r.AMOUNT,
                    r.FREQUENCY,
                    r.NEXT_DUE_DATE,
                    r.DESCRIPTION,
                    r.ACCOUNT_ID,
                    r.CATEGORY_ID
                from RECURRING_TRANSACTION r
                join ACCOUNT a on r.ACCOUNT_ID = a.ACCOUNT_ID
                join CATEGORY c on r.CATEGORY_ID = c.CATEGORY_ID
                where a.USER_ID = ?
                order by r.NEXT_DUE_DATE
            """, (self.controller.user_id,))
            recurring = cursor.fetchall()
            conn.close()
            
            # Store full data for later use
            self.recurring_data = {r[0]: r for r in recurring}
            
            # Insert into treeview (excluding the account_id and category_id at the end)
            for r in recurring:
                self.recurring_tree.insert("", "end", values=r[:7])
                
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to load recurring transactions: {e}")

    # When selecting a recurring transaction
    def on_recurring_select(self, event):
        selected_items = self.recurring_tree.selection()
        if (not selected_items):
            return
            
        # Get values of selected item
        item = self.recurring_tree.item(selected_items[0])
        recurring_id = item["values"][0]
        
        # Get full data from our stored mapping
        if (recurring_id in self.recurring_data):
            r = self.recurring_data[recurring_id]
            recurring_id, account_name, category_name, amount, frequency, next_due, description, account_id, category_id = r
            
            # Find the account and category in our mappings
            account_key = None
            for key, value in self.accounts.items():
                if (value == account_id):
                    account_key = key
                    break
                    
            category_key = None
            for key, value in self.categories.items():
                if (value == category_id):
                    category_key = key
                    break
            
            # Update form fields
            self.recurring_id_var.set(recurring_id)
            if (account_key):
                self.account_var.set(account_key)
            if (category_key):
                self.category_var.set(category_key)
            self.amount_var.set(amount)
            self.frequency_var.set(frequency)
            self.next_due_var.set(next_due)
            self.description_var.set(description if description else "")

    # Clear recurring transactions form
    def clear_form(self):
        self.recurring_id_var.set("")
        self.account_var.set("")
        self.category_var.set("")
        self.amount_var.set("")
        self.frequency_var.set("")
        self.next_due_var.set(datetime.now().strftime("%Y-%m-%d"))  # Default to today
        self.description_var.set("")
        
        # Deselect any selected item
        for selected_item in self.recurring_tree.selection():
            self.recurring_tree.selection_remove(selected_item)

    # Create/Save recurring transactions
    def save_recurring(self):
        # Validate required fields
        if (not self.account_var.get()) or (not self.category_var.get()) or (not self.frequency_var.get()):
            messagebox.showerror("Error", "Account, Category and Frequency are required.")
            return
            
        # Validate amount
        try:
            amount = float(self.amount_var.get())
            if (amount <= 0):
                messagebox.showerror("Error", "Amount must be greater than zero.")
                return
        except (ValueError):
            messagebox.showerror("Error", "Amount must be a number.")
            return
            
        # Validate date
        next_due_str = self.next_due_var.get()
        try:
            datetime.strptime(next_due_str, "%Y-%m-%d")
        except (ValueError):
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")
            return
            
        # Get IDs from selections
        account_id = self.accounts[self.account_var.get()]
        category_id = self.categories[self.category_var.get()]
        frequency = self.frequency_var.get()
        description = self.description_var.get() if self.description_var.get() else None
        recurring_id = self.recurring_id_var.get()
        
        try:
            if (recurring_id):  # Update existing
                Edit_Recurring_Transaction(recurring_id, account_id, category_id, amount, frequency, next_due_str, description)
                messagebox.showinfo("Success", "Recurring transaction updated successfully.")
            else:  # Create new
                Add_Recurring_Transaction(account_id, category_id, amount, frequency, next_due_str, description)
                messagebox.showinfo("Success", "Recurring transaction added successfully.")
                
            # Refresh the list
            self.load_recurring()
            self.clear_form()
            
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to save recurring transaction: {e}")

    # Delete recurring transaction
    def delete_recurring(self):
        selected_items = self.recurring_tree.selection()
        if (not selected_items):
            messagebox.showinfo("Info", "Please select a recurring transaction to delete.")
            return
            
        # Get recurring ID
        item = self.recurring_tree.item(selected_items[0])
        recurring_id = item["values"][0]
        
        # Confirm deletion
        if (messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this recurring transaction?")):
            try:
                Delete_Recurring_Transaction(recurring_id)
                messagebox.showinfo("Success", "Recurring transaction deleted successfully.")
                self.load_recurring()
                self.clear_form()
            except (Exception) as e:
                messagebox.showerror("Error", f"Failed to delete recurring transaction: {e}")

    # Process recurring transactions
    # TODO: Fix processing occuring for all accounts
    def process_recurring(self):
        try:
            Process_Due_Recurring_Transactions()
            messagebox.showinfo("Success", "Processed due recurring transactions.")
            self.load_recurring()
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to process recurring transactions: {e}")

# Reports tab class
class ReportsTab(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Report selection frame
        selection_frame = ttk.LabelFrame(self, text="Generate Report")
        selection_frame.pack(fill="x", padx=10, pady=10)
        
        # Report type
        ttk.Label(selection_frame, text="Report Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.report_type_var = tk.StringVar()
        ttk.Combobox(selection_frame, textvariable=self.report_type_var, 
                    values=["Monthly Summary", "Expense Categories", "Income Categories"], 
                    state="readonly").grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Date selection
        ttk.Label(selection_frame, text="Year:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        current_year = datetime.now().year
        self.year_var = tk.StringVar(value=str(current_year))
        years = [str(y) for y in range(current_year-5, current_year+1)]
        ttk.Combobox(selection_frame, textvariable=self.year_var, values=years, state="readonly").grid(
                    row=1, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Month:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        current_month = datetime.now().month
        self.month_var = tk.StringVar(value=str(current_month))
        months = [(str(m), calendar.month_name[m]) for m in range(1, 13)]
        month_combo = ttk.Combobox(selection_frame, textvariable=self.month_var, 
                                  values=[f"{m[0]}: {m[1]}" for m in months], state="readonly")
        month_combo.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        month_combo.current(current_month-1)  # Select current month
        
        # Generate button
        ttk.Button(selection_frame, text="Generate Report", command=self.generate_report).grid(
                  row=3, column=0, columnspan=2, pady=10)
        
        # Configure grid weights
        selection_frame.columnconfigure(1, weight=1)
        
        # Report display frame
        self.report_frame = ttk.LabelFrame(self, text="Report Results")
        self.report_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Text widget for report display
        self.report_text = tk.Text(self.report_frame, wrap="word", height=20)
        self.report_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Scrollbar for text widget
        scrollbar = ttk.Scrollbar(self.report_text, orient="vertical", command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    # Generate selected report
    def generate_report(self):
        # Validate selections
        if (not self.report_type_var.get()):
            messagebox.showerror("Error", "Please select a report type.")
            return
            
        try:
            year = int(self.year_var.get())
            month = int(self.month_var.get().split(":")[0])
        except (ValueError):
            messagebox.showerror("Error", "Invalid year or month.")
            return
            
        # Clear previous report
        self.report_text.delete(1.0, tk.END)
        
        # Redirect stdout to capture report output
        import io
        import sys
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        
        try:
            # Generate selected report
            report_type = self.report_type_var.get()
            if (report_type == "Monthly Summary"):
                Generate_Monthly_Summary(self.controller.user_id, year, month)
            elif (report_type == "Expense Categories"):
                Generate_Category_Report(self.controller.user_id, year, month)
            elif (report_type == "Income Categories"):
                Generate_Income_Report(self.controller.user_id, year, month)
                
            # Get report output
            report_output = new_stdout.getvalue()
            
            # Display in text widget
            self.report_text.insert(tk.END, report_output)
            
        except (Exception) as e:
            messagebox.showerror("Error", f"Failed to generate report: {e}")
        finally:
            # Restore stdout
            sys.stdout = old_stdout

# RUN APPLICATION!!
if __name__ == "__main__":
    # Ensure database exists (run initDB.py first if needed)
    try:
        import sqlite3
        conn = sqlite3.connect("financeManager.db")
        # Quick check if USER table exists
        conn.execute("SELECT 1 FROM USER LIMIT 1")
        conn.close()
    except (sqlite3.Error) as e:
        print(f"Database error: {e}")
        print("Please ensure the database 'financeManager.db' exists and is initialized.")
        print("You may need to run 'python initDB.py' first.")
        exit()
        
    app = FinanceApp()
    app.mainloop()
