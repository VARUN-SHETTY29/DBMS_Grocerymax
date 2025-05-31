# app.py
from flask import Flask, render_template, request, redirect, url_for, g, flash
import database_operations
import datetime
import json
import math
import os # Import os
from dotenv import load_dotenv # If using .env file

load_dotenv() # Load environment variables from .env

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

if not app.secret_key:
    print("CRITICAL ERROR: FLASK_SECRET_KEY environment variable not set. Application will not run securely.")
    raise ValueError("No FLASK_SECRET_KEY set. Please set this environment variable.")

# --- Database Connection Management ---
def get_db():
    if 'db' not in g or g.db is None or not g.db.is_connected():
        g.db = database_operations.create_connection()
    if g.db is None: # If connection still failed
        print("CRITICAL: Failed to establish database connection in get_db.")
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None and db.is_connected():
        db.close()

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.datetime.now().year}

# --- Main Route ---
@app.route('/')
def index():
    conn = get_db()
    stats = {
        'total_products': 'N/A',
        'total_categories': 'N/A',
        'total_customers': 'N/A',
        'low_stock_items': 'N/A'
    }
    if conn:
        stats['total_products'] = database_operations.get_total_products_count(conn)
        stats['total_categories'] = database_operations.get_total_categories_count(conn)
        stats['total_customers'] = database_operations.get_total_customers_count(conn)
        stats['low_stock_items'] = database_operations.get_low_stock_items_count(conn, threshold=10)
    else:
        flash("Database connection error. Cannot load dashboard statistics.", "error")
    return render_template('index.html', title='Dashboard', stats=stats)

# --- Product Routes ---
@app.route('/products')
def show_products():
    conn = get_db()
    search_query = request.args.get('search_query', '').strip()
    try:
        page = int(request.args.get('page', 1))
        if page < 1: page = 1
    except ValueError:
        page = 1

    ITEMS_PER_PAGE = 10
    products_list = []
    total_matching_products = 0

    if not conn:
        flash("Database connection error. Could not fetch products.", "error")
    else:
        result = database_operations.fetch_products_with_category_names(
            conn,
            search_term=search_query if search_query else None,
            page=page,
            items_per_page=ITEMS_PER_PAGE
        )
        products_list = result['products']
        total_matching_products = result['total_count']

    total_pages = math.ceil(total_matching_products / ITEMS_PER_PAGE) if total_matching_products > 0 else 0
    if page > total_pages and total_pages > 0:
        page = total_pages # Adjust if current page is out of bounds

    return render_template('products.html',
                           title='Product Catalog',
                           products=products_list,
                           current_page=page,
                           total_pages=total_pages,
                           search_query=search_query)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product_route():
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        product_name = request.form.get('product_name')
        description = request.form.get('description', '')
        category_id_str = request.form.get('category_id')
        price_str = request.form.get('price')
        stock_quantity_str = request.form.get('stock_quantity')
        errors = []

        if not product_name: errors.append("Product name is required.")
        if not category_id_str: errors.append("Category is required.")
        if not price_str: errors.append("Price is required.")
        if not stock_quantity_str: errors.append("Stock quantity is required.")

        category_id_int, price_float, stock_quantity_int = None, None, None
        try:
            if category_id_str: category_id_int = int(category_id_str)
            if price_str: price_float = float(price_str)
            if stock_quantity_str: stock_quantity_int = int(stock_quantity_str)
        except ValueError:
            errors.append("Invalid number format for price, quantity, or category ID.")

        if errors:
            for error_msg in errors: flash(error_msg, "error")
            categories = database_operations.fetch_categories(conn)
            return render_template('add_product.html', title='Add New Product', categories=categories, form_data=request.form)

        product_id = database_operations.get_or_create_product(
            conn, product_name, description, category_id_int,
            price_float, stock_quantity_int, update_if_exists=True
        )

        if product_id:
            flash(f"Product '{product_name}' processed successfully.", "success")
            return redirect(url_for('show_products'))
        else:
            flash(f"Failed to process product '{product_name}'. It might already exist with a unique constraint issue or another database error occurred.", "error")
            categories = database_operations.fetch_categories(conn)
            return render_template('add_product.html', title='Add New Product', categories=categories, form_data=request.form)

    categories = database_operations.fetch_categories(conn)
    return render_template('add_product.html', title='Add New Product', categories=categories)

