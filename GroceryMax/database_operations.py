# database_operations.py
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
load_dotenv()

# Load from environment variables with defaults for local development (optional)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_NAME = os.environ.get('DB_NAME', 'grocery_store_db')
DB_USER = os.environ.get('DB_USER', 'grocery_app_user')
DB_PASSWORD = os.environ.get('DB_PASSWORD', None) # No default for password is safer

# Check if essential DB_PASSWORD is set
if DB_PASSWORD is None:
    print("CRITICAL ERROR: DB_PASSWORD environment variable is not set.")

DB_CONFIG = {
    'host': DB_HOST,
    'database': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD
}

def create_connection():
    """Creates and returns a MySQL database connection object or None on failure."""
    conn = None
    if not DB_CONFIG['password']: # Check again if password is None
        print("DB_Connection_Error: Password not configured. Set DB_PASSWORD environment variable.")
        return None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"DB_Connection_Error: {e}")
        # More detailed error for missing password:
        if "Access denied" in str(e) and not DB_CONFIG['password']:
             print("Hint: Ensure DB_PASSWORD environment variable is set correctly.")
    return conn

# --- Category Functions ---
def add_category(conn, category_name, description=""):
    """Adds a new category. Returns new CategoryID or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (add_category).")
        return None
    cursor = None
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO Categories (CategoryName, Description) VALUES (%s, %s)"
        val = (category_name, description)
        cursor.execute(sql, val)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        if e.errno == 1062: # Duplicate entry
            print(f"DB_Error: Category name '{category_name}' already exists.")
        else:
            print(f"DB_Error adding category '{category_name}': {e}")
        if conn.is_connected():
            try: conn.rollback()
            except Error as rb_error: print(f"DB_Error during rollback (add_category): {rb_error}")
        return None
    finally:
        if cursor: cursor.close()

def fetch_categories(conn):
    """Fetches all categories, ordered by name. Returns a list of dicts or an empty list."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (fetch_categories).")
        return []
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("SELECT CategoryID, CategoryName, Description FROM Categories ORDER BY CategoryName")
        return cursor.fetchall()
    except Error as e:
        print(f"DB_Error fetching categories: {e}")
        return []
    finally:
        if cursor: cursor.close()

def get_category_by_id(conn, category_id):
    """Fetches a category by its ID. Returns a dict or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (get_category_by_id).")
        return None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = "SELECT CategoryID, CategoryName, Description FROM Categories WHERE CategoryID = %s"
        cursor.execute(sql, (category_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"DB_Error fetching category by ID '{category_id}': {e}")
        return None
    finally:
        if cursor: cursor.close()

def get_category_by_name(conn, category_name):
    """Fetches a category by name. Returns a dict or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (get_category_by_name).")
        return None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = "SELECT CategoryID, CategoryName, Description FROM Categories WHERE CategoryName = %s"
        cursor.execute(sql, (category_name,))
        return cursor.fetchone()
    except Error as e:
        print(f"DB_Error fetching category by name '{category_name}': {e}")
        return None
    finally:
        if cursor: cursor.close()

def get_or_create_category(conn, category_name, description=""):
    """Gets a category by name; if not found, creates it. Returns CategoryID or None."""
    category = get_category_by_name(conn, category_name)
    if category:
        return category['CategoryID']
    return add_category(conn, category_name, description)

