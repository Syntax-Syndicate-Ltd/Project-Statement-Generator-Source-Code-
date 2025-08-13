📄 **Project Statement Generator**

A Flask-based web application that helps users quickly generate professional project statements.
Includes authentication, project statement input, and formatted output.This project is powered by GROQ CLIENT API, and give AI analyzied responses. 


🚀 **Features**

> User Authentication — Register, log in, and securely manage your account.

> Project Statement Creation — Enter details like objectives, type, and timeline.

> Instant Results — Automatically generate and view your formatted project statement.

> Quick Print Button - Instantly print your statement 

> Database Storage — SQLite database to store user data and project statements.

> Responsive UI — HTML/CSS & Bootstrap, templates for a clean and mobile-friendly experience.


🛠️ **Tech Stack**

> Backend: Python, Flask, SQLAlchemy

> Frontend: HTML, CSS (Custom Styling), Bootstrap

> Database: SQLite

> Environment: .env for configuration

> Api : Groq API

> Authentication: Werkzeug security for password hashing


📂 **Project Structure**
```
.
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── instance/app.db         # SQLite database
├── static/css/style.css    # Styling
├── templates/              # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── result.html
└── Project-Statement-Generator/README.md  # Original README
```
⚙️ **Installation**

**1. Clone the repository**

```
git clone <your-repo-url>
cd (your_path_here)
```

**2.Create & activate a virtual environment**
```
python -m venv venv
source venv/bin/activate      # On Mac/Linux
venv\Scripts\activate         # On Windows
```

**3.Install dependencies**
```
pip install -r requirements.txt
```

**4.Set environment variables**

Create a .env file with:
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
GROQ_API_KEY=your-api-key
```
Follow these steps to get your API key:

Go to the official Groq Developer Portal:
👉 https://console.groq.com/keys

Sign up or log in with your account.

Navigate to the API Keys section.

Click "Create New API Key" and copy it.

Open your project folder and locate the .env file (create one if it doesn't exist).

Paste your key in the .env file like this:

```
GROQ_API_KEY=your-api-key-here
```
Save the file — you’re done! 🎉

⚠ Important:
Never share your API key publicly (e.g., on GitHub). Your .env file is already listed in .gitignore so it won’t be uploaded.
**5.Run the app**

```
python app.py
```


**📸 Screenshots**

Example Use :
<img width="1917" height="728" alt="image" src="https://github.com/user-attachments/assets/16e6bb3c-73e5-4c00-bddf-a34e4f738f96" />
<img width="1904" height="911" alt="image" src="https://github.com/user-attachments/assets/bb701abd-14bc-40f2-a1cd-f9878cc525ae" />
<img width="1897" height="908" alt="image" src="https://github.com/user-attachments/assets/649a3244-3a30-4899-8948-abec3586af1d" />



```
