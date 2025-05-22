import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def check_query_relevance(user_input):
    """
    Check if the user input is relevant to the employee database using GPT-3.5
    """
    system_prompt = """You are a helpful assistant that determines if a user query is related to an employee database. 
    The database contains two tables:
    
    1. employees table with: employee_id, first_name, last_name, email, phone_number, 
    hire_date, job_title, department, salary, manager_id, management_level
    
    2. employee_stats table with: employee_id, annual_leave_balance, sick_leave_balance,
    last_promotion_date, performance_rating
    
    Respond with only 'YES' if the query is related to employee data, or 'NO' if it's not."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content.strip().upper() == 'YES'

def generate_sql_query(user_input):
    """
    Generate an SQL query based on the user input using GPT-3.5
    """
    system_prompt = """You are an SQL expert. Generate a SQL query for the following user request.
    The database has two tables:

    1. employees table:
    - employee_id (INTEGER PRIMARY KEY)
    - first_name (TEXT)
    - last_name (TEXT)
    - email (TEXT)
    - phone_number (TEXT)
    - hire_date (DATE)
    - job_title (TEXT)
    - department (TEXT)
    - salary (DECIMAL)
    - manager_id (INTEGER)
    - management_level (INTEGER)

    2. employee_stats table:
    - employee_id (INTEGER PRIMARY KEY) - References employees.employee_id
    - annual_leave_balance (INTEGER)
    - sick_leave_balance (INTEGER)
    - last_promotion_date (DATE)
    - performance_rating (DECIMAL)

 --                         Rules for SQL Query Generation
-- ----------------------------------------------------------------------------
-- These guidelines will help you choose the right patterns and syntax whenever  
-- you write queries against the `employees` and `employee_stats` tables (or  
-- any similar two-table schema). You can organize them under these broad areas:
-- ============================================================================

-- 1. BASIC VS. ENRICHED QUERIES
--    • **Simple lookups**  
--      When you only need core details (name, email, job_title, salary, hire_date),  
--        select directly from `employees`.  
--      Avoid joining to `employee_stats` unless you also need leave or performance data.  
--    • **Augmented results**  
--      As soon as you require annual_leave_balance, sick_leave_balance,  
--        last_promotion_date, or performance_rating, join in `employee_stats`.  
--      Choose your join type based on whether you need every employee or only those  
--        with stats (see “JOIN STRATEGIES” below).

-- 2. JOIN STRATEGIES
--    • **LEFT JOIN**  
--      Use LEFT JOIN when you want every row from `employees`, regardless of  
--        whether a matching row exists in `employee_stats`.  
--      Good for dashboards that show “all employees” and blank stats for new hires.  
--    • **INNER JOIN**  
--      Use INNER JOIN when you only care about employees who also have a stats record.  
--      Ideal for reports on “completed performance reviews” or leave balances.  
--    • **Other JOIN TYPES**  
--       RIGHT/FULL OUTER JOIN (simulate via UNION in SQLite) if you ever invert your master table.  
--       CROSS JOIN only for deliberate Cartesian products (rare here).

-- 3. FILTERING, SORTING & PAGING
--    • **WHERE**  
--       Narrow down to specific employees by `employee_id`, `department`, `manager_id`,  
--        `hire_date`, etc.  
--    • **HAVING**  
--       After aggregating (GROUP BY), use HAVING to filter grouped results—e.g.  
--        departments with AVG(salary) > 100000.  
--    • **ORDER BY**  
--       Rank or sort your results: `ORDER BY salary DESC`, `ORDER BY last_promotion_date ASC`.  
--    • **LIMIT / OFFSET**  
--       Page through large result sets or return “top N” records (e.g. top 5 performers).

-- 4. AGGREGATION & GROUPING
--    • **GROUP BY**  
--       Roll up by any categorical column: `department`, `manager_id`, `management_level`.  
--    • **Aggregate functions**  
--       COUNT( ), SUM( ), AVG( ), MAX( ), MIN( ) on salary, leave balances, performance_rating.  
--    • **DISTINCT**  
--       Deduplicate when necessary: COUNT(DISTINCT department), SELECT DISTINCT job_title.  

-- 5. CONDITIONAL LOGIC & NULL HANDLING
--    • **CASE … WHEN … THEN … ELSE … END**  
--      Bucket salaries into bands, translate ratings into “Meets Expectations” vs. “Exceeds.”  
--    • **COALESCE(column, default_value)**  
--      Provide a fallback for NULL leave balances or missing promotion dates.  
--    • **NULLIF / IFNULL**  
--      Convert empty strings to NULL, replace zeroes with NULL, etc.

