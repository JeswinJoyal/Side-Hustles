# Good Picks (Product Website Prototype)

A foundational e-commerce store prototype inspired by platforms like Amazon and Flipkart, built as a summer side project. The project currently has the core foundation laid: a responsive mobile-friendly storefront UI, an admin dashboard with a product creation interface, a FastAPI backend, and a database layer with secure Argon2 admin authentication and session management.

> **Status:** Prototype / Foundation stage (Archived / Inactive).

---

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **Security & Auth:** Passlib (Argon2 hashing), Secrets (cryptographic session tokens)
- **Database:** MySQL (`mysql-connector-python`), python-dotenv (earlier PostgreSQL scripts in `sqlFunctions/`)
- **Frontend:** Vanilla HTML5, CSS3 (custom CSS variables & flex/grid layout), Vanilla JavaScript

---

## Directory Structure

```text
product website/
├── client_side/             # Frontend assets and views
│   ├── css/                 # Stylesheets (theme root, common, layout, admin)
│   ├── images/              # Media and asset placeholders
│   ├── js/                  # Client-side scripts (auth handling, form requests)
│   ├── index.html           # Storefront landing page
│   ├── profile.html         # User profile placeholder
│   ├── adminLogin.html      # Admin login portal
│   ├── adminDashboard.html  # Admin navigation hub
│   └── addProduct.html      # Product upload form
│
├── server_side/             # Backend application
│   ├── requestHandler.py    # FastAPI server, route handlers, static file mounting
│   └── sqlFunctions/        # Database models, schema creation & helper queries
│       ├── data.py          # MySQL operations (products, admins, sessions)
│       ├── create.py        # Schema setup reference
│       └── modify.py        # Database utility reference
│
├── .gitignore               # Ignored files (.env, __pycache__)
└── README.md                # Project documentation
```

---

## Implemented Features

### 1. Storefront Interface (`client_side/index.html`)
- **Responsive Layout:** Mobile-friendly container design with bottom navigation (Home, Products, Cart, Profile).
- **Search & Category Navigation:** Integrated search bar header with category filter subtabs (Explore, Women, Men, Kids, Home & Decor).
- **Product Card Component:** Responsive grid showcasing product thumbnails, title, pricing (₹), and "Add to Cart" action buttons.

### 2. Admin System & Security
- **Admin Authentication:**
  - Dedicated login interface (`/admin/login`).
  - Passwords hashed and verified using **Argon2** via `passlib`.
  - Secure session token generation (`secrets.token_urlsafe(32)`).
  - Session tracking table storing tokens, admin IDs, and expiration timestamps (default 30-minute validity).
  - Cleanup routine (`cleanup_user_sessions`) for purging expired tokens.
- **Admin Dashboard (`/admin`):**
  - Navigation hub with cards to add or manage products.
- **Product Entry Interface (`/admin/add-product`):**
  - Input form supporting product name, gender target (Men, Women, Unisex, Kids), category, subcategory, sub-subcategory, price, and image URL.

### 3. Database Layer (`server_side/sqlFunctions/data.py`)
- **Schema Management:** Automated table creation queries for `products`, `admins`, and `sessions`.
- **SQL Injection Safeguards:**
  - All SQL queries use parameterized queries (`%s`).
  - Product insertion enforces a strict field allow-list (`PRODUCT_FIELDS`) preventing rogue column injection.

---

## Current Status & Unimplemented Items

As development stopped after laying the foundation, several elements remain incomplete:
- **API Wiring:** The frontend form in `addProduct.html` sends a `POST /admin/add_product` request, but the matching endpoint in `requestHandler.py` has not yet been connected to `insert_product`.
- **Token Storage Consistency:** `adminLogin.js` stores tokens in `sessionStorage`, while `add-products.js` currently reads from `localStorage`.
- **Storefront Dynamic Data:** The homepage currently displays static placeholder cards rather than querying products from MySQL.
- **E-Commerce Workflows:** Cart functionality, checkout/payment flow, user registration, and product editing/deletion remain as placeholders.

---

## Running the Project

### Prerequisites
- Python 3.10+
- MySQL Server

### 1. Setup Environment
In `server_side/`, create a `.env` file with your database credentials:
```env
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=polyglot
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn mysql-connector-python passlib[argon2] python-dotenv pydantic
```

### 3. Initialize Database Tables
Run Python interactively or via script to create tables:
```python
from sqlFunctions.data import setup_database, setup_admin_database, setup_session_table
setup_database()
setup_admin_database()
setup_session_table()
```

### 4. Start Server
Run the FastAPI development server from within `server_side/`:
```bash
uvicorn requestHandler:app --reload --port 8000
```
- Storefront: `http://localhost:8000/`
- Admin Login: `http://localhost:8000/admin/login`
- Admin Dashboard: `http://localhost:8000/admin`