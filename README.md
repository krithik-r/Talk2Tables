# Talk2Tables
Talk2Tables is a lightweight, LLM-powered natural language interface for querying structured databases using plain English. Built for developers and analysts, this project translates user questions into optimized SQL queries, executes them, and returns clear, human-readable summaries. This system allows you to query an employee database using natural language. It uses GPT-3.5 to interpret your questions, generate appropriate SQL queries, and provide natural language responses.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. Initialize the database with sample data:
```bash
python setup_database.py
```

## Usage

1. Run the main script:
```bash
python main.py
```

2. Enter your questions about employees when prompted. The system will:
   - Check if your question is relevant to the employee database
   - Generate and execute an appropriate SQL query
   - Provide a natural language response

3. Special commands:
   - Type 'show sql' to display the SQL queries being executed
   - Type 'hide sql' to hide the SQL queries
   - Type 'quit' to exit the program

## Example Questions

### Simple Queries (Single Table)
- "Who are all the employees in the Engineering department?"
- "What is the email address of the employee with the highest salary?"
- "List all employees hired in 2021"
- "Who are the C-level executives?"
- "Show me all employees who report to Sarah Chen"

### Complex Queries (Using Joins)
- "Who has the most sick leave days?"
- "Show me employees with high performance ratings but haven't been promoted"
- "What is the average performance rating by department?"
- "List all employees with their leave balances and performance ratings"
- "Who has the highest performance rating in each department?"
- "Show me employees who have used more than 15 days of annual leave"
- "Which employees have been promoted in the last year and what are their current performance ratings?"
- "What is the correlation between salary and performance rating?"
- "Show me the leave balances for all employees in the Finance department"
- "Who are the top 3 performers in terms of both performance rating and salary?"

## Database Schema

The database consists of two related tables:

### 1. employees
Contains basic employee information:
- employee_id (INTEGER PRIMARY KEY)
- first_name (TEXT)
- last_name (TEXT)
- email (TEXT)
- phone_number (TEXT)
- hire_date (DATE)
- job_title (TEXT)
- department (TEXT)
- salary (DECIMAL)
- manager_id (INTEGER) - References employee_id in the same table
- management_level (INTEGER) - 0: Regular, 1: Middle Management, 2: Senior Management, 3: C-Level

### 2. employee_stats
Contains performance and leave information:
- employee_id (INTEGER PRIMARY KEY) - References employees.employee_id
- annual_leave_balance (INTEGER)
- sick_leave_balance (INTEGER)
- last_promotion_date (DATE)
- performance_rating (DECIMAL) - Scale of 0.00 to 5.00

The tables are linked through the employee_id field, allowing for complex queries using JOIN operations to combine employee information with their performance and leave statistics. The system automatically determines whether to use:
- Simple queries for basic employee information
- INNER JOIN when matching records from both tables are required
- LEFT JOIN when all employees should be included regardless of stats
- Appropriate aggregation functions (COUNT, AVG, MAX, MIN) for statistical analysis
- ORDER BY for ranking and sorting
- GROUP BY for department-wise or category-wise analysis

## Customizing the Database

### Adding More Tables
To add more tables to the database:

1. Modify `setup_database.py` to include new table creation:
```python
def create_database():
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()

    # Create new table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY,
        field1 TEXT,
        field2 INTEGER,
        FOREIGN KEY (id) REFERENCES employees (employee_id)
    )
    ''')
```

2. Update the system prompts in `main.py` to include the new table structure:
```python
system_prompt = """... existing tables ...
3. new_table:
- id (INTEGER PRIMARY KEY)
- field1 (TEXT)
- field2 (INTEGER)
"""
```

### Connecting to an Existing Database
To use an existing SQLite database:

1. Copy your database file to the project directory
2. Update the connection in `main.py`:
```python
def execute_sql_query(query):
    conn = sqlite3.connect('your_existing_database.db')
    # ... rest of the function
```

### Using Data Dictionaries
To create a new database from data dictionaries:

1. Create a Python dictionary with your data:
```python
data_dict = {
    'table1': [
        {'id': 1, 'name': 'John'},
        {'id': 2, 'name': 'Jane'}
    ],
    'table2': [
        {'id': 1, 'value': 100},
        {'id': 2, 'value': 200}
    ]
}
```

