import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
import sqlite3
import os
os.remove('exam_scores.db')

###################
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

# cursor.executemany('INSERT INTO scores (experience, salary) VALUES (?, ?)',
#                     [(2, 300000), (3, 400000), (4, 500000), (5, 600000), (6, 700000), (7, 800000),
#                      (8, 900000), (9, 1000000), (10, 1100000), (11, 1200000), (12, 1300000)])

# cursor.executemany('INSERT INTO scores (experience, salary) VALUES (?, ?)',
#                     [(2, 400000), (3, 600000), (4, 800000), (5, 1000000), (6, 1200000), (7, 1400000),
#                      (8, 1600000), (9, 1800000), (10, 2000000), (11, 2200000), (12, 2400000)])

cursor.executemany('INSERT INTO scores (experience, salary) VALUES (?, ?)',
                    [(2, 500000), (3, 700000), (4, 900000), (5, 1100000), (6, 1300000), (7, 1500000),
                     (8, 1700000), (9, 1900000), (10, 2100000), (11, 2300000), (12, 2500000)])

conn.commit()
conn.close()

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

print(exp, sal)
########################################

# Data
hours_studied = exp
test_scores = sal



# Create a scatter plot
plt.scatter(hours_studied, test_scores)
plt.xlabel('Hours Studied')
plt.ylabel('Test Score')
plt.title('Hours Studied vs. Test Score')
plt.show()


# Reshape data for scikit-learn
X = np.array(hours_studied).reshape(-1, 1)
Y = np.array(test_scores)

# Create and fit the linear regression model
model = LinearRegression()
model.fit(X, Y)

# Get the intercept (a) and slope (b)
intercept = model.intercept_
slope = model.coef_[0]

print(f"Intercept (a): {intercept}")
print(f"Slope (b): {slope}")


# Predict the test score for 12 hours of study
new_prediction_for_year = 20
predicted_score = model.predict([[new_prediction_for_year]])
print(f"Predicted salary for {new_prediction_for_year} years of experience: {predicted_score[0]}")


# Plot the scatter plot
plt.scatter(hours_studied, test_scores)

# Plot the regression line
regression_line = intercept + slope * np.array(hours_studied)
plt.plot(hours_studied, regression_line, color='red', linestyle='--', label='Regression Line')

plt.xlabel('years of exp')
plt.ylabel('salary')
plt.title('exp vs salary')
plt.legend()
plt.show()
