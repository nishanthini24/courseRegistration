from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from database_setup import students_collection, admin_collection


from werkzeug.security import generate_password_hash, check_password_hash
import csv
import os

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/course_registration'
app.config['SECRET_KEY'] = 'your_secret_key'
mongo = PyMongo(app)

# Admin Login
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = mongo.db.admins.find_one({'username': username})

        if admin and check_password_hash(admin['password'], password):
            session['admin'] = username  # Store admin session
            return redirect(url_for('dashboard'))  # Redirect to dashboard
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

# Admin Logout
@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))

# Student Registration Form (Restrict Multiple Registrations)

           
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        gender = request.form['gender']
        course = request.form['course']

        # Check if the same course has already been registered by the email
        existing = students_collection.find_one({"email": email, "course": course})
        if existing:
            flash("This email has already registered for the selected course.", "error")
            return redirect(url_for('register'))

        # Otherwise, allow registration
        student = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "dob": dob,
            "gender": gender,
            "course": course
        }
        students_collection.insert_one(student)
        flash("Registration successful!", "success")
        return redirect(url_for('register'))

    return render_template('register.html')


# Admin Dashboard (View Students)
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    students = mongo.db.students.find()
    return render_template('dashboard.html', students=students)

# Delete Student
@app.route('/delete/<student_id>')
def delete_student(student_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    mongo.db.students.delete_one({'_id': ObjectId(student_id)})
    
    return redirect(url_for('dashboard'))

# Edit Student
@app.route('/edit/<student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    
    student = mongo.db.students.find_one({'_id': ObjectId(student_id)})

    if request.method == 'POST':
        updated_data = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': request.form['email'],
            'phone': request.form['phone'],
            'dob': request.form['dob'],
            'gender': request.form['gender'],
            'course': request.form['course']
        }
        mongo.db.students.update_one({'_id': ObjectId(student_id)}, {'$set': updated_data})
        
        return redirect(url_for('dashboard'))

    return render_template('edit_student.html', student=student)

# Download Report (Fixing the URL Error)
@app.route('/download_report')
def download_report():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    students = mongo.db.students.find()
    
    # Create a CSV file
    csv_file = "student_report.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["First Name", "Last Name", "Email", "Phone", "DOB", "Gender", "Course"])
        
        for student in students:
            writer.writerow([student["first_name"], student["last_name"], student["email"],
                             student["phone"], student["dob"], student["gender"], student["course"]])

    return send_file(csv_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