2. Modify `setup_database.py` to use the dictionary:
```python
def create_database_from_dict(data_dict):
    conn = sqlite3.connect('new_database.db')
    cursor = conn.cursor()
    
    for table_name, records in data_dict.items():
        # Create table based on dictionary keys
        columns = list(records[0].keys())
        create_table_sql = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(f'{col} TEXT' for col in columns)}
        )
        '''
        cursor.execute(create_table_sql)
        
        # Insert data
        for record in records:
            placeholders = ', '.join(['?' for _ in record])
            insert_sql = f'''
            INSERT INTO {table_name} ({', '.join(columns)})
            VALUES ({placeholders})
            '''
            cursor.execute(insert_sql, list(record.values()))
    
    conn.commit()
    conn.close()
```

### Importing Data from Files
To import data from CSV, Excel, or other files:

1. Add required dependencies to `requirements.txt`:
```
pandas
openpyxl  # for Excel files
```

2. Create a data import function:
```python
import pandas as pd

def import_data_from_file(file_path, table_name):
    # Read file based on extension
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(file_path)
    
    # Connect to database
    conn = sqlite3.connect('employees.db')
    
    # Import data
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    conn.close()
```

## Adapting for Different Use Cases

To adapt the system for different use cases (e.g., hospital, bank, school):

1. Update the database schema in `setup_database.py` to match your use case
2. Modify the system prompts in `main.py`:

```python
# For a hospital system
system_prompt = """You are an SQL expert. Generate a SQL query for the following user request.
The database has these tables:

1. patients:
- patient_id (INTEGER PRIMARY KEY)
- first_name (TEXT)
- last_name (TEXT)
- date_of_birth (DATE)
- gender (TEXT)
- contact_number (TEXT)

2. medical_records:
- record_id (INTEGER PRIMARY KEY)
- patient_id (INTEGER)
- diagnosis (TEXT)
- treatment (TEXT)
- admission_date (DATE)
- discharge_date (DATE)
- doctor_id (INTEGER)

3. doctors:
- doctor_id (INTEGER PRIMARY KEY)
- first_name (TEXT)
- last_name (TEXT)
- specialization (TEXT)
- department (TEXT)
"""

# For a school system
system_prompt = """You are an SQL expert. Generate a SQL query for the following user request.
The database has these tables:

1. students:
- student_id (INTEGER PRIMARY KEY)
- first_name (TEXT)
- last_name (TEXT)
- grade_level (INTEGER)
- enrollment_date (DATE)

2. courses:
- course_id (INTEGER PRIMARY KEY)
- course_name (TEXT)
- teacher_id (INTEGER)
- credits (INTEGER)

3. grades:
- grade_id (INTEGER PRIMARY KEY)
- student_id (INTEGER)
- course_id (INTEGER)
- grade_value (DECIMAL)
- semester (TEXT)
"""
```

3. Update the example questions in the README to match your use case
4. Modify the response generation to use domain-specific language

Remember to:
- Update all foreign key relationships
- Adjust the data types to match your needs
- Modify the example queries to be relevant to your domain
- Update the natural language processing to understand domain-specific terminology 

## System Test Results and Interpretation

The system has been thoroughly tested using `test_system.py`. Here are the latest test results and their interpretation:

### Component-wise Performance

1. **Query Relevance (87.50%)**
   - Passed: 7/8 tests
   - Interpretation: Good - System is performing well with minor issues
   - The system correctly identifies relevant queries most of the time, with room for improvement in edge cases

2. **SQL Generation (100.00%)**
   - Passed: 3/3 tests
   - Interpretation: Excellent - System is performing very well
   - The system consistently generates correct SQL queries for various types of requests

3. **Query Execution (100.00%)**
   - Passed: 1/1 tests
   - Interpretation: Excellent - System is performing very well
   - All SQL queries execute successfully and return expected results

4. **Response Generation (100.00%)**
   - Passed: 1/1 tests
   - Interpretation: Excellent - System is performing very well
   - The system effectively formats and presents query results to users

5. **Data Integrity (66.67%)**
   - Passed: 2/3 tests
   - Interpretation: Poor - System needs significant improvements
   - Areas for improvement in data validation and constraint enforcement

### Overall System Performance
- **Overall Accuracy: 87.50%**
- **Interpretation**: The system is reliable but could benefit from some improvements
- **Recommendations**:
  1. Focus on improving data integrity checks
  2. Enhance query relevance detection for edge cases
  3. Add more comprehensive test cases for data validation

### Running Tests
To run the test suite and see the latest results:
```bash
python test_system.py
```

The test suite verifies:
- Database structure and relationships
- Query processing capabilities
- Data integrity and constraints
- Response generation
- Error handling 