def update_category(conn, category_id, new_name, new_description):
    """Updates an existing category. Returns True on success, False on failure."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (update_category).")
        return False
    cursor = None
    try:
        cursor = conn.cursor()
        sql = "UPDATE Categories SET CategoryName = %s, Description = %s WHERE CategoryID = %s"
        cursor.execute(sql, (new_name, new_description, category_id))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        if e.errno == 1062:
            print(f"DB_Error updating Category ID {category_id}: Name '{new_name}' already exists.")
        else:
            print(f"DB_Error updating Category ID {category_id}: {e}")
        if conn.is_connected(): conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def delete_category(conn, category_id):
    """Deletes a category. Returns True on success, False on failure."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (delete_category).")
        return False
    cursor = None
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM Categories WHERE CategoryID = %s"
        cursor.execute(sql, (category_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        if e.errno == 1451: # Foreign key constraint violation
            print(f"DB_Error: Cannot delete Category ID {category_id}, referenced by products.")
        else:
            print(f"DB_Error deleting Category ID {category_id}: {e}")
        if conn.is_connected(): conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

# --- Product Functions ---
def get_product_by_id(conn, product_id):
    """Fetches a product by ID, including CategoryName. Returns a dict or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (get_product_by_id).")
        return None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = """SELECT p.*, c.CategoryName
                 FROM Products p
                 LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
                 WHERE p.ProductID = %s"""
        cursor.execute(sql, (product_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"DB_Error fetching product by ID '{product_id}': {e}")
        return None
    finally:
        if cursor: cursor.close()

def get_product_by_name(conn, product_name):
    """Fetches a product by its name. Returns a dict or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (get_product_by_name).")
        return None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = "SELECT * FROM Products WHERE ProductName = %s"
        cursor.execute(sql, (product_name,))
        return cursor.fetchone()
    except Error as e:
        print(f"DB_Error fetching product by name '{product_name}': {e}")
        return None
    finally:
        if cursor: cursor.close()

def actual_add_product(conn, product_name, description, category_id, price, stock_quantity, supplier_id=None):
    """Internal: Inserts a new product. Returns ProductID or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (actual_add_product).")
        return None
    if category_id is None:
        print(f"DB_Logic_Error: CategoryID missing for product '{product_name}'.")
        return None
    cursor = None
    try:
        cursor = conn.cursor()
        sql = """INSERT INTO Products
                 (ProductName, Description, CategoryID, Price, StockQuantity, SupplierID)
                 VALUES (%s, %s, %s, %s, %s, %s)"""
        val = (product_name, description, category_id, price, stock_quantity, supplier_id)
        cursor.execute(sql, val)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        if e.errno == 1062:
            print(f"DB_Error: Product '{product_name}' already exists (Unique Constraint).")
        else:
            print(f"DB_Error adding product '{product_name}': {e}")
        if conn.is_connected(): conn.rollback()
        return None
    finally:
        if cursor: cursor.close()

def update_product_details(conn, product_id, new_price=None, new_stock_quantity=None, new_description=None, new_category_id=None):
    """Updates product details. Returns True on success, False otherwise."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (update_product_details).")
        return False
    if not any([new_price is not None, new_stock_quantity is not None, new_description is not None, new_category_id is not None]):
        return False # No actual updates provided

    updates = []
    params = []
    if new_description is not None: updates.append("Description = %s"); params.append(new_description)
    if new_category_id is not None: updates.append("CategoryID = %s"); params.append(new_category_id)
    if new_price is not None: updates.append("Price = %s"); params.append(new_price)
    if new_stock_quantity is not None: updates.append("StockQuantity = %s"); params.append(new_stock_quantity)

    if not updates: return False # Should be caught by 'any' check above
    params.append(product_id)
    cursor = None
    try:
        cursor = conn.cursor()
        sql = f"UPDATE Products SET {', '.join(updates)} WHERE ProductID = %s"
        cursor.execute(sql, tuple(params))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"DB_Error updating Product ID {product_id}: {e}")
        if conn.is_connected(): conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def get_or_create_product(conn, product_name, description, category_id, price, stock_quantity, supplier_id=None, update_if_exists=False):
    """Gets product by name; creates if not found. Updates if found and update_if_exists is True. Returns ProductID or None."""
    if category_id is None:
        print(f"DB_Logic_Error: CategoryID missing for product '{product_name}'.")
        return None
    existing_product = get_product_by_name(conn, product_name)
    if existing_product:
        product_id = existing_product['ProductID']
        if update_if_exists:
            update_product_details(conn, product_id, new_price=price, new_stock_quantity=stock_quantity, new_description=description, new_category_id=category_id)
        return product_id
    return actual_add_product(conn, product_name, description, category_id, price, stock_quantity, supplier_id)

