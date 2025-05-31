# GroceryMax - Web-Based Grocery Store Management System

GroceryMax is a comprehensive web application designed to manage the core operations of a small to medium-sized grocery store. It provides functionalities for inventory control, sales processing, customer data management, and essential reporting, all through an intuitive web-based interface.

This project was developed as a [mention your context, e.g., college project for XYZ course].

## Key Features

* **Dashboard:** At-a-glance overview of key store statistics (total products, categories, customers, low stock items).
* **Product Management:**
    * Add, view, edit, and delete products.
    * Search products by name.
    * Paginated product listings for easy Browse.
    * Track product name, description, category, price, and stock quantity.
* **Category Management:**
    * Add, view, edit, and delete product categories.
* **Customer Management:**
    * Add, view, edit, and delete customer records.
    * Store customer contact details and addresses.
* **Sales Processing (Point of Sale - POS):**
    * Interactive interface to add products to a cart.
    * Client-side cart management with real-time quantity and stock validation.
    * Option to associate sales with registered customers or process as guest sales.
    * Selection of payment methods.
    * Backend processing with atomic stock updates and detailed sales recording.
* **Reporting:**
    * **Sales History:** View a list of all sales transactions.
    * **Sale Details:** Drill down to see individual items sold in each transaction.
    * **Low Stock Report:** Identify products with stock levels below a predefined threshold.

## Technologies Used

* **Backend:**
    * Python 3.9+
    * Flask (Web Micro-framework)
    * MySQL (Relational Database)
    * `mysql-connector-python` (MySQL driver for Python)
* **Frontend:**
    * HTML5
    * Tailwind CSS (v3.x via Play CDN for styling)
    * Jinja2 (Templating engine for Flask)
    * JavaScript (ES6+ for client-side interactivity, e.g., POS cart)
* **Development Environment & Tools:**
    * Python Virtual Environment (`venv`)
    * Git (Version Control)
    * `python-dotenv` (for managing environment variables)

## Setup and Installation

Follow these steps to set up and run the GroceryMax application locally:

**1. Prerequisites:**
    * Python 3.9 or higher installed.
    * MySQL Server installed and running.
    * Git installed (for cloning).

**2. Clone the Repository (if you haven't already for the parent `Webapps` repo):**
   If you've cloned the parent `Webapps` repository, navigate into it. This project resides in the `GroceryMax` subfolder.
   ```bash
   git clone [https://github.com/Nitin-4115/Webapps.git](https://github.com/Nitin-4115/Webapps.git)
   cd Webapps/GroceryMax