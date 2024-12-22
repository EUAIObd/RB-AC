# Access Control System for Small Organizations

## Project Overview

This project implements a web-based access control system designed for small organizations. The system is built using Python with the Flask framework and provides essential features for managing user access and security. It demonstrates best practices in web application development, including user authentication, role-based access control (RBAC), secure password handling, and user-friendly interface design.

## Key Features

*   **User Authentication:**
    *   Secure user login and logout.
    *   Password hashing using `Werkzeug` for secure storage.
*   **Role-Based Access Control (RBAC):**
    *   Two user roles: **Admin** (with further differentiation into Main Admin and Secondary Admin) and **Regular User**.
    *   Role-specific access to different parts of the application.
*   **User Management:**
    *   User registration with required fields (name, email, address, cellphone, password).
    *   Admin ability to list, view details of, and delete users.
*   **Admin Management (Main Admin Only):**
    *   Listing of secondary and main admins.
    *   Creation of new admins (with the option to make them main admins).
    *   Deletion of secondary admins.
*   **Profile Management:**
    *   Users can update their profile information (name, email, address, cellphone).
    *   Users can upload and change their profile pictures.
    *   Users and admins can change their passwords securely.
*   **Security:**
    *   Password hashing using `Werkzeug`.
    *   Strong password enforcement (minimum length, character type requirements).
    *   Password strength meter using `zxcvbn` to provide real-time feedback.
    *   Session management using Flask-Login.
    *   Cache-control headers to prevent caching of sensitive pages.
    *   Input validation on both client and server sides.
*   **Usability:**
    *   Minimalist and intuitive user interface design.
    *   "Show/Hide" password functionality for better user experience.
    *   "More Info" dropdown for viewing user details on the admin dashboard.
    *   Back navigation for ease of use.
    *   Error handling and informative error messages.

## Technology Stack

*   **Backend:** Python 3 with Flask web framework
*   **Database:** SQLite (for development/simplicity) with SQLAlchemy ORM
*   **Authentication:** Flask-Login
*   **Password Hashing:** Werkzeug
*   **Frontend:**
    *   HTML
    *   CSS (with Bootstrap 4.5.2 for styling)
    *   JavaScript (with zxcvbn for password strength and other interactive elements)
    *   Font Awesome for icons
*   **Development Tools:**
    *   `pip` for package management
    *   Virtual environment (recommended)

## System Architecture

The application follows a modular structure (similar to the Model-View-Controller pattern):

*   **`models.py`:** Defines the database schema using SQLAlchemy models (`User` and `Admin` tables).
*   **`routes.py` (or combined in `app.py`):** Contains the application logic, including route definitions, user authentication, authorization, and data manipulation.
*   **`templates/`:** Holds the HTML templates for the user interface.
*   **`static/`:** Stores static files like CSS, JavaScript, and images (including the default profile picture).
*   **`create_database_standalone.py` (optional):** A separate script to create the database and tables independently of the Flask app.

## Database Schema

**Table: `user`**

| Column        | Type         | Constraints            | Description                                                                   |
| ------------- | ------------ | ---------------------- | ----------------------------------------------------------------------------- |
| `id`          | `INTEGER`    | `PRIMARY KEY`          | Unique user ID.                                                              |
| `name`        | `VARCHAR(80)` | `NOT NULL`             | User's full name.                                                            |
| `email`       | `VARCHAR(120)` | `NOT NULL, UNIQUE`    | User's email address (used for login and must be unique).                    |
| `address`     | `VARCHAR(200)` |                        | User's address.                                                              |
| `cellphone`   | `VARCHAR(20)` |                        | User's cellphone number.                                                     |
| `profile_pic` | `VARCHAR(200)` | `DEFAULT 'defaultpic.png'` | Filepath to the user's profile picture (relative to the `static` folder). |
| `password`    | `VARCHAR(200)` | `NOT NULL`             | User's hashed password.                                                     |

**Table: `admin`**

| Column          | Type         | Constraints            | Description                                                                 |
| --------------- | ------------ | ---------------------- | --------------------------------------------------------------------------- |
| `id`            | `INTEGER`    | `PRIMARY KEY`          | Unique admin ID.                                                             |
| `name`          | `VARCHAR(80)` | `NOT NULL, UNIQUE`    | Admin's username (must be unique).                                           |
| `password`      | `VARCHAR(200)` | `NOT NULL`             | Admin's hashed password.                                                    |
| `is_main_admin` | `BOOLEAN`    | `DEFAULT FALSE`        | Indicates whether the admin is a main admin (`TRUE`) or secondary (`FALSE`). |

## Installation and Setup

1.  **Prerequisites:**
    *   Python 3.7 or higher
    *   `pip` (Python package installer)

2.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

3.  **Create a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    ```

4.  **Activate the Virtual Environment:**
    *   **Windows:**
        ```bash
        venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

5.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Create the Database:**
    *   **Option 1 (Using the standalone script):**
        ```bash
        python create_database_standalone.py
        ```
    *   **Option 2 (Creating the database within `app.py`):**
        *   Ensure you have the `create_database()` function in `app.py` and it's called before `app.run()`.
        *   Run `python app.py`.

7.  **Run the Application:**
    ```
    python app.py
    ```

8.  **Access the Application:**
    Open your web browser and go to `http://127.0.0.1:5000/`.

## Usage

Refer to the **User Manual** section in the project documentation for detailed instructions on how to use the different features of the application.

## Security Measures

*   **Password Hashing:** Passwords are never stored in plain text. They are hashed using the `generate_password_hash` function from `Werkzeug`.
*   **Strong Password Enforcement:** The system enforces strong password requirements during signup and password change.
*   **Password Strength Meter:** A password strength meter provides real-time feedback to users about the strength of their passwords.
*   **Role-Based Access Control (RBAC):** Access to different parts of the application is restricted based on user roles (admin or regular user).
*   **Session Management:** Flask-Login is used to manage user sessions securely.
*   **Cache Control:** `Cache-Control` headers are used to prevent browsers from caching sensitive pages.
*   **Input Validation:** User inputs are validated on both the client-side and server-side.
*   **Admin Account Security:** Special restrictions are placed on main admin accounts to prevent accidental deletion and unauthorized access.

## Key Features

### User Authentication

The system provides secure user login and logout functionality.

**Login:** Users can log in using their registered email address or username and password.

**Example:**

1.  Navigate to the login page (`/login`).
2.  Enter your email address in the "Username/Email" field.
3.  Enter your password in the "Password" field.
4.  Click the "Login" button.

**Password Hashing:** Upon registration or password change, user passwords are not stored in plain text. Instead, they are hashed using the `generate_password_hash` function from the `Werkzeug` library. This function implements strong, one-way hashing algorithms, making it computationally infeasible to retrieve the original password from the hash.

**Example Code (app.py):**

from werkzeug.security import generate_password_hash

# ...

hashed_password = generate_password_hash(password)
new_user = User(name=name, email=email, password=hashed_password, ...)

## Future Improvements

*   **Two-Factor Authentication (2FA)**
*   **Audit Logging**
*   **RESTful API**
*   **Advanced RBAC (more granular permissions)**
*   **Single Sign-On (SSO) Integration**
*   **Automated Database Backups**
*   **Rate Limiting**
*   **Security Audits and Penetration Testing**
*   **Frontend Framework (e.g., React, Vue, Angular)**

## Contributing

Contributions to this project are welcome. Please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Write clear and concise code with proper documentation.
4.  Test your changes thoroughly.
5.  Submit a pull request with a detailed description of your changes.