def fetch_products_with_category_names(conn, search_term=None, page=1, items_per_page=10):
    """Fetches paginated/searched products. Returns {'products': list, 'total_count': int}."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (fetch_products_with_category_names).")
        return {'products': [], 'total_count': 0}

    offset = (page - 1) * items_per_page
    products_on_page = []
    total_count = 0
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        base_sql_select = "SELECT p.ProductID, p.ProductName, p.Description, c.CategoryName, p.CategoryID, p.Price, p.StockQuantity "
        base_sql_from_join = "FROM Products p LEFT JOIN Categories c ON p.CategoryID = c.CategoryID "
        
        where_clauses = []
        params = []
        if search_term:
            where_clauses.append("p.ProductName LIKE %s")
            params.append(f"%{search_term}%")
        
        sql_where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        count_sql = f"SELECT COUNT(p.ProductID) as total FROM Products p {sql_where_clause}"
        cursor.execute(count_sql, tuple(params))
        total_count_result = cursor.fetchone()
        if total_count_result: total_count = total_count_result['total']

        paginated_params = list(params)
        paginated_params.extend([offset, items_per_page])
        products_sql = f"{base_sql_select} {base_sql_from_join} {sql_where_clause} ORDER BY p.ProductName LIMIT %s, %s"
        cursor.execute(products_sql, tuple(paginated_params))
        products_on_page = cursor.fetchall()
        
        return {'products': products_on_page, 'total_count': total_count}
    except Error as e:
        print(f"DB_Error fetching paginated products: {e}")
        return {'products': [], 'total_count': 0}
    finally:
        if cursor: cursor.close()

def delete_product(conn, product_id):
    """Deletes a product. Returns True on success, False otherwise."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (delete_product).")
        return False
    cursor = None
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM Products WHERE ProductID = %s"
        cursor.execute(sql, (product_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        if e.errno == 1451:
            print(f"DB_Error: Cannot delete Product ID {product_id}, referenced in sales records.")
        else:
            print(f"DB_Error deleting Product ID {product_id}: {e}")
        if conn.is_connected(): conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

# --- Customer Functions ---
def add_customer(conn, first_name, last_name=None, email=None, phone_number=None, address=None):
    """Adds a new customer. Returns new CustomerID or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (add_customer).")
        return None
    cursor = None
    try:
        cursor = conn.cursor()
        sql = """INSERT INTO Customers (FirstName, LastName, Email, PhoneNumber, Address)
                 VALUES (%s, %s, %s, %s, %s)"""
        val = (first_name, last_name, email, phone_number, address)
        cursor.execute(sql, val)
        conn.commit()
        return cursor.lastrowid
    except Error as e:
        if e.errno == 1062 and email:
            print(f"DB_Error: Customer with email '{email}' already exists.")
        else:
            print(f"DB_Error adding customer '{first_name} {last_name or ''}': {e}")
        if conn.is_connected(): conn.rollback()
        return None
    finally:
        if cursor: cursor.close()

def fetch_customers(conn):
    """Fetches all customers, ordered by name. Returns a list of dicts or an empty list."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (fetch_customers).")
        return []
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = "SELECT CustomerID, FirstName, LastName, Email, PhoneNumber, Address, RegistrationDate FROM Customers ORDER BY LastName, FirstName"
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f"DB_Error fetching customers: {e}")
        return []
    finally:
        if cursor: cursor.close()

