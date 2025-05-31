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