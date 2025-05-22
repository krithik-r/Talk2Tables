import sqlite3
import datetime

def create_database():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()

    # Create employees table with basic information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT,
        hire_date DATE NOT NULL,
        job_title TEXT NOT NULL,
        department TEXT NOT NULL,
        salary DECIMAL(10, 2) NOT NULL,
        manager_id INTEGER,
        management_level INTEGER DEFAULT 0,
        FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
    )
    ''')

    # Create employee_stats table with performance and leave information
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee_stats (
        employee_id INTEGER PRIMARY KEY,
        annual_leave_balance INTEGER DEFAULT 20,
        sick_leave_balance INTEGER DEFAULT 10,
        last_promotion_date DATE,
        performance_rating DECIMAL(3,2),
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
    )
    ''')

    # Insert sample data for employees table
    employee_data = [
        # C-Level (Level 3)
        (1, 'James', 'Wilson', 'james.wilson@company.com', '555-0101', '2018-01-15', 'CEO', 'Executive', 250000.00, None, 3),
        
        # Senior Management (Level 2)
        (2, 'Sarah', 'Chen', 'sarah.chen@company.com', '555-0102', '2018-06-20', 'CTO', 'Engineering', 180000.00, 1, 2),
        (3, 'Michael', 'Rodriguez', 'michael.r@company.com', '555-0103', '2019-03-10', 'CFO', 'Finance', 175000.00, 1, 2),
        
        # Middle Management (Level 1)
        (4, 'Jane', 'Smith', 'jane.smith@company.com', '555-0104', '2019-08-15', 'Engineering Manager', 'Engineering', 120000.00, 2, 1),
        (5, 'Robert', 'Taylor', 'robert.t@company.com', '555-0105', '2019-09-20', 'Finance Manager', 'Finance', 115000.00, 3, 1),
        
        # Regular Employees (Level 0)
        (6, 'John', 'Doe', 'john.doe@company.com', '555-0106', '2020-01-15', 'Senior Engineer', 'Engineering', 95000.00, 4, 0),
        (7, 'Alice', 'Williams', 'alice.w@company.com', '555-0107', '2020-04-28', 'Financial Analyst', 'Finance', 85000.00, 5, 0),
        (8, 'Bob', 'Johnson', 'bob.j@company.com', '555-0108', '2021-06-10', 'Software Engineer', 'Engineering', 80000.00, 4, 0),
        (9, 'Emma', 'Brown', 'emma.b@company.com', '555-0109', '2021-09-15', 'Junior Analyst', 'Finance', 70000.00, 5, 0),
        (10, 'David', 'Lee', 'david.l@company.com', '555-0110', '2022-01-10', 'Software Engineer', 'Engineering', 75000.00, 4, 0)
    ]

    # Insert sample data for employee_stats table
    stats_data = [
        (1, 25, 15, '2022-01-01', 4.8),
        (2, 22, 12, '2021-12-15', 4.7),
        (3, 20, 10, '2022-02-01', 4.6),
        (4, 18, 8, '2021-08-15', 4.5),
        (5, 15, 7, '2021-07-01', 4.3),
        (6, 12, 5, '2022-03-15', 4.2),
        (7, 15, 8, '2021-12-01', 4.0),
        (8, 20, 10, None, 3.8),
        (9, 20, 10, None, 3.7),
        (10, 20, 10, None, 3.9)
    ]

    # Clear existing data and insert new data
    cursor.execute('DROP TABLE IF EXISTS employee_stats')
    cursor.execute('DROP TABLE IF EXISTS employees')
    
    # Recreate tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        employee_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone_number TEXT,
        hire_date DATE NOT NULL,
        job_title TEXT NOT NULL,
        department TEXT NOT NULL,
        salary DECIMAL(10, 2) NOT NULL,
        manager_id INTEGER,
        management_level INTEGER DEFAULT 0,
        FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee_stats (
        employee_id INTEGER PRIMARY KEY,
        annual_leave_balance INTEGER DEFAULT 20,
        sick_leave_balance INTEGER DEFAULT 10,
        last_promotion_date DATE,
        performance_rating DECIMAL(3,2),
        FOREIGN KEY (employee_id) REFERENCES employees (employee_id)
    )
    ''')

    # Insert data into both tables
    cursor.executemany('''
    INSERT INTO employees (
        employee_id, first_name, last_name, email, phone_number, hire_date, 
        job_title, department, salary, manager_id, management_level
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', employee_data)

    cursor.executemany('''
    INSERT INTO employee_stats (
        employee_id, annual_leave_balance, sick_leave_balance, 
        last_promotion_date, performance_rating
    )
    VALUES (?, ?, ?, ?, ?)
    ''', stats_data)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_database()
    print("Database created successfully with two tables and sample data!") 