# DigiMenu - Digital Menu Sharing Platform

DigiMenu is a simple and elegant web application built with Flask that allows restaurant owners and vendors to create an account, upload their menu images, and instantly generate a shareable link and QR code. This provides a modern, contactless way for customers to view menus.

## ✨ Key Features

* **Vendor Authentication:** Secure registration and login system for vendors.
* **Easy Menu Uploads:** A simple interface for vendors to upload their menu images (JPG, PNG, GIF).
* **Instant Sharing:** Automatically generates a unique, permanent link for each uploaded menu.
* **QR Code Generation:** One-click QR code download for each menu, perfect for printing and placing in a physical location.
* **Clean Dashboard:** A user-friendly dashboard for vendors to manage all their uploaded menus.
* **Modern UI:** A beautiful and responsive interface built with Bootstrap 5.
* **Customizable Base URL:** Easily configure the application for your production domain using an environment file.

## 🚀 Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

You will need to have Python and `pip` installed on your system.

* [Python 3](https://www.python.org/downloads/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/AadityaJain0128/DigiMenu.git](https://github.com/AadityaJain0128/DigiMenu.git)
    cd DigiMenu
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You will need to create a `requirements.txt` file. See the "Technologies Used" section below for the contents.)*

### Project Structure

Your project directory should be set up as follows:

```
/DigiMenu
|-- app.py              # Main Flask application
|-- .env                # Environment variables (for production URL)
|-- requirements.txt    # Python dependencies
|-- /instance
|   |-- db.sqlite3      # SQLite database file (auto-generated)
|-- /uploads
|   |-- (menu images will be saved here)
|-- /templates
    |-- base.html
    |-- register.html
    |-- login.html
    |-- dashboard.html
    |-- menu.html
```

### Environment Variable Setup

1.  Create a file named `.env` in the root directory of the project.
2.  Add your production URL to this file. This will ensure that the generated links and QR codes point to your live domain instead of `localhost`.

    ```
    # .env file
    BASE_URL=[https://www.your-digimenu-domain.com](https://www.your-digimenu-domain.com)
    ```

### Running the Application

1.  Make sure you are in the project's root directory and your virtual environment is activated.
2.  Run the Flask application:
    ```bash
    python app.py
    ```
3.  Open your web browser and navigate to `http://127.0.0.1:5000`. You will be redirected to the registration page.

## 🛠️ Technologies Used

* **Backend:**
    * [Flask](https://flask.palletsprojects.com/): A lightweight WSGI web application framework.
    * [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/): Adds SQLAlchemy support to Flask.
    * [qrcode](https://pypi.org/project/qrcode/): For generating QR codes.
    * [python-dotenv](https://pypi.org/project/python-dotenv/): For managing environment variables.

* **Frontend:**
    * [Bootstrap 5](https://getbootstrap.com/): For styling and UI components.
    * [Bootstrap Icons](https://icons.getbootstrap.com/): For icons.
    * [Jinja2](https://jinja.palletsprojects.com/): The template engine for Flask.

---

### `requirements.txt` file content:

```
Flask
Flask-SQLAlchemy
Werkzeug
qrcode[pil]
python-dotenv
