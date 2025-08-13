# Import OS module to interact with the operating system
# (used for reading environment variables and generating random data)
import os

# Import dotenv's function to load environment variables from a .env file
from dotenv import load_dotenv

# Import core Flask tools for building web apps
from flask import Flask, render_template, request, redirect, url_for, flash, session

# Import Groq API client to interact with the LLM model
from groq import Groq

# Import SQLAlchemy for ORM (Object Relational Mapping) with Flask
from flask_sqlalchemy import SQLAlchemy

# Import secure password hashing & verification methods
from werkzeug.security import generate_password_hash, check_password_hash

# Import wraps to preserve function metadata when creating decorators
from functools import wraps


# Load environment variables from the .env file into the program
load_dotenv()

# Create a new Flask application instance
app = Flask(__name__)

# Generate a random secret key for sessions (stored in memory during runtime)
app.secret_key = os.urandom(24)

# Configure the SQLite database path (local database file named app.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  

# Disable SQLAlchemy's change tracking feature for performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the database object linked to our Flask app
db = SQLAlchemy(app)

# Initialize Groq client with API key from environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ---------------------- AUTHENTICATION HELPERS ----------------------

# Decorator to ensure a route requires the user to be logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:  # If user is not logged in
            flash("Please log in to continue.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)  # If logged in, run the original function
    return decorated_function

# Decorator to ensure logged-in users can't access certain routes (like login/register)
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:  # If user is already logged in
            flash("You are already logged in.", "info")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------- DATABASE MODEL ----------------------

# User model for storing login credentials in the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique user ID
    username = db.Column(db.String(100), unique=True, nullable=False)  # Username (must be unique)
    password_hash = db.Column(db.String(200), nullable=False)  # Hashed password

    # Method to hash and store password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Method to verify if a password matches the stored hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    

# ---------------------- ROUTES ----------------------

# Home page - accessible only when logged in
@app.route('/home')
@login_required
def index():
    return render_template('index.html')


# Registration page
@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    if request.method == 'POST':
        # Get form input values
        username = request.form['username']
        password = request.form['password']

        # Check for empty fields
        if not username or not password:
            flash("Please fill in all fields", "danger")
            return redirect(url_for('register'))

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('register'))

        # Create and store new user
        new_user = User(username=username)
        new_user.set_password(password)  # Store hashed password
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    # Show registration form for GET request
    return render_template('register.html')


# Login page
@app.route('/', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':
        # Get form input values
        username = request.form['username']
        password = request.form['password']

        # Search for user in database
        user = User.query.filter_by(username=username).first()

        # Check if user exists and password is correct
        if user and user.check_password(password):
            # Store login session details
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for('login'))

    # Show login form for GET request
    return render_template('login.html')


# Logout route
@app.route('/logout')
@login_required
def logout():
    session.clear()  # Remove all session data
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))


# Generate project statement using Groq API
@app.route('/generate', methods=['POST'])
@login_required
def generate():
    # Get form data
    project_type = request.form.get('project_type')
    domain = request.form.get('domain')
    goals = request.form.get('goals')
    audience = request.form.get('audience')
    timeline = request.form.get('timeline')
    budget = request.form.get('budget')
    constraints = request.form.get('constraints')
    
    # Check if required fields are filled
    if not all([project_type, domain, goals]):
        flash('Please fill in all required fields (Project Type, Domain, and Goals)', 'error')
        return redirect(url_for('index'))
    
    # Prompt to send to Groq AI for generating project statement
    prompt = f"""
You are an expert project strategist.

Here are the initial project details provided (context only — do not simply restate):
Project Type: {project_type}
Domain: {domain}
Goals: {goals}
Target Audience: {audience if audience else 'Not specified'}
Timeline: {timeline if timeline else 'Not specified'}
Budget: {budget if budget else 'Not specified'}
Constraints: {constraints if constraints else 'None specified'}

Your task:
1. Invent new and creative project ideas, opportunities, and directions that build on these details.
2. Suggest approaches the user might not have considered yet.
3. Incorporate innovative methods, technologies, and strategies.
4. Highlight unique ways to network, collaborate, or reach the audience.
5. Keep the tone professional but inspiring.
6. The statement should be professional statement like question statement.

Output the final result in **pure HTML** with the following structure and tags:

<h2>Project Statement</h2>
<p>...</p>

<h2>Objectives (This is all about guidance, not the part of statement)</h2>
<ul><li>...</li></ul>

<h2>Scope</h2>
<ul><li>...</li></ul>

<h2>Deliverables</h2>
<ul><li>...</li></ul>

<h2>Success Metrics</h2>
<ul><li>...</li></ul>

<h2>Tech Stack</h2>
<ul><li>...</li></ul>

<h2>Tech Approach</h2>
<ul><li>...</li></ul>

<h2>Potential Challenges</h2>
<ul><li>...</li></ul>

<h2>Recommended Approach</h2>
<ul><li>...</li></ul>

Rules:
- You have to generate a solid problem statement and the it should be professional statement containing statement also with tech stack.
- Do not repeat the original text exactly.
- Do not include any introduction or explanation outside the HTML tags.
- Every section must contain **original suggestions and ideas** that expand beyond the given details.
"""
    
    try:
        # Send request to Groq API to generate project statement
        response = client.chat.completions.create(
            model="llama3-70b-8192",  # Groq model to use
            messages=[
                {"role": "system", "content": "You are an expert project manager with experience in creating detailed project statements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Controls creativity
            max_tokens=2048   # Maximum length of response
        )
        
        # Extract generated content from response
        project_statement = response.choices[0].message.content
        
        # Render the result page with generated statement and form data
        return render_template('result.html', 
                              project_statement=project_statement,
                              form_data=request.form)
    
    except Exception as e:
        # Handle any API errors
        flash(f'Error generating project statement: {str(e)}', 'error')
        return redirect(url_for('index'))


# ---------------------- MAIN ENTRY POINT ----------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure database and tables are created
    app.run(host="0.0.0.0", port=4000)  # Start Flask server on port 4000
