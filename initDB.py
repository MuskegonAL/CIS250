import sqlite3

# Connect to SQLite database
connection = sqlite3.connect("financeManager.db")
cursor = connection.cursor()

# Create User Table
cursor.execute("""
    create table if not exists USER (
        USER_ID integer primary key autoincrement,
        USERNAME text unique not null,
        EMAIL text not null,
        PASSWORD_HASH text not null,
        CREATED_AT timestamp default current_timestamp,
        UPDATED_AT timestamp default current_timestamp
    )
""")

# Create Account Table
cursor.execute("""
    create table if not exists ACCOUNT (
        ACCOUNT_ID integer primary key autoincrement,
        USER_ID integer not null,
        NAME text not null,
        ACCOUNT_TYPE text not null,
        BALANCE decimal(10,2) not null,
        INSTITUTION text not null,
        CREATED_AT timestamp default current_timestamp,
        UPDATED_AT timestamp default current_timestamp,
        foreign key (USER_ID) references USER(USER_ID) on delete cascade
    )
""")

# Create Category Table
cursor.execute("""
    create table if not exists CATEGORY (
        CATEGORY_ID integer primary key autoincrement,
        NAME text not null,
        TYPE text not null,
        DESCRIPTION text,
        PARENT_CATEGORY_ID integer,
        foreign key (PARENT_CATEGORY_ID) references CATEGORY(CATEGORY_ID)
    )
""")

# Create Recurring_Transaction Table
cursor.execute("""
    create table if not exists RECURRING_TRANSACTION (
        RECURRING_ID integer primary key autoincrement,
        ACCOUNT_ID integer not null,
        CATEGORY_ID integer not null,
        AMOUNT decimal(10,2) not null,
        FREQUENCY text not null check (FREQUENCY in ('daily', 'weekly', 'monthly', 'yearly')),
        NEXT_DUE_DATE timestamp default current_timestamp,
        DESCRIPTION text,
        CREATED_AT timestamp default current_timestamp,
        UPDATED_AT timestamp default current_timestamp,
        foreign key (ACCOUNT_ID) references ACCOUNT(ACCOUNT_ID),
        foreign key (CATEGORY_ID) references CATEGORY(CATEGORY_ID)
    )
""")

# Create Transactions Table
cursor.execute("""
    create table if not exists TRANSACTIONS (
        TRANSACTION_ID integer primary key autoincrement,
        ACCOUNT_ID integer not null,
        CATEGORY_ID integer not null,
        AMOUNT decimal(10,2) not null,
        TRANSACTION_TYPE text not null check (TRANSACTION_TYPE in ('income', 'expense')),
        TRANSACTION_DATE timestamp default current_timestamp,
        DESCRIPTION text,
        RECURRING_TRANSACTION_ID integer,
        CREATED_AT timestamp default current_timestamp,
        UPDATED_AT timestamp default current_timestamp,
        foreign key (ACCOUNT_ID) references ACCOUNT(ACCOUNT_ID),
        foreign key (CATEGORY_ID) references CATEGORY(CATEGORY_ID),
        foreign key (RECURRING_TRANSACTION_ID) references RECURRING_TRANSACTION(RECURRING_ID)
    )
""")

# Create Budget Table
cursor.execute("""
    create table if not exists BUDGET (
        BUDGET_ID integer primary key autoincrement,
        ACCOUNT_ID integer not null,
        CATEGORY_ID integer not null,
        PERIOD date not null,
        BUDGET_AMOUNT decimal(10,2) not null,
        CREATED_AT timestamp default current_timestamp,
        UPDATED_AT timestamp default current_timestamp,
        foreign key (ACCOUNT_ID) references ACCOUNT(ACCOUNT_ID),
        foreign key (CATEGORY_ID) references CATEGORY(CATEGORY_ID)
    )
""")

connection.commit()
connection.close()

print("Database initialized successfully!")
