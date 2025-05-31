# User Manual: GroceryMax - Grocery Store Management System

## 1. Introduction

Welcome to the GroceryMax Grocery Store Management System! This manual provides step-by-step instructions on how to download, set up, and run the application on your local machine. GroceryMax is a web-based application designed to manage products, categories, customers, sales, and provide basic inventory reporting for a small to medium-sized grocery store.

## 2. Prerequisites / System Requirements

Before you begin, please ensure you have the following software installed on your system:

* **Python:** Version 3.9 or higher.
* **Git:** For cloning the project repository.
* **MySQL Server:** Version 8.0 or a compatible version, installed and running.
* **Web Browser:** A modern web browser such as Google Chrome, Mozilla Firefox, or Microsoft Edge.
* **Pip:** Python package installer (usually comes with Python).

## 3. Step-by-Step Setup Instructions

### Step 1: Download the Project from GitHub

1.  Open your terminal or command prompt.
2.  Navigate to the directory where you want to store the project.
3.  Clone the main `Webapps` repository using Git:
    ```bash
    git clone [https://github.com/Nitin-4115/Webapps.git](https://github.com/Nitin-4115/Webapps.git)
    ```
4.  Navigate into the cloned repository and then into the specific project folder:
    ```bash
    cd Webapps/GroceryMax
    ```
    All subsequent commands should be run from this `Webapps/GroceryMax/` directory.

### Step 2: Set Up a Python Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

1.  Create a virtual environment (e.g., named `venv`):
    ```bash
    python -m venv venv
    ```
2.  Activate the virtual environment:
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    Your command prompt should now indicate that you are in the `(venv)` environment.

### Step 3: Install Dependencies

