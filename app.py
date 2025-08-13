import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
from groq import Groq
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            flash("You are already logged in.", "info")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
@app.route('/home')
@login_required
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
@logout_required
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("Please fill in all fields", "danger")
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "danger")
            return redirect(url_for('register'))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/', methods=['GET', 'POST'])
@logout_required
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for('login'))

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
    
    # Validate required fields
    if not all([project_type, domain, goals]):
        flash('Please fill in all required fields (Project Type, Domain, and Goals)', 'error')
        return redirect(url_for('index'))
    
    # Create prompt for Groq API
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
        # Generate project statement using Groq API
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an expert project manager with experience in creating detailed project statements."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2048
        )
        
        project_statement = response.choices[0].message.content
        
        return render_template('result.html', 
                              project_statement=project_statement,
                              form_data=request.form)
    
    except Exception as e:
        flash(f'Error generating project statement: {str(e)}', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=4000)