def get_customer_by_id(conn, customer_id):
    """Fetches a customer by ID. Returns a dict or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (get_customer_by_id).")
        return None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = "SELECT CustomerID, FirstName, LastName, Email, PhoneNumber, Address, RegistrationDate FROM Customers WHERE CustomerID = %s"
        cursor.execute(sql, (customer_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"DB_Error fetching customer by ID '{customer_id}': {e}")
        return None
    finally:
        if cursor: cursor.close()

def update_customer(conn, customer_id, first_name, last_name=None, email=None, phone_number=None, address=None):
    """Updates an existing customer. Returns True on success, False otherwise."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (update_customer).")
        return False
    
    updates = []
    params = []
    if first_name is not None: updates.append("FirstName = %s"); params.append(first_name)
    # Allow clearing optional fields by passing empty string or handle None explicitly if needed by DB schema
    updates.append("LastName = %s"); params.append(last_name)
    updates.append("Email = %s"); params.append(email)
    updates.append("PhoneNumber = %s"); params.append(phone_number)
    updates.append("Address = %s"); params.append(address)
    
    # Filter out None assignments if DB fields don't accept None and you want to only update provided fields
    # Current logic updates all provided fields, potentially to NULL if None is passed and DB allows.

    if not updates or first_name is None: # Assuming first_name is essential for an update to proceed
        print(f"Insufficient details or missing FirstName for update, CustomerID: {customer_id}.")
        return False 

    params.append(customer_id)
    cursor = None
    try:
        cursor = conn.cursor()
        sql = f"UPDATE Customers SET {', '.join(updates)} WHERE CustomerID = %s"
        cursor.execute(sql, tuple(params))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        if e.errno == 1062 and email:
            print(f"DB_Error updating Customer ID {customer_id}: Email '{email}' already exists.")
        else:
            print(f"DB_Error updating Customer ID {customer_id}: {e}")
        if conn.is_connected(): conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def delete_customer(conn, customer_id):
    """Deletes a customer. Returns True on success, False otherwise."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (delete_customer).")
        return False
    cursor = None
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM Customers WHERE CustomerID = %s"
        cursor.execute(sql, (customer_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"DB_Error deleting Customer ID {customer_id}: {e}")
        if conn.is_connected(): conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

# --- Sales Processing Functions ---
def process_new_sale(conn, items_sold, customer_id=None, payment_method="Unknown"):
    """Processes a new sale. Returns SaleID on success, None otherwise.
       items_sold: [{'product_id': int, 'quantity': int, 'unit_price': float}, ...]
    """
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (process_new_sale).")
        return None
    if not items_sold:
        print("Sale_Logic_Error: No items provided for sale.")
        return None

    cursor = None
    original_autocommit_status = None
    try:
        cursor = conn.cursor(dictionary=True)
        original_autocommit_status = conn.autocommit
        conn.autocommit = False # Start transaction

        total_sale_amount = 0
        line_items_details = []

        for item in items_sold:
            product_id = item['product_id']
            quantity_sold = item['quantity']
            if quantity_sold <= 0:
                raise ValueError(f"Invalid quantity ({quantity_sold}) for Product ID {product_id}.")

            cursor.execute("SELECT ProductName, Price, StockQuantity FROM Products WHERE ProductID = %s FOR UPDATE", (product_id,))
            product = cursor.fetchone()

            if not product:
                raise ValueError(f"Product ID {product_id} not found.")
            if product['StockQuantity'] < quantity_sold:
                raise ValueError(f"Insufficient stock for Product '{product['ProductName']}' (ID {product_id}). Available: {product['StockQuantity']}, Requested: {quantity_sold}")

            unit_price_at_sale = item.get('unit_price', product['Price'])
            line_total = unit_price_at_sale * quantity_sold
            total_sale_amount += line_total
            
            line_items_details.append({
                'product_id': product_id, 'quantity': quantity_sold,
                'unit_price': unit_price_at_sale, 'total_price': line_total
            })

        sql_insert_sale = "INSERT INTO Sales (CustomerID, SaleDate, TotalAmount, PaymentMethod) VALUES (%s, NOW(), %s, %s)"
        cursor.execute(sql_insert_sale, (customer_id, total_sale_amount, payment_method))
        sale_id = cursor.lastrowid
        if not sale_id: raise Exception("Failed to create sale record in Sales table.")

        sql_insert_saledetail = "INSERT INTO SaleDetails (SaleID, ProductID, Quantity, UnitPrice, TotalPrice) VALUES (%s, %s, %s, %s, %s)"
        sql_update_stock = "UPDATE Products SET StockQuantity = StockQuantity - %s WHERE ProductID = %s"
        sql_log_inventory = "INSERT INTO InventoryLogs (ProductID, ChangeType, QuantityChange, Notes) VALUES (%s, %s, %s, %s)"

        for detail in line_items_details:
            cursor.execute(sql_insert_saledetail, (sale_id, detail['product_id'], detail['quantity'], detail['unit_price'], detail['total_price']))
            cursor.execute(sql_update_stock, (detail['quantity'], detail['product_id']))
            log_notes = f"Sale ID: {sale_id}"
            cursor.execute(sql_log_inventory, (detail['product_id'], 'Sale', -detail['quantity'], log_notes))


        conn.commit()
        print(f"Sale ID: {sale_id} processed successfully.")
        return sale_id
    except (Error, ValueError, Exception) as e:
        print(f"Error processing sale: {e}")
        if conn.is_connected(): conn.rollback()
        return None
    finally:
        if conn is not None and conn.is_connected() and original_autocommit_status is not None:
            conn.autocommit = original_autocommit_status
        if cursor: cursor.close()

# --- Sales Reporting Functions ---
def fetch_sales_history(conn):
    """Fetches sales history. Returns a list of dicts or an empty list."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (fetch_sales_history).")
        return []
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = """SELECT s.SaleID, s.SaleDate, s.TotalAmount, s.PaymentMethod, s.CustomerID,
                        c.FirstName AS CustomerFirstName, c.LastName AS CustomerLastName, c.Email AS CustomerEmail
                 FROM Sales s
                 LEFT JOIN Customers c ON s.CustomerID = c.CustomerID
                 ORDER BY s.SaleDate DESC"""
        cursor.execute(sql)
        return cursor.fetchall()
    except Error as e:
        print(f"DB_Error fetching sales history: {e}")
        return []
    finally:
        if cursor: cursor.close()

