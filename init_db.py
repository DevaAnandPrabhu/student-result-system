import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Students table
c.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    reg_no TEXT UNIQUE NOT NULL,
    department TEXT NOT NULL
)
''')

# Marks table
c.execute('''
CREATE TABLE IF NOT EXISTS marks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    subject TEXT,
    mark INTEGER,
    FOREIGN KEY(student_id) REFERENCES students(id)
)
''')

conn.commit()
conn.close()

print("✅ Database and tables created successfully!")