Install all the required Python packages listed in the `requirements.txt` file:
```bash
pip install -r requirements.txt

### Step 4: MySQL Database and User Setup

1.  **Ensure MySQL Server is Running:** Start your MySQL server if it's not already running.
2.  **Connect to MySQL:** Open a MySQL client (e.g., MySQL command line, MySQL Workbench) and connect as a user with privileges to create databases and users (e.g., the `root` user):
    ```bash
    mysql -u root -p
    ```
    (Enter your MySQL root password when prompted).
3.  **Create the Database:** Replace `your_database_name` with the name you want for your database (e.g., `grocery_store_db`).
    ```sql
    CREATE DATABASE IF NOT EXISTS your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ```
4.  **Create the Application User and Grant Privileges:** Replace `your_app_username` with a username for the application and `your_strong_password` with a secure password. Ensure `your_database_name` matches the one you created above.
    ```sql
    CREATE USER IF NOT EXISTS 'your_app_username'@'localhost' IDENTIFIED BY 'your_strong_password';
    GRANT ALL PRIVILEGES ON your_database_name.* TO 'your_app_username'@'localhost';
    FLUSH PRIVILEGES;
    ```
5.  **Create Tables:** Select the database and then run the table creation SQL commands.
    ```sql
    USE your_database_name;
    ```
    Now, execute the following `CREATE TABLE` statements:
    ```sql
    CREATE TABLE IF NOT EXISTS Categories (
        CategoryID INT PRIMARY KEY AUTO_INCREMENT,
        CategoryName VARCHAR(100) NOT NULL UNIQUE,
        Description TEXT
    );

    CREATE TABLE IF NOT EXISTS Suppliers (
        SupplierID INT PRIMARY KEY AUTO_INCREMENT,
        SupplierName VARCHAR(255) NOT NULL,
        ContactName VARCHAR(100),
        PhoneNumber VARCHAR(20),
        Email VARCHAR(255),
        Address TEXT
    );

    CREATE TABLE IF NOT EXISTS Products (
        ProductID INT PRIMARY KEY AUTO_INCREMENT,
        ProductName VARCHAR(255) NOT NULL UNIQUE,
        Description TEXT,
        CategoryID INT,
        Price DECIMAL(10, 2) NOT NULL,
        StockQuantity INT NOT NULL DEFAULT 0,
        SupplierID INT,
        DateAdded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID) ON DELETE SET NULL ON UPDATE CASCADE,
        FOREIGN KEY (SupplierID) REFERENCES Suppliers(SupplierID) ON DELETE SET NULL ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Customers (
        CustomerID INT PRIMARY KEY AUTO_INCREMENT,
        FirstName VARCHAR(100) NOT NULL,
        LastName VARCHAR(100),
        Email VARCHAR(255) UNIQUE,
        PhoneNumber VARCHAR(20),
        Address TEXT,
        RegistrationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS Sales (
        SaleID INT PRIMARY KEY AUTO_INCREMENT,
        CustomerID INT,
        SaleDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        TotalAmount DECIMAL(10, 2) NOT NULL,
        PaymentMethod VARCHAR(50),
        FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID) ON DELETE SET NULL ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS SaleDetails (
        SaleDetailID INT PRIMARY KEY AUTO_INCREMENT,
        SaleID INT NOT NULL,
        ProductID INT NOT NULL,
        Quantity INT NOT NULL,
        UnitPrice DECIMAL(10, 2) NOT NULL,
        TotalPrice DECIMAL(10, 2) NOT NULL,
        FOREIGN KEY (SaleID) REFERENCES Sales(SaleID) ON DELETE CASCADE ON UPDATE CASCADE,
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE RESTRICT ON UPDATE CASCADE
    );

    CREATE TABLE IF NOT EXISTS InventoryLogs (
        LogID INT PRIMARY KEY AUTO_INCREMENT,
        ProductID INT NOT NULL,
        ChangeDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ChangeType VARCHAR(50),
        QuantityChange INT NOT NULL,
        Notes TEXT,
        FOREIGN KEY (ProductID) REFERENCES Products(ProductID) ON DELETE CASCADE ON UPDATE CASCADE
    );
    ```
6.  Exit the MySQL client:
    ```sql
    EXIT;
    ```

### Step 5: Configure Environment Variables

1.  In the root of your `GroceryMax` project folder (where `app.py` is located), create a new file named `.env`.
2.  Add the following content to the `.env` file. **Replace the placeholder values** with the actual database name, username, and password you configured in Step 4. Also, generate a strong, unique `FLASK_SECRET_KEY`.

    ```env
    DB_HOST="localhost"
    DB_NAME="your_database_name"
    DB_USER="your_app_username"
    DB_PASSWORD="your_strong_password"
    FLASK_SECRET_KEY="generate_a_very_strong_random_secret_key_here"
    ```
    * **Important:** To generate a strong `FLASK_SECRET_KEY`, you can run the following in a Python interpreter:
        ```python
        import secrets
        print(secrets.token_hex(24))
        ```
        Copy the output and use it as your `FLASK_SECRET_KEY`.
    * The `.env` file should **not** be committed to Git if your repository is public (ensure it's listed in your `.gitignore` file).

### Step 6: Seed the Database (Initial Data)

To populate the database with some initial sample data (categories, products, etc.):

1.  Ensure your virtual environment is still active.
2.  Run the `seed_db.py` script from the `GroceryMax` project directory:
    ```bash
    python seed_db.py
    ```
    This script will connect to your database using the credentials from the `.env` file and add the predefined sample data. You should see messages in your console indicating the progress of the seeding process.

### Step 7: Run the Flask Application

1.  Ensure your virtual environment is still active.
2.  From the `GroceryMax` project directory, run the Flask application:
    ```bash
    python app.py
    ```
3.  You should see output indicating that the Flask development server is running, typically on `http://127.0.0.1:5000/`. The output will look something like this:
    ```
     * Serving Flask app 'app'
     * Debug mode: on
    WARNING: This is a development server. Do not use it in a production deployment.
    Use a production WSGI server instead.
     * Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)
    Press CTRL+C to quit
    ```
4.  Open this URL (`http://127.0.0.1:5000/`) in your web browser to access the GroceryMax application.

## 4. Using the Application (Brief Overview)

Once the "GroceryMax" application is successfully running and accessible in your web browser, you can interact with its various features using the navigation bar and on-page controls.

* **Dashboard:** Upon logging in (or on the main page, if no authentication is implemented), you will see the Dashboard. This page provides a quick overview of key store statistics like total products, categories, customers, and items that are low on stock. It may also feature quick action buttons to common tasks.

* **Navigation Bar:** Located at the top of each page, the navigation bar allows you to easily switch between different modules of the application:
    * **Products:** Click here to view, add, search, edit, and delete products. The product list supports pagination if there are many items.
    * **Categories:** Manage product categories. You can view existing categories, add new ones, edit their details, or delete them.
    * **Customers:** Access the customer management section to view, add, edit, or delete customer records.
    * **New Sale:** This takes you to the Point of Sale (POS) interface.
    * **Reports:** This dropdown menu provides access to:
        * **Sales History:** View a chronological list of all sales transactions.
        * **Low Stock Report:** See a list of products that are running low on inventory based on a predefined threshold.

* **Managing Items (Products, Categories, Customers):**
    * **Viewing Lists:** Each management page (Products, Categories, Customers) will display a table of existing items.
    * **Adding New Items:** Look for an "Add New [Product/Category/Customer]" button, which will take you to a form to enter the details.
    * **Editing Items:** In the item lists, there will be an "Edit" option (button or link) next to each item, allowing you to modify its details.
    * **Deleting Items:** An option to "Delete" items will also be available in the lists. You will usually be asked for confirmation before an item is permanently removed. (Note: Deleting categories or customers might have implications for associated products or sales, as defined by database constraints).

* **Processing a New Sale (POS Interface):**
    1.  Navigate to the "New Sale" page.
    2.  **Select Products:** Use the product dropdown to find and select items.
    3.  **Enter Quantity:** Specify the quantity for the selected product.
    4.  **Add to Cart:** Click the "Add to Cart" button. The item will appear in the "Current Sale Items" list, and the total will update. Client-side validation will check for available stock.
    5.  **Manage Cart:** You can add multiple products or remove items from the cart if needed.
    6.  **Select Customer (Optional):** Choose a registered customer from the dropdown or leave it as "Guest Sale."
    7.  **Choose Payment Method:** Select the method of payment.
    8.  **Finalize Sale:** Click the "Finalize Sale" button. The system will process the sale, update stock levels, and record the transaction.

* **Viewing Reports:**
    * **Sales History:** Access this report to see all sales. Click on "View Items" (or a similar link) next to a sale to see the specific products, quantities, and prices for that transaction.
    * **Low Stock Report:** This report lists all products whose current stock quantity is below the set threshold, helping you identify items that need reordering.

* **Feedback Messages:** The application uses flash messages (usually appearing at the top of the page) to provide feedback on your actions, such as "Product added successfully" or "Error: Category name is required."

Explore the different sections to familiarize yourself with all the functionalities of the GroceryMax system.