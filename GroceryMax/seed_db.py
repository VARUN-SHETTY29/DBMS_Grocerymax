# seed_db.py
import database_operations as db_ops # Assuming database_operations.py is in the same directory

def seed_data():
    """Connects to the DB and seeds it with initial data."""
    print("Attempting to seed database...")
    conn = db_ops.create_connection()

    if not conn or not conn.is_connected():
        print("Failed to connect to the database. Seeding aborted.")
        return

    try:
        # --- Seed Categories ---
        print("\n--- Seeding Categories ---")
        cat_fruits_id = db_ops.get_or_create_category(conn, "Fruits", "Fresh and juicy fruits")
        cat_veg_id = db_ops.get_or_create_category(conn, "Vegetables", "Farm fresh vegetables")
        cat_dairy_id = db_ops.get_or_create_category(conn, "Dairy", "Milk, cheese, yogurt, etc.")
        cat_bakery_id = db_ops.get_or_create_category(conn, "Bakery", "Freshly baked goods")
        cat_beverages_id = db_ops.get_or_create_category(conn, "Beverages", "Drinks and refreshments")
        cat_snacks_id = db_ops.get_or_create_category(conn, "Snacks", "Chips, nuts, and other munchies")
        # Add more categories as needed

        print("\n--- Seeding Products ---")
        # Ensure category IDs are valid (i.e., the get_or_create_category calls above were successful)

        if cat_fruits_id:
            db_ops.get_or_create_product(conn, "Organic Apples", "Crisp Fuji variety, sold per piece", cat_fruits_id, 0.75, 150, update_if_exists=True)
            db_ops.get_or_create_product(conn, "Bananas", "Bunch of 5, ripe", cat_fruits_id, 1.99, 200, update_if_exists=True)
            db_ops.get_or_create_product(conn, "Blueberries", "Fresh organic blueberries, 1 pint", cat_fruits_id, 4.99, 60, update_if_exists=True)
        
        if cat_veg_id:
            db_ops.get_or_create_product(conn, "Carrots", "1lb bag, organic", cat_veg_id, 1.29, 100, update_if_exists=True)
            db_ops.get_or_create_product(conn, "Broccoli", "Fresh crown, approx 1lb", cat_veg_id, 2.49, 75, update_if_exists=True)

        if cat_dairy_id:
            db_ops.get_or_create_product(conn, "Whole Milk", "1 Gallon, Vitamin D", cat_dairy_id, 3.99, 50, update_if_exists=True)
            db_ops.get_or_create_product(conn, "Cheddar Cheese", "8oz block, sharp", cat_dairy_id, 4.79, 40, update_if_exists=True)

        if cat_bakery_id:
            db_ops.get_or_create_product(conn, "Sourdough Bread", "Artisan loaf, unsliced", cat_bakery_id, 5.50, 30, update_if_exists=True)

        if cat_beverages_id:
            db_ops.get_or_create_product(conn, "Orange Juice", "Not from concentrate, 52 fl oz", cat_beverages_id, 4.25, 80, update_if_exists=True)

        if cat_snacks_id:
            db_ops.get_or_create_product(conn, "Potato Chips", "Classic salted, 9oz bag", cat_snacks_id, 3.19, 120, update_if_exists=True)
            db_ops.get_or_create_product(conn, "Almonds", "Roasted, unsalted, 1lb bag", cat_snacks_id, 7.99, 60, update_if_exists=True)
        
        # Add more products as needed

        print("\n--- Seeding Customers (Optional) ---")
        db_ops.add_customer(conn, "John", "Doe", "john.doe@example.com", "555-0101", "123 Main St, Anytown")
        db_ops.add_customer(conn, "Jane", "Smith", "jane.smith@example.com", "555-0102", "456 Oak Ave, Anytown")
        # Add more customers if you like

        print("\n--- Seeding completed successfully! ---")

    except Exception as e:
        print(f"An error occurred during seeding: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed after seeding.")

if __name__ == '__main__':
    # This makes the script executable
    seed_data()