@app.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product_route(product_id):
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('show_products'))

    if request.method == 'POST':
        description = request.form.get('description', '')
        category_id_str = request.form.get('category_id')
        price_str = request.form.get('price')
        stock_quantity_str = request.form.get('stock_quantity')
        errors = []

        if not category_id_str: errors.append("Category is required.")
        if not price_str: errors.append("Price is required.")
        if not stock_quantity_str: errors.append("Stock quantity is required.")

        category_id_int, price_float, stock_quantity_int = None, None, None
        try:
            if category_id_str: category_id_int = int(category_id_str)
            if price_str: price_float = float(price_str)
            if stock_quantity_str: stock_quantity_int = int(stock_quantity_str)
        except ValueError:
            errors.append("Invalid number format for category, price, or quantity.")

        if errors:
            for error_msg in errors: flash(error_msg, "error")
            product_data_for_form = database_operations.get_product_by_id(conn, product_id) # Original data
            categories = database_operations.fetch_categories(conn)
             # For repopulating, merge original product_data with form values
            form_values = dict(request.form)
            form_values['ProductID'] = product_id # Ensure ID is available
            if product_data_for_form: # Keep original name if not submitted/changed
                 form_values['ProductName'] = product_data_for_form.get('ProductName')
            return render_template('edit_product.html', title='Edit Product', product=form_values, categories=categories)


        success = database_operations.update_product_details(
            conn, product_id,
            new_price=price_float, new_stock_quantity=stock_quantity_int,
            new_description=description, new_category_id=category_id_int
        )
        if success:
            flash(f"Product ID {product_id} updated successfully.", "success")
        else:
            flash(f"Failed to update Product ID {product_id}. Data might be unchanged or an error occurred.", "error")
        return redirect(url_for('show_products'))

    product_data = database_operations.get_product_by_id(conn, product_id)
    if not product_data:
        flash(f"Product with ID {product_id} not found.", "error")
        return redirect(url_for('show_products'))
    categories = database_operations.fetch_categories(conn)
    return render_template('edit_product.html', title='Edit Product', product=product_data, categories=categories)

@app.route('/products/delete/<int:product_id>', methods=['POST'])
def delete_product_route(product_id):
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('show_products'))
    success = database_operations.delete_product(conn, product_id)
    if success:
        flash(f"Product ID {product_id} deleted successfully.", "success")
    else:
        flash(f"Failed to delete Product ID {product_id}. It may be referenced in sales or no longer exist.", "error")
    return redirect(url_for('show_products'))

# --- Category Routes ---
@app.route('/categories')
def show_categories():
    conn = get_db()
    category_list = []
    if conn:
        category_list = database_operations.fetch_categories(conn)
    else:
        flash("Database connection error. Could not fetch categories.", "error")
    return render_template('categories.html', title='Manage Categories', categories=category_list)

@app.route('/categories/add', methods=['GET', 'POST'])
def add_category_route():
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('show_categories'))

    if request.method == 'POST':
        category_name = request.form.get('category_name')
        description = request.form.get('description', '')
        if not category_name:
            flash("Category name is required.", "error")
            return render_template('add_category.html', title='Add New Category', form_data=request.form)

        category_id = database_operations.add_category(conn, category_name, description)
        if category_id:
            flash(f"Category '{category_name}' added successfully.", "success")
            return redirect(url_for('show_categories'))
        else:
            flash(f"Failed to add category '{category_name}'. It might already exist or a database error occurred.", "error")
            return render_template('add_category.html', title='Add New Category', form_data=request.form)
    return render_template('add_category.html', title='Add New Category')

