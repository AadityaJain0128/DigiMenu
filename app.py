import os
import secrets
import qrcode
import io
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- App Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# --- Create Uploads Directory ---
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# --- Database Models ---
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    restaurant_name = db.Column(db.String(120), nullable=False)
    menus = db.relationship('Menu', backref='vendor', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'), nullable=False)
    image_filename = db.Column(db.String(120), nullable=False)
    unique_slug = db.Column(db.String(20), unique=True, nullable=False)

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/')
def index():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        # ... (rest of the function is unchanged)
        username = request.form['username']
        password = request.form['password']
        restaurant_name = request.form['restaurant_name']

        existing_vendor = Vendor.query.filter_by(username=username).first()
        if existing_vendor:
            flash('Username already exists. Please choose a different one.', 'error')
            return redirect(url_for('register'))

        new_vendor = Vendor(username=username, restaurant_name=restaurant_name)
        new_vendor.set_password(password)
        db.session.add(new_vendor)
        db.session.commit()

        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'vendor_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # ... (rest of the function is unchanged)
        username = request.form['username']
        password = request.form['password']
        vendor = Vendor.query.filter_by(username=username).first()

        if vendor and vendor.check_password(password):
            session['vendor_id'] = vendor.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('vendor_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'vendor_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))

    vendor = Vendor.query.get(session['vendor_id'])
    menus = Menu.query.filter_by(vendor_id=vendor.id).all()
    # Get base_url from environment variable, with a fallback for local development
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
    return render_template("dashboard.html", vendor=vendor, menus=menus, base_url=base_url)

@app.route('/upload', methods=['POST'])
def upload_menu():
    # ... (function is unchanged)
    if 'vendor_id' not in session:
        return redirect(url_for('login'))

    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('dashboard'))
    
    file = request.files['file']

    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('dashboard'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = secrets.token_hex(8) + "_" + filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        
        slug = secrets.token_hex(6)
        new_menu = Menu(
            vendor_id=session['vendor_id'], 
            image_filename=unique_filename,
            unique_slug=slug
        )
        db.session.add(new_menu)
        db.session.commit()
        flash('Menu uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Please upload an image.', 'error')

    return redirect(url_for('dashboard'))


@app.route('/menu/<slug>')
def view_menu(slug):
    menu = Menu.query.filter_by(unique_slug=slug).first_or_404()
    return render_template("menu.html", menu=menu)

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_menu/<int:menu_id>', methods=['POST'])
def delete_menu(menu_id):
    # ... (function is unchanged)
    if 'vendor_id' not in session:
        flash('Please log in.', 'error')
        return redirect(url_for('login'))

    menu = Menu.query.get_or_404(menu_id)

    if menu.vendor_id != session['vendor_id']:
        flash('You do not have permission to delete this menu.', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], menu.image_filename))
    except OSError as e:
        print(f"Error deleting file {menu.image_filename}: {e}")
        flash('Error deleting menu file from server.', 'error')

    db.session.delete(menu)
    db.session.commit()
    
    flash('Menu deleted successfully.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/qr/<slug>')
def qr_code(slug):
    """Generates a QR code for the menu link using the BASE_URL."""
    # Use the BASE_URL from .env file, with a fallback to the current request's host URL
    base_url = os.getenv('BASE_URL', request.host_url.rstrip('/'))
    menu_url = f"{base_url}{url_for('view_menu', slug=slug)}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(menu_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
