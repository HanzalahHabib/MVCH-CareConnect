import mysql.connector
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder='templates')
app.secret_key = 'awp_ak47'

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "caamodel@1",  
    "database": "hospital_db"
}
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route("/submit", methods=["POST"])
def submit():
    connection = None
    cursor = None
    try:
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        skills = request.form["skills"]

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        query = "INSERT INTO volunteers (name, email, phone, skills) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, email, phone, skills))
        connection.commit()
        return redirect("/thankyou")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "An error occurred while saving your data."
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route("/voluneer-welcome")
def welcome():
    return render_template("welcome.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    print(f"Received Username: '{username}', Password: '{password}'") 

    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    user = cursor.fetchone()

    if user:
        print(f"User found: {user['username']}, Role: '{user['role']}'")
        if user['password'] == password:
            session['user_id'] = user['id']
            session['role'] = user['role']
            print(f"Login successful. Role: {user['role']}")  
            if user['role'] == 'doctor':
                return redirect('/doctor-dashboard')
            elif user['role'] == 'nurse':
                return redirect('/nurse-dashboard')
            else:
                print(f"Invalid role found: '{user['role']}'") 
                return "Role not found", 401
        else:
            print("Incorrect password") 
            return "Invalid credentials", 401  
    else:
        print("User not found") 
        return "Invalid credentials", 401 


@app.route('/doctor-dashboard')
def doctor_dashboard():
    if session.get('role') != 'doctor':
        return "Unauthorized", 403

    doctor_id = session['user_id']
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM appointments WHERE doctor_id = %s"
    cursor.execute(query, (doctor_id,))
    appointments = cursor.fetchall()

    if not appointments:
        return render_template('doctor_dashboard.html', message="No appointments available")
    
    return render_template('doctor_dashboard.html', appointments=appointments)

@app.route('/nurse-dashboard')
def nurse_dashboard():
    if session.get('role') != 'nurse':
        return "Unauthorized", 403

    nurse_id = session['user_id']
    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM ward_info WHERE nurse_id = %s"
    cursor.execute(query, (nurse_id,))
    wards = cursor.fetchall()

    if not wards:
        return render_template('nurse_dashboard.html', message="No wards available")

    return render_template('nurse_dashboard.html', wards=wards)

@app.route('/volunteer-form')
def volunteer_form():
    return render_template('form.html')

if __name__ == '__main__':
    app.run(debug=True)
