import sqlite3

DB_NAME = "financeManager.db"

def Get_DB_Connection():
    return sqlite3.connect(DB_NAME)

def Create_Category(userID, name, categoryType, description=None, parentCategoryID=None):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            insert into CATEGORY (USER_ID, NAME, TYPE, DESCRIPTION, PARENT_CATEGORY_ID)
                values (?, ?, ?, ?, ?)
        """, (userID, name, categoryType, description, parentCategoryID))
        conn.commit()
        print("Category Added")
    except Exception as e:
        print(f"Failed to add category: {e}")
    finally:
        conn.close()

def List_Categories(userID):
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
    """, (userID,))
    categories = cursor.fetchall()
    conn.close()

    if (categories):
        print("\nCategories:")
        for category in categories:
            print(f"ID: {category[0]}, Name: {category[1]}, Type: {category[2]}, Description: {category[3]}, Parent ID: {category[4]}")
    else:
        print("No Categories Found")

def Edit_Category(categoryID, name, categoryType, description=None, parentCategoryID=None):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            update CATEGORY
                set NAME = ?
                  , TYPE = ?
                  , DESCRIPTION = ?
                  , PARENT_CATEGORY_ID = ?
                where CATEGORY_ID = ?
        """, (name, categoryType, description, parentCategoryID, categoryID))

        if (cursor.rowcount == 0):
            print("Category not found")
        else:
            conn.commit()
            print("Category Updated")
    except Exception as e:
        print(f"Failed to update category: {e}")
    finally:
        conn.close()

def Delete_Category(categoryID):
    conn = Get_DB_Connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            select
                    count(*)
                from TRANSACTIONS
                where CATEGORY_ID = ?
        """, (categoryID,))

        count = cursor.fetchone()[0]
        if (count > 0):
            print("Cannot delete category. It is used in existing transactions.")
            return

        cursor.execute("""
            delete from CATEGORY
                where CATEGORY_ID = ?
        """, (categoryID,))

        if (cursor.rowcount == 0):
            print("Category not found")
        else:
            conn.commit()
            print("Category Deleted")
    except Exception as e:
        print(f"Failed to delete category: {e}")
    finally:
        conn.close()