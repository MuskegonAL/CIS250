import sqlite3

DEFAULT_DB_NAME = "financeManager.db"

# Initialize database in specified Schema - allows use with unit tests
def initialize_database(db_name=DEFAULT_DB_NAME):
    print(f"Initializing database: {db_name}...")
    connection = None
    # Try connecting to database, or create it if it does not exist
    try:
        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()

        cursor.executescript("""
            -- User Table
            create table if not exists USER (
                USER_ID integer primary key autoincrement,
                USERNAME text unique not null,
                EMAIL text not null,
                PASSWORD_HASH text not null,
                CREATED_AT timestamp default current_timestamp,
                UPDATED_AT timestamp default current_timestamp
            );

            -- Account Table
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
            );

            -- Category Table
            create table if not exists CATEGORY (
                CATEGORY_ID integer primary key autoincrement,
                USER_ID integer not null,
                NAME text not null,
                TYPE text not null check (TYPE in ('income', 'expense')),
                DESCRIPTION text,
                PARENT_CATEGORY_ID integer,
                foreign key (USER_ID) references USER(USER_ID) on delete cascade,
                foreign key (PARENT_CATEGORY_ID) references CATEGORY(CATEGORY_ID)
            );

            -- Recurring_Transaction Table
            create table if not exists RECURRING_TRANSACTION (
                RECURRING_ID integer primary key autoincrement,
                ACCOUNT_ID integer not null,
                CATEGORY_ID integer not null,
                AMOUNT decimal(10,2) not null,
                FREQUENCY text not null check (FREQUENCY in ('daily', 'weekly', 'monthly', 'yearly')),
                NEXT_DUE_DATE date, 
                DESCRIPTION text,
                CREATED_AT timestamp default current_timestamp,
                UPDATED_AT timestamp default current_timestamp,
                foreign key (ACCOUNT_ID) references ACCOUNT(ACCOUNT_ID) on delete cascade, 
                foreign key (CATEGORY_ID) references CATEGORY(CATEGORY_ID) on delete restrict 
            );

            -- Create Transactions Table
            create table if not exists TRANSACTIONS (
                TRANSACTION_ID integer primary key autoincrement,
                ACCOUNT_ID integer not null,
                CATEGORY_ID integer not null,
                AMOUNT decimal(10,2) not null,
                TRANSACTION_TYPE text not null check (TRANSACTION_TYPE in ('income', 'expense')),
                TRANSACTION_DATE date not null,
                DESCRIPTION text,
                RECURRING_TRANSACTION_ID integer,
                CREATED_AT timestamp default current_timestamp,
                UPDATED_AT timestamp default current_timestamp,
                foreign key (ACCOUNT_ID) references ACCOUNT(ACCOUNT_ID) on delete cascade, 
                foreign key (CATEGORY_ID) references CATEGORY(CATEGORY_ID) on delete restrict, 
                foreign key (RECURRING_TRANSACTION_ID) references RECURRING_TRANSACTION(RECURRING_ID) on delete set null 
            );

            -- Create Budget Table
            create table if not exists BUDGET (
                BUDGET_ID integer primary key autoincrement,
                ACCOUNT_ID integer not null,
                CATEGORY_ID integer not null,
                PERIOD date not null, 
                BUDGET_AMOUNT decimal(10,2) not null,
                CREATED_AT timestamp default current_timestamp,
                UPDATED_AT timestamp default current_timestamp,
                foreign key (ACCOUNT_ID) references ACCOUNT(ACCOUNT_ID) on delete cascade,
                foreign key (CATEGORY_ID) references CATEGORY(CATEGORY_ID) on delete cascade 
            );
        """)

        connection.commit()
        print(f"Database '{db_name}' initialized successfully!")

    except (sqlite3.Error) as e:
        print(f"An error occurred during database initialization: {e}")
    finally:
        if (connection):
            connection.close()


# Run script automatically
if __name__ == "__main__":
    initialize_database()