-- 6. COMBINING DATASETS
--    • **Subqueries**  
--       Scalar subqueries in SELECT:  
--          `(SELECT AVG(salary) FROM employees WHERE department = e.department) AS dept_avg_salary`  
--       Correlated subqueries in WHERE:  
--          `WHERE salary > (SELECT AVG(salary) FROM employees WHERE department = e.department)`  
--    • **CTEs (WITH … AS)**  
--       Break complex logic into named steps:  
--          ```sql
--          WITH recent_hires AS (
--            SELECT * FROM employees WHERE hire_date > date('now','-1 year')
--          )
--          SELECT … FROM recent_hires r
--          LEFT JOIN employee_stats s ON r.employee_id = s.employee_id;
--          ```  
--    • **Views**  
--      Encapsulate recurring joins/filters in a `CREATE VIEW`.

-- 7. WINDOW FUNCTIONS
--    • Ranking: `ROW_NUMBER() OVER (PARTITION BY department ORDER BY performance_rating DESC)`  
--    • Running totals / moving averages:  
--         `AVG(salary) OVER (PARTITION BY department ORDER BY hire_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`  
--    • Lead/Lag comparisons:  
--         `LAG(performance_rating) OVER (PARTITION BY department ORDER BY last_promotion_date)`  

-- 8. PERFORMANCE & INDEXING
--    • **Indexes**  
--      Index foreign keys (`employee_id` in `employee_stats`), filter columns (`department`), join keys.  
--    • **EXPLAIN**  
--       Always validate your plan with `EXPLAIN QUERY PLAN` (SQLite) or DB-specific tools.  
--    • **Transactions**  
--      Wrap INSERT/UPDATE/DELETE sequences in `BEGIN … COMMIT/ROLLBACK` to maintain integrity.

-- 9. EXTENSIONS & VENDOR-SPECIFIC SYNTAX
--    • JSON functions if you ever store JSON in a text column.  
--    • Full-text search for notes or comments fields.  
--    • Materialized views, partitioning, advanced indexing—add only if your RDBMS supports them.

-- 10. GENERAL BEST PRACTICES
--    • **Explicit is better than implicit**: always name your columns, alias tables (`e`/`s`).  
--    • **Document intent**: comment non-obvious filters or calculations.  
--    • **Avoid SELECT ***: only return what the consumer actually needs.  
--    • **Parameterize** your queries in application code to prevent SQL injection.  
--    • **Consistent style**: pick snake_case or camelCase and stick with it.

-- ----------------------------------------------------------------------------
-- With these guidelines, you can construct anything from a simple
-- “list all engineers and their salaries” to a complex
-- “top 3 highest-performing, recently promoted managers by department
-- over the past 6 months”—confident that you’re following best practices 
-- for readability, correctness, and performance.

    Respond with ONLY the SQL query, nothing else."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )
    
    return response.choices[0].message.content.strip()

def execute_sql_query(query):
    """
    Execute the SQL query and return the results
    """
    conn = sqlite3.connect('employees.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        columns = [description[0] for description in cursor.description]
        results = cursor.fetchall()
        conn.close()
        return columns, results
    except Exception as e:
        conn.close()
        raise e

def generate_response(user_input, query_results):
    """
    Generate a natural language response based on the query results using GPT-3.5
    """
    columns, results = query_results
    results_str = f"Columns: {', '.join(columns)}\nResults: {results}"
    
    system_prompt = """You are a helpful assistant that generates natural language responses based on database query results.
    Provide a clear and concise response that answers the user's question using the query results.
    If the results show rankings or comparisons, explain them clearly.
    If the results are empty, explain why that might be the case."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Original question: {user_input}\n\nQuery results: {results_str}"}
        ]
    )
    
    return response.choices[0].message.content.strip()

def process_user_input(user_input):
    """
    Main function to process user input and return appropriate response
    """
    try:
        # Check if query is relevant to employee database
        if not check_query_relevance(user_input):
            return "This query appears to be unrelated to the employee database. Please ask a question about employee data."

        # Generate and execute SQL query
        sql_query = generate_sql_query(user_input)
        query_results = execute_sql_query(sql_query)
        
        # Generate natural language response
        final_response = generate_response(user_input, query_results)
        
        # Always show SQL query with response
        final_response = f"SQL Query:\n{sql_query}\n\nResponse:\n{final_response}"
            
        return final_response

    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    print("Welcome to the Employee Database Query System!")
    print("Type 'quit' to exit")
    print("\nWhat would you like to know about the employees?")
    
    while True:
        user_input = input("\nEnter your question: ")
        if user_input.lower() == 'quit':
            break
        
        response = process_user_input(user_input)
        print("\nResponse:", response) 