@app.route('/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category_route(category_id):
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('show_categories'))

    if request.method == 'POST':
        category_name = request.form.get('category_name')
        description = request.form.get('description', '')
        if not category_name:
            flash("Category name is required.", "error")
            # Pass back submitted data for repopulation
            return render_template('edit_category.html', title='Edit Category', category=request.form, category_id_for_url=category_id)


        success = database_operations.update_category(conn, category_id, category_name, description)
        if success:
            flash(f"Category '{category_name}' updated successfully.", "success")
            return redirect(url_for('show_categories'))
        else:
            flash(f"Failed to update category. The name '{category_name}' might already exist or a database error occurred.", "error")
            form_data_with_id = dict(request.form)
            form_data_with_id['CategoryID'] = category_id # Ensure ID is in the dict for the template
            return render_template('edit_category.html', title='Edit Category', category=form_data_with_id)


    category_data = database_operations.get_category_by_id(conn, category_id)
    if not category_data:
        flash(f"Category with ID {category_id} not found.", "error")
        return redirect(url_for('show_categories'))
    return render_template('edit_category.html', title='Edit Category', category=category_data)

@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category_route(category_id):
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('show_categories'))
    success = database_operations.delete_category(conn, category_id)
    if success:
        flash(f"Category ID {category_id} deleted successfully.", "success")
    else:
        flash(f"Failed to delete Category ID {category_id}. It might be in use by products or not exist.", "error")
    return redirect(url_for('show_categories'))

# --- Customer Routes ---
@app.route('/customers')
def show_customers():
    conn = get_db()
    customer_list = []
    if conn:
        customer_list = database_operations.fetch_customers(conn)
    else:
        flash("Database connection error. Could not fetch customers.", "error")
    return render_template('customers.html', title='Manage Customers', customers=customer_list)

@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer_route():
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('show_customers'))
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name', '')
        email = request.form.get('email', '')
        phone_number = request.form.get('phone_number', '')
        address = request.form.get('address', '')
        if not first_name:
            flash("First name is required.", "error")
            return render_template('add_customer.html', title='Add New Customer', form_data=request.form)

        customer_id = database_operations.add_customer(conn, first_name, last_name, email, phone_number, address)
        if customer_id:
            flash(f"Customer '{first_name} {last_name}' added successfully.", "success")
            return redirect(url_for('show_customers'))
        else:
            flash(f"Failed to add customer '{first_name} {last_name}'. Email might already exist or a database error occurred.", "error")
            return render_template('add_customer.html', title='Add New Customer', form_data=request.form)
    return render_template('add_customer.html', title='Add New Customer')

@app.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer_route(customer_id):
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('show_customers'))

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name', '')
        email = request.form.get('email', '')
        phone_number = request.form.get('phone_number', '')
        address = request.form.get('address', '')
        if not first_name:
            flash("First name is required.", "error")
            # Pass back submitted data for repopulation
            form_data_with_id = dict(request.form)
            form_data_with_id['CustomerID'] = customer_id
            return render_template('edit_customer.html', title='Edit Customer', customer=form_data_with_id)


        success = database_operations.update_customer(conn, customer_id, first_name, last_name, email, phone_number, address)
        if success:
            flash(f"Customer ID {customer_id} updated successfully.", "success")
            return redirect(url_for('show_customers'))
        else:
            flash(f"Failed to update Customer ID {customer_id}. Email might already exist or a database error occurred.", "error")
            form_data_with_id = dict(request.form)
            form_data_with_id['CustomerID'] = customer_id
            return render_template('edit_customer.html', title='Edit Customer', customer=form_data_with_id)

    customer_data = database_operations.get_customer_by_id(conn, customer_id)
    if not customer_data:
        flash(f"Customer ID {customer_id} not found.", "error")
        return redirect(url_for('show_customers'))
    return render_template('edit_customer.html', title='Edit Customer', customer=customer_data)