def fetch_sale_items(conn, sale_id):
    """Fetches items for a specific sale. Returns a list of dicts or an empty list."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (fetch_sale_items).")
        return []
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = """SELECT sd.ProductID, p.ProductName, sd.Quantity, sd.UnitPrice, sd.TotalPrice
                 FROM SaleDetails sd
                 JOIN Products p ON sd.ProductID = p.ProductID
                 WHERE sd.SaleID = %s
                 ORDER BY p.ProductName"""
        cursor.execute(sql, (sale_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"DB_Error fetching sale items for SaleID {sale_id}: {e}")
        return []
    finally:
        if cursor: cursor.close()

def get_sale_by_id(conn, sale_id):
    """Fetches a single sale by ID, including customer name. Returns a dict or None."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (get_sale_by_id).")
        return None
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = """SELECT s.SaleID, s.SaleDate, s.TotalAmount, s.PaymentMethod, s.CustomerID,
                        c.FirstName AS CustomerFirstName, c.LastName AS CustomerLastName, c.Email AS CustomerEmail
                 FROM Sales s
                 LEFT JOIN Customers c ON s.CustomerID = c.CustomerID
                 WHERE s.SaleID = %s"""
        cursor.execute(sql, (sale_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"DB_Error fetching sale by ID {sale_id}: {e}")
        return None
    finally:
        if cursor: cursor.close()

# --- Inventory/Dashboard Functions ---
def fetch_low_stock_products(conn, threshold=10):
    """Fetches products below a stock threshold. Returns a list of dicts or an empty list."""
    if not conn or not conn.is_connected():
        print("DB_Error: Connection not active (fetch_low_stock_products).")
        return []
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        sql = """SELECT p.ProductID, p.ProductName, p.StockQuantity, p.Price, c.CategoryName
                 FROM Products p
                 LEFT JOIN Categories c ON p.CategoryID = c.CategoryID
                 WHERE p.StockQuantity < %s
                 ORDER BY p.StockQuantity ASC, p.ProductName ASC"""
        cursor.execute(sql, (threshold,))
        return cursor.fetchall()
    except Error as e:
        print(f"DB_Error fetching low stock products: {e}")
        return []
    finally:
        if cursor: cursor.close()

def get_total_products_count(conn):
    """Gets total number of products. Returns int."""
    if not conn or not conn.is_connected(): return 0
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Products")
        count = cursor.fetchone()
        return count[0] if count else 0
    except Error as e:
        print(f"DB_Error getting total products count: {e}")
        return 0
    finally:
        if cursor: cursor.close()

def get_total_categories_count(conn):
    """Gets total number of categories. Returns int."""
    if not conn or not conn.is_connected(): return 0
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Categories")
        count = cursor.fetchone()
        return count[0] if count else 0
    except Error as e:
        print(f"DB_Error getting total categories count: {e}")
        return 0
    finally:
        if cursor: cursor.close()

def get_total_customers_count(conn):
    """Gets total number of customers. Returns int."""
    if not conn or not conn.is_connected(): return 0
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Customers")
        count = cursor.fetchone()
        return count[0] if count else 0
    except Error as e:
        print(f"DB_Error getting total customers count: {e}")
        return 0
    finally:
        if cursor: cursor.close()

def get_low_stock_items_count(conn, threshold=10):
    """Gets count of products below stock threshold. Returns int."""
    if not conn or not conn.is_connected(): return 0
    cursor = None
    try:
        cursor = conn.cursor()
        sql = "SELECT COUNT(*) FROM Products WHERE StockQuantity < %s"
        cursor.execute(sql, (threshold,))
        count = cursor.fetchone()
        return count[0] if count else 0
    except Error as e:
        print(f"DB_Error getting low stock items count: {e}")
        return 0
    finally:
        if cursor: cursor.close()


if __name__ == '__main__':
    print("Running database_operations.py directly (for testing or seeding)...")
    pass # Keeps the block valid if all tests are commented out