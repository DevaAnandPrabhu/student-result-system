import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # for session and flash

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'admin123':
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid Login Credentials", "danger")
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()
        conn.close()
        return render_template('dashboard.html', students=students)
    return redirect(url_for('home'))


@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form['name']
        reg_no = request.form['reg_no']
        dept = request.form['department']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO students (name, reg_no, department) VALUES (?, ?, ?)",
                    (name, reg_no, dept))
        conn.commit()
        conn.close()
        flash("Student Added Successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_student.html')

@app.route('/add-marks', methods=['GET', 'POST'])
def add_marks():
    if 'user' not in session:
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    # Fetch students for dropdown
    cur.execute("SELECT id, name, reg_no FROM students")
    students = cur.fetchall()

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject = request.form['subject']
        mark = request.form['mark']

        cur.execute("INSERT INTO marks (student_id, subject, mark) VALUES (?, ?, ?)",
                    (student_id, subject, mark))
        conn.commit()
        conn.close()

        flash("Mark added successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('add_marks.html', students=students)

@app.route('/view-result', methods=['GET', 'POST'])
def view_result():
    if request.method == 'POST':
        reg_no = request.form['reg_no']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        # Get student ID
        cur.execute("SELECT id, name, department FROM students WHERE reg_no = ?", (reg_no,))
        student = cur.fetchone()

        if student:
            student_id = student[0]
            name = student[1]
            dept = student[2]

            # Get marks
            cur.execute("SELECT subject, mark FROM marks WHERE student_id = ?", (student_id,))
            marks = cur.fetchall()

            return render_template('result.html', name=name, reg_no=reg_no, dept=dept, marks=marks)

        else:
            flash("Register number not found!", "danger")
            return redirect(url_for('view_result'))

    return render_template('view_result.html')

@app.route('/edit-student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'user' not in session:
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        reg_no = request.form['reg_no']
        dept = request.form['department']
        cur.execute("UPDATE students SET name=?, reg_no=?, department=? WHERE id=?",
                    (name, reg_no, dept, id))
        conn.commit()
        conn.close()
        flash("Student updated successfully!", "success")
        return redirect(url_for('dashboard'))

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()
    conn.close()
    return render_template('edit_student.html', student=student)


@app.route('/delete-student/<int:id>')
def delete_student(id):
    if 'user' not in session:
        return redirect(url_for('home'))

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Student deleted!", "info")
    return redirect(url_for('dashboard'))

@app.route('/student-login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        reg_no = request.form['reg_no']
        dob = request.form['dob']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE reg_no=? AND dob=?", (reg_no, dob))
        student = cur.fetchone()
        conn.close()

        if student:
            session['student_id'] = student[0]
            return redirect(url_for('student_result'))
        else:
            flash("Invalid Register No or DOB", "danger")
            return redirect(url_for('student_login'))

    return render_template('student_login.html')

@app.route('/student-result')
def student_result():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    student_id = session['student_id']
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT name, reg_no, department FROM students WHERE id=?", (student_id,))
    student = cur.fetchone()
    cur.execute("SELECT * FROM marks WHERE student_id=?", (student_id,))
    marks = cur.fetchall()
    conn.close()

    return render_template('student_result.html', student=student, marks=marks)



@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