@app.route('/customers/delete/<int:customer_id>', methods=['POST'])
def delete_customer_route(customer_id):
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('show_customers'))
    success = database_operations.delete_customer(conn, customer_id)
    if success:
        flash(f"Customer ID {customer_id} deleted successfully. Associated sales records will have customer link removed.", "success")
    else:
        flash(f"Failed to delete Customer ID {customer_id}. A database error occurred.", "error")
    return redirect(url_for('show_customers'))

# --- Sales Routes ---
@app.route('/sales/new', methods=['GET', 'POST'])
def new_sale_route():
    conn = get_db()
    if not conn:
        flash("Database connection failed. Please try again later.", "error")
        return redirect(url_for('index'))

    if request.method == 'POST':
        cart_data_json = request.form.get('cart_data')
        customer_id_str = request.form.get('customer_id')
        payment_method = request.form.get('payment_method')

        if not cart_data_json:
            flash("Cart data is missing. Sale cannot be processed.", "error")
            return redirect(url_for('new_sale_route'))
        try:
            items_sold = json.loads(cart_data_json)
        except json.JSONDecodeError:
            flash("Invalid cart data format. Sale cannot be processed.", "error")
            return redirect(url_for('new_sale_route'))
        if not items_sold:
            flash("Cart is empty. Nothing to process.", "info")
            return redirect(url_for('new_sale_route'))

        customer_id = None
        if customer_id_str and customer_id_str.isdigit():
            customer_id = int(customer_id_str)
        elif customer_id_str: # Non-empty but not digit
             flash("Invalid customer ID format. Processing as guest sale.", "warning")

        sale_id = database_operations.process_new_sale(
            conn, items_sold=items_sold, customer_id=customer_id, payment_method=payment_method
        )
        if sale_id:
            flash(f"Sale successfully processed! Sale ID: {sale_id}", "success")
            return redirect(url_for('sales_history_route'))
        else:
            flash("Failed to process the sale. Stock might be insufficient, or a database error occurred. Please review cart and try again.", "error")
            return redirect(url_for('new_sale_route'))

    # GET request
    products_for_dropdown = []
    all_products_data = database_operations.fetch_products_with_category_names(conn, page=1, items_per_page=99999)
    if all_products_data and 'products' in all_products_data:
        products_for_dropdown = all_products_data['products']
    customers = database_operations.fetch_customers(conn)
    return render_template('new_sale.html',
                           title='New Sale / Point of Sale',
                           products=products_for_dropdown,
                           customers=customers)

@app.route('/sales/history')
def sales_history_route():
    conn = get_db()
    sales_records = []
    if conn:
        sales_records = database_operations.fetch_sales_history(conn)
    else:
        flash("Database connection error. Could not fetch sales history.", "error")
    return render_template('sales_history.html', title='Sales History', sales_records=sales_records)

@app.route('/sales/details/<int:sale_id>')
def sale_details_route(sale_id):
    conn = get_db()
    if not conn:
        flash("Database connection failed.", "error")
        return redirect(url_for('sales_history_route'))

    sale_main_info = database_operations.get_sale_by_id(conn, sale_id)
    sale_items = database_operations.fetch_sale_items(conn, sale_id)

    if not sale_main_info:
        flash(f"Sale with ID {sale_id} not found.", "error")
        return redirect(url_for('sales_history_route'))
    return render_template('sale_details.html',
                           title=f"Details for Sale ID: {sale_id}",
                           sale=sale_main_info,
                           items=sale_items)

# --- Inventory Report Route ---
@app.route('/inventory/low_stock')
def low_stock_report_route():
    conn = get_db()
    low_stock_items = []
    stock_threshold = 10 # Default threshold
    if conn:
        low_stock_items = database_operations.fetch_low_stock_products(conn, stock_threshold)
    else:
        flash("Database connection error. Could not fetch low stock report.", "error")
    return render_template('low_stock_report.html',
                           title=f"Low Stock Report (Below {stock_threshold} Units)",
                           items=low_stock_items,
                           threshold=stock_threshold)

if __name__ == '__main__':
    app.run(debug=True)