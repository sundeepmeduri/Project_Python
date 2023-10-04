from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# Create the SQLite database and table
conn = sqlite3.connect('exam_scores.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        experience REAL,
        salary REAL
    )
''')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        new_hours = float(request.form['new_hours'])

        # Predict the exam score for the new hour using the linear regression model
        model = reload_model()
        predicted_score = model.predict([[new_hours]])

        return render_template('index.html', prediction=predicted_score[0], new_hours=new_hours)

    return redirect(url_for('index'))

@app.route('/data_entry', methods=['GET', 'POST'])
def data_entry():
    if request.method == 'POST':
        experience = float(request.form['experience'])
        salary = float(request.form['salary'])

        # Connect to the database
        conn = sqlite3.connect('exam_scores.db')
        cursor = conn.cursor()

        # Insert the new data into the table
        cursor.execute('INSERT INTO scores (experience, salary) VALUES (?, ?)',
                       (experience, salary))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('data_entry.html')

@app.route('/edit_data/<int:id>', methods=['GET', 'POST'])
def edit_data(id):
    if request.method == 'POST':
        experience = float(request.form['experience'])
        salary = float(request.form['salary'])

        # Connect to the database
        conn = sqlite3.connect('exam_scores.db')
        cursor = conn.cursor()

        # Update the data in the table
        cursor.execute('UPDATE scores SET experience=?, salary=? WHERE id=?',
                       (experience, salary, id))

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    # Fetch the existing data for editing
    conn = sqlite3.connect('exam_scores.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scores WHERE id=?', (id,))
    data = cursor.fetchone()
    conn.close()

    return render_template('edit_data.html', data=data)

@app.route('/view_all')
def view_all():
    # Fetch all data from the database
    conn = sqlite3.connect('exam_scores.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scores')
    data = cursor.fetchall()
    conn.close()
    return render_template('view_all.html', data=data)

# ... (rest of the code)


def reload_model():
    conn = sqlite3.connect('exam_scores.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM scores')
    data = cursor.fetchall()
    conn.close()
    exp = []
    sal = []
    for i in data:
        exp.append(i[1])
        sal.append(i[2])
    X = np.array(exp).reshape(-1, 1)
    Y = np.array(sal)
    model = LinearRegression()
    model.fit(X, Y)
    return model


if __name__ == '__main__':
    app.run(debug=True)
