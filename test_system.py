import unittest
import sqlite3
import os
from main import check_query_relevance, generate_sql_query, execute_sql_query, generate_response
from setup_database import create_database

class TestEmployeeDatabaseSystem(unittest.TestCase):
    # Class variable to store test results
    test_results = {
        'query_relevance': {'passed': 0, 'total': 0},
        'sql_generation': {'passed': 0, 'total': 0},
        'query_execution': {'passed': 0, 'total': 0},
        'response_generation': {'passed': 0, 'total': 0},
        'data_integrity': {'passed': 0, 'total': 0}
    }

    @classmethod
    def setUpClass(cls):
        """Set up test database before running tests"""
        # Create a test database
        create_database()
        
    def setUp(self):
        """Set up test environment before each test"""
        self.conn = sqlite3.connect('employees.db')
        self.cursor = self.conn.cursor()

    def tearDown(self):
        """Clean up after each test"""
        self.conn.close()

    @classmethod
    def calculate_accuracy(cls):
        """Calculate and print accuracy scores for each component"""
        print("\n=== System Accuracy Report ===")
        total_passed = 0
        total_tests = 0
        
        for component, results in cls.test_results.items():
            accuracy = (results['passed'] / results['total']) * 100 if results['total'] > 0 else 0
            print(f"\n{component.replace('_', ' ').title()}:")
            print(f"Accuracy: {accuracy:.2f}%")
            print(f"Passed: {results['passed']}/{results['total']} tests")
            
            # Interpretation
            if accuracy >= 90:
                interpretation = "Excellent - System is performing very well"
            elif accuracy >= 80:
                interpretation = "Good - System is performing well with minor issues"
            elif accuracy >= 70:
                interpretation = "Fair - System needs some improvements"
            else:
                interpretation = "Poor - System needs significant improvements"
            print(f"Interpretation: {interpretation}")
            
            total_passed += results['passed']
            total_tests += results['total']
        
        overall_accuracy = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        print(f"\nOverall System Accuracy: {overall_accuracy:.2f}%")
        
        # Overall interpretation
        if overall_accuracy >= 90:
            overall_interpretation = "The system is highly reliable and ready for production use"
        elif overall_accuracy >= 80:
            overall_interpretation = "The system is reliable but could benefit from some improvements"
        elif overall_accuracy >= 70:
            overall_interpretation = "The system needs significant improvements before production use"
        else:
            overall_interpretation = "The system requires major improvements and should not be used in production"
        print(f"Overall Interpretation: {overall_interpretation}")

    def test_database_structure(self):
        """Test if database tables are created correctly"""
        self.__class__.test_results['data_integrity']['total'] += 1
        try:
            # Check if tables exist
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in self.cursor.fetchall()]
            self.assertIn('employees', tables)
            self.assertIn('employee_stats', tables)

            # Check employees table structure
            self.cursor.execute("PRAGMA table_info(employees)")
            employee_columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            self.assertIn('employee_id', employee_columns)
            self.assertIn('first_name', employee_columns)
            self.assertIn('last_name', employee_columns)
            self.assertIn('email', employee_columns)
            self.assertIn('salary', employee_columns)

            # Check employee_stats table structure
            self.cursor.execute("PRAGMA table_info(employee_stats)")
            stats_columns = {row[1]: row[2] for row in self.cursor.fetchall()}
            self.assertIn('employee_id', stats_columns)
            self.assertIn('annual_leave_balance', stats_columns)
            self.assertIn('sick_leave_balance', stats_columns)
            self.assertIn('performance_rating', stats_columns)
            self.__class__.test_results['data_integrity']['passed'] += 1
        except AssertionError:
            pass

    def test_data_integrity(self):
        """Test if sample data is inserted correctly"""
        self.__class__.test_results['data_integrity']['total'] += 1
        try:
            # Check if data exists in employees table
            self.cursor.execute("SELECT COUNT(*) FROM employees")
            employee_count = self.cursor.fetchone()[0]
            self.assertGreater(employee_count, 0)

            # Check if data exists in employee_stats table
            self.cursor.execute("SELECT COUNT(*) FROM employee_stats")
            stats_count = self.cursor.fetchone()[0]
            self.assertGreater(stats_count, 0)

            # Check if all employees have corresponding stats
            self.cursor.execute("""
                SELECT COUNT(*) FROM employees e
                LEFT JOIN employee_stats s ON e.employee_id = s.employee_id
                WHERE s.employee_id IS NULL
            """)
            missing_stats = self.cursor.fetchone()[0]
            self.assertEqual(missing_stats, 0)
            self.__class__.test_results['data_integrity']['passed'] += 1
        except AssertionError:
            pass

    def test_query_relevance(self):
        """Test if query relevance check works correctly"""
        # Test relevant queries
        relevant_queries = [
            "Who has the highest salary?",
            "Show me all employees in Engineering",
            "What is the average performance rating?",
            "List employees with most sick leave"
        ]
        for query in relevant_queries:
            self.__class__.test_results['query_relevance']['total'] += 1
            if check_query_relevance(query):
                self.__class__.test_results['query_relevance']['passed'] += 1

        # Test irrelevant queries
        irrelevant_queries = [
            "What's the weather like?",
            "Tell me a joke",
            "What time is it?",
            "How to make coffee?"
        ]
        for query in irrelevant_queries:
            self.__class__.test_results['query_relevance']['total'] += 1
            if not check_query_relevance(query):
                self.__class__.test_results['query_relevance']['passed'] += 1

    def test_sql_generation(self):
        """Test if SQL query generation works correctly"""
        test_cases = [
            {
                "query": "Who has the highest salary?",
                "expected_keywords": ["SELECT", "FROM", "employees", "ORDER BY", "salary", "DESC", "LIMIT"]
            },
            {
                "query": "Show me employees with most sick leave",
                "expected_keywords": ["SELECT", "FROM", "employees", "JOIN", "employee_stats", "ORDER BY", "sick_leave_balance", "DESC"]
            },
            {
                "query": "What is the average performance rating by department?",
                "expected_keywords": ["SELECT", "AVG", "GROUP BY", "department"]
            }
        ]

        for test_case in test_cases:
            self.__class__.test_results['sql_generation']['total'] += 1
            try:
                sql_query = generate_sql_query(test_case["query"])
                all_keywords_present = all(keyword.upper() in sql_query.upper() 
                                        for keyword in test_case["expected_keywords"])
                if all_keywords_present:
                    self.__class__.test_results['sql_generation']['passed'] += 1
            except Exception:
                pass

    def test_query_execution(self):
        """Test if SQL queries execute correctly"""
        self.__class__.test_results['query_execution']['total'] += 1
        try:
            # Test simple query
            simple_query = "SELECT first_name, last_name FROM employees WHERE department = 'Engineering'"
            columns, results = execute_sql_query(simple_query)
            self.assertIn('first_name', columns)
            self.assertIn('last_name', columns)
            self.assertGreater(len(results), 0)

            # Test join query
            join_query = """
                SELECT e.first_name, e.last_name, s.performance_rating
                FROM employees e
                JOIN employee_stats s ON e.employee_id = s.employee_id
                ORDER BY s.performance_rating DESC
            """
            columns, results = execute_sql_query(join_query)
            self.assertIn('first_name', columns)
            self.assertIn('last_name', columns)
            self.assertIn('performance_rating', columns)
            self.assertGreater(len(results), 0)
            self.__class__.test_results['query_execution']['passed'] += 1
        except Exception:
            pass

    def test_response_generation(self):
        """Test if response generation works correctly"""
        self.__class__.test_results['response_generation']['total'] += 1
        try:
            # Test with simple query results
            columns = ['first_name', 'last_name', 'salary']
            results = [('John', 'Doe', 95000.00)]
            query_results = (columns, results)
            response = generate_response("Who has the highest salary?", query_results)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)

            # Test with empty results
            empty_results = (columns, [])
            response = generate_response("Show me employees with salary > 1000000", empty_results)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)
            self.__class__.test_results['response_generation']['passed'] += 1
        except Exception:
            pass

    def test_foreign_key_constraints(self):
        """Test if foreign key constraints are working"""
        self.__class__.test_results['data_integrity']['total'] += 1
        try:
            # Try to insert invalid manager_id
            with self.assertRaises(sqlite3.IntegrityError):
                self.cursor.execute("""
                    INSERT INTO employees (employee_id, first_name, last_name, email, 
                    phone_number, hire_date, job_title, department, salary, manager_id, 
                    management_level)
                    VALUES (999, 'Test', 'User', 'test@test.com', '555-9999', 
                    '2024-01-01', 'Test', 'Test', 50000, 9999, 0)
                """)
                self.conn.commit()

            # Try to insert invalid employee_id in stats
            with self.assertRaises(sqlite3.IntegrityError):
                self.cursor.execute("""
                    INSERT INTO employee_stats (employee_id, annual_leave_balance, 
                    sick_leave_balance, performance_rating)
                    VALUES (9999, 20, 10, 4.0)
                """)
                self.conn.commit()
            self.__class__.test_results['data_integrity']['passed'] += 1
        except Exception:
            pass

    @classmethod
    def tearDownClass(cls):
        """Print final accuracy report after all tests"""
        cls.calculate_accuracy()

if __name__ == '__main__':
    unittest.main() 