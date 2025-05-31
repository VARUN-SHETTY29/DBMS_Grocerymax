User Manual: GroceryMax - Grocery Store Management System
1. Introduction
Welcome to the GroceryMax Grocery Store Management System! This manual provides step-by-step instructions on how to download, set up, and run the application on your local machine. GroceryMax is a web-based application designed to manage products, categories, customers, sales, and provide basic inventory reporting for a small to medium-sized grocery store.

2. Prerequisites / System Requirements
Before you begin, please ensure you have the following software installed on your system:

Python: Version 3.9 or higher.
Git: For cloning the project repository.
MySQL Server: Version 8.0 or a compatible version, installed and running.
Web Browser: A modern web browser such as Google Chrome, Mozilla Firefox, or Microsoft Edge.
Pip: Python package installer (usually comes with Python).
3. Step-by-Step Setup Instructions
Step 1: Download the Project from GitHub

Open your terminal or command prompt.
Navigate to the directory where you want to store the project.
Clone the main Webapps repository using Git:

git clone https://github.com/Nitin-4115/Webapps.git

Navigate into the cloned repository and then into the specific project folder:

cd Webapps/GroceryMax

All subsequent commands should be run from this Webapps/GroceryMax/ directory.
Step 2: Set Up a Python Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

Create a virtual environment (e.g., named venv):
    python -m venv venv
2. Activate the virtual environment: * **On Windows:**
.\venv\Scripts\activate
* **On macOS/Linux:**
source venv/bin/activate
```
Your command prompt should now indicate that you are in the (venv) environment.

Step 3: Install Dependencies

Install all the required Python packages listed in the requirements.txt file:

pip install -r requirements.txt

Step 4: MySQL Database and User Setup

Ensure MySQL Server is Running: Start your MySQL server if it's not already running.
Connect to MySQL: Open a MySQL client (e.g., MySQL command line, MySQL Workbench) and connect as a user with privileges to create databases and users (e.g., the root user):

mysql -u root -p
(Enter your MySQL root password when prompted).

Create the Database:

CREATE DATABASE IF NOT EXISTS grocery_store_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

Create the Application User and Grant Privileges: Replace 'DB_Password' with the same password you will specify in the .env file later if you choose a different one.

CREATE USER IF NOT EXISTS 'grocery_app_user'@'localhost' IDENTIFIED BY 'DB_Password';
GRANT ALL PRIVILEGES ON grocery_store_db.* TO 'grocery_app_user'@'localhost';
FLUSH PRIVILEGES;

Create Tables: Select the database and then run the table creation SQL commands.

USE grocery_store_db;

Now, execute the following CREATE TABLE statements (which are also detailed in Chapter 3.2 of the Project Report):

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

Exit the MySQL client:

EXIT;

Step 5: Configure Environment Variables

In the root of your GroceryMax project folder (where app.py is located), create a new file named .env.

Add the following content to the .env file, ensuring the database credentials match what you set up in MySQL:

Code snippet

DB_HOST="localhost"
DB_NAME="grocery_store_db"
DB_USER="grocery_app_user"
DB_PASSWORD="DB_Password"
FLASK_SECRET_KEY="secret_key" 
Important: Replace "secret_key" with a unique, long, and random string. This is crucial for Flask's session security. You can generate one using Python: import secrets; print(secrets.token_hex(24))
The .env file should not be committed to Git if your repository is public (ensure it's in your .gitignore file).
Step 6: Seed the Database (Initial Data)

To populate the database with some initial sample data (categories, products, etc.):

Ensure your virtual environment is still active.
Run the seed_db.py script from the GroceryMax project directory:
Bash

python seed_db.py
This script will connect to your database and add the predefined sample data.
Step 7: Run the Flask Application

Ensure your virtual environment is still active.
From the GroceryMax project directory, run the Flask application:
Bash

python app.py
You should see output indicating that the Flask development server is running, typically on http://127.0.0.1:5000/.
Open this URL in your web browser to access the GroceryMax application.
4. Using the Application (Brief Overview)
Once the application is running, you can use the navigation bar to access different sections:

Dashboard: View key statistics about the store.
Products: View, add, search, edit, and delete products. Use pagination to browse.
Categories: View, add, edit, and delete product categories.
Customers: View, add, edit, and delete customer records.
New Sale: Use the Point of Sale interface to add items to a cart, select a customer (optional), choose a payment method, and finalize sales. Stock levels will be updated automatically.
Reports:
Sales History: View a list of all sales. Click "View Items" for details on a specific sale.
Low Stock Report: See products that are running low on inventory.
Explore the different forms and tables to manage your grocery store data. Flash messages will provide feedback on actions (success or errors).