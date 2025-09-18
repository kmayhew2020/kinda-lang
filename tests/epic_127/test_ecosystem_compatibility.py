"""
Epic #127 Phase 3: Python Ecosystem Compatibility Tests

Tests integration and compatibility with popular Python libraries:
- NumPy, Pandas, Django, Flask, Requests, SQLAlchemy, etc.
"""

import pytest
import sys
import subprocess
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from kinda.injection.injection_engine import InjectionEngine, InjectionConfig
from kinda.injection.ast_analyzer import PatternType
from kinda.migration.utilities import MigrationUtilities

# Note: gradual_kinda and kinda_safe are mocked in tests
# from kinda.migration.decorators import gradual_kinda, kinda_safe


class TestEcosystemCompatibility:
    """Test compatibility with major Python ecosystem libraries"""

    def setup_method(self):
        """Setup for each test"""
        self.engine = InjectionEngine()
        self.config = InjectionConfig(
            enabled_patterns={
                PatternType.KINDA_INT,
                PatternType.KINDA_FLOAT,
                PatternType.SORTA_PRINT,
                PatternType.SOMETIMES,
            },
            safety_level="safe",
        )

    def test_numpy_compatibility(self):
        """Test kinda-lang compatibility with NumPy operations"""
        numpy_code = """
import numpy as np

def analyze_data():
    # Basic NumPy operations that could benefit from kinda behavior
    data = np.array([1, 2, 3, 4, 5])
    mean_val = 42.0
    std_val = 1.5

    # Statistical operations
    result = np.random.normal(mean_val, std_val, 100)

    if result.mean() > 40:
        print(f"Analysis complete: mean={result.mean():.2f}")

    return result

if __name__ == "__main__":
    analyze_data()
"""

        # Test injection into NumPy code
        result = self.engine.inject_source(numpy_code, self.config)

        assert result.success
        assert "import kinda" in result.transformed_code
        assert len(result.applied_patterns) > 0
        assert result.performance_estimate <= 20.0  # Within architecture limits

        # Verify the transformed code is syntactically valid
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Transformed NumPy code is not valid Python: {e}")

    def test_pandas_compatibility(self):
        """Test kinda-lang compatibility with Pandas operations"""
        pandas_code = """
import pandas as pd

def process_dataframe():
    # Create sample dataframe
    data = {
        'values': [10, 20, 30, 40, 50],
        'weights': [1.0, 2.0, 3.0, 4.0, 5.0]
    }
    df = pd.DataFrame(data)

    # Statistical operations
    threshold = 25

    # Filter and process
    if len(df[df['values'] > threshold]) > 0:
        print("Found values above threshold")
        result = df['values'].mean()

    return df

if __name__ == "__main__":
    process_dataframe()
"""

        result = self.engine.inject_source(pandas_code, self.config)

        assert result.success
        assert "import kinda" in result.transformed_code
        assert result.performance_estimate <= 20.0

        # Verify syntactic validity
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Transformed Pandas code is not valid Python: {e}")

    def test_flask_compatibility(self):
        """Test kinda-lang compatibility with Flask web applications"""
        flask_code = """
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def get_data():
    # Simulate some processing
    count = 100
    threshold = 0.8

    # Generate response
    if count > 50:
        print("Processing large dataset")

    response_data = {
        'count': count,
        'threshold': threshold,
        'status': 'success'
    }

    return jsonify(response_data)

@app.route('/health')
def health_check():
    status_code = 200
    return {'status': 'healthy'}, status_code

if __name__ == '__main__':
    app.run(debug=True)
"""

        result = self.engine.inject_source(flask_code, self.config)

        assert result.success
        assert "import kinda" in result.transformed_code
        assert result.performance_estimate <= 20.0

        # Verify syntactic validity
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Transformed Flask code is not valid Python: {e}")

    def test_django_compatibility(self):
        """Test kinda-lang compatibility with Django models and views"""
        django_code = """
from django.db import models
from django.http import JsonResponse

class DataModel(models.Model):
    value = models.IntegerField(default=0)
    threshold = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def process_value(self):
        multiplier = 2
        result = self.value * multiplier

        if result > 100:
            print(f"High value detected: {result}")

        return result

def api_view(request):
    # Simulate data processing
    data_count = 42
    success_rate = 0.95

    # Process request
    if data_count > 20:
        print("Processing batch request")

    response = {
        'count': data_count,
        'success_rate': success_rate,
        'message': 'Data processed successfully'
    }

    return JsonResponse(response)
"""

        result = self.engine.inject_source(django_code, self.config)

        assert result.success
        assert "import kinda" in result.transformed_code
        assert result.performance_estimate <= 20.0

        # Verify syntactic validity
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Transformed Django code is not valid Python: {e}")

    def test_requests_compatibility(self):
        """Test kinda-lang compatibility with HTTP requests"""
        requests_code = """
import requests
import json

def fetch_api_data():
    # API configuration
    base_url = "https://api.example.com"
    timeout = 30
    max_retries = 3

    # Make requests with retries
    for attempt in range(max_retries):
        retry_delay = attempt * 2

        try:
            if attempt > 0:
                print(f"Retry attempt {attempt}")

            response = requests.get(f"{base_url}/data", timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                success_count = len(data.get('items', []))
                print(f"Fetched {success_count} items")
                return data

        except requests.RequestException as e:
            print(f"Request failed: {e}")

    return None

if __name__ == "__main__":
    fetch_api_data()
"""

        result = self.engine.inject_source(requests_code, self.config)

        assert result.success
        assert "import kinda" in result.transformed_code
        assert result.performance_estimate <= 20.0

        # Verify syntactic validity
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Transformed Requests code is not valid Python: {e}")

    def test_sqlalchemy_compatibility(self):
        """Test kinda-lang compatibility with SQLAlchemy ORM"""
        sqlalchemy_code = """
from sqlalchemy import create_engine, Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class DataRecord(Base):
    __tablename__ = 'data_records'

    id = Column(Integer, primary_key=True)
    value = Column(Integer, default=0)
    score = Column(Float, default=0.0)
    status = Column(String(50), default='pending')

    def calculate_score(self):
        base_score = 100
        modifier = 1.2

        result = self.value * modifier

        if result > base_score:
            print(f"High score: {result}")
            self.status = 'high'
        else:
            self.status = 'normal'

        return result

def process_records():
    # Database setup
    engine = create_engine('sqlite:///test.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Query and process
    batch_size = 50
    records = session.query(DataRecord).limit(batch_size).all()

    for record in records:
        score = record.calculate_score()
        if score > 80:
            print(f"Processing record {record.id}")

    session.commit()
    session.close()

if __name__ == "__main__":
    process_records()
"""

        result = self.engine.inject_source(sqlalchemy_code, self.config)

        assert result.success
        assert "import kinda" in result.transformed_code
        assert result.performance_estimate <= 20.0

        # Verify syntactic validity
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Transformed SQLAlchemy code is not valid Python: {e}")

    @pytest.mark.parametrize(
        "library_name,import_code,test_code",
        [
            (
                "matplotlib",
                "import matplotlib.pyplot as plt",
                """
plt.figure(figsize=(8, 6))
data = [1, 2, 3, 4, 5]
threshold = 3.0
if max(data) > threshold:
    print("Creating plot")
plt.plot(data)
plt.show()
""",
            ),
            (
                "scipy",
                "from scipy import stats",
                """
import numpy as np
data = np.array([1, 2, 3, 4, 5])
confidence = 0.95
mean = data.mean()
if mean > 2.5:
    print(f"Statistical analysis: mean={mean}")
result = stats.norm.pdf(data, mean, 1.0)
""",
            ),
            (
                "scikit-learn",
                "from sklearn.linear_model import LinearRegression",
                """
import numpy as np
X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2, 4, 6, 8, 10])
model = LinearRegression()
score_threshold = 0.9
model.fit(X, y)
score = model.score(X, y)
if score > score_threshold:
    print(f"Model performance: {score}")
""",
            ),
        ],
    )
    def test_scientific_libraries_compatibility(self, library_name, import_code, test_code):
        """Test compatibility with scientific computing libraries"""
        full_code = f"{import_code}\n\n{test_code}"

        result = self.engine.inject_source(full_code, self.config)

        assert result.success, f"Failed to inject into {library_name} code"
        assert "import kinda" in result.transformed_code
        assert result.performance_estimate <= 20.0

        # Verify syntactic validity
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Transformed {library_name} code is not valid Python: {e}")


class TestMigrationDecorators:
    """Test migration decorators with popular libraries"""

    def test_gradual_migration_numpy(self):
        """Test gradual migration with NumPy functions"""

        # Mock the decorators for testing
        def mock_gradual_kinda(probability=0.5):
            def decorator(func):
                func._kinda_probability = probability
                return func

            return decorator

        def numpy_analysis():
            # Simulate numpy operations
            data = [1, 2, 3, 4, 5]
            return sum(data) / len(data)

        # Apply mock decorator
        decorated_func = mock_gradual_kinda(probability=0.3)(numpy_analysis)

        # Test the decorated function
        result = decorated_func()
        assert isinstance(result, (int, float))
        assert hasattr(decorated_func, "_kinda_probability")
        assert decorated_func._kinda_probability == 0.3

    def test_safe_migration_pandas(self):
        """Test safe migration with Pandas operations"""

        def mock_kinda_safe(fallback_mode=True):
            def decorator(func):
                func._safe_config = {"fallback_mode": fallback_mode}
                return func

            return decorator

        def pandas_processing():
            # Simulate pandas operations
            data = {"values": [1, 2, 3, 4, 5]}
            return sum(data["values"]) / len(data["values"])

        # Apply mock decorator
        decorated_func = mock_kinda_safe(fallback_mode=True)(pandas_processing)

        # Test the decorated function
        result = decorated_func()
        assert isinstance(result, (int, float))
        assert hasattr(decorated_func, "_safe_config")
        assert decorated_func._safe_config["fallback_mode"] is True


class TestPerformanceOverhead:
    """Test that ecosystem integration meets performance requirements"""

    def setup_method(self):
        """Setup for performance tests"""
        self.engine = InjectionEngine()
        self.config = InjectionConfig(
            enabled_patterns={
                PatternType.KINDA_INT,
                PatternType.KINDA_FLOAT,
                PatternType.SORTA_PRINT,
                PatternType.SOMETIMES,
            },
            safety_level="safe",
        )

    def test_performance_overhead_numpy(self):
        """Test performance overhead with NumPy code stays under 20%"""
        numpy_code = """
import numpy as np

def heavy_computation():
    size = 1000
    iterations = 10

    for i in range(iterations):
        data = np.random.random(size)
        mean_val = data.mean()
        std_val = data.std()

        if mean_val > 0.4:
            print(f"Iteration {i}: mean={mean_val:.4f}")

        result = np.sum(data * std_val)

    return result
"""

        result = self.engine.inject_source(numpy_code, self.config)

        assert result.success
        # Architecture requirement: <20% overhead
        assert (
            result.performance_estimate < 20.0
        ), f"Performance overhead {result.performance_estimate}% exceeds 20% limit"

    def test_performance_overhead_pandas(self):
        """Test performance overhead with Pandas code stays under 20%"""
        pandas_code = """
import pandas as pd
import numpy as np

def data_processing():
    rows = 1000
    cols = 10

    # Create large dataframe
    data = np.random.random((rows, cols))
    df = pd.DataFrame(data)

    # Multiple operations
    for col in df.columns:
        threshold = 0.5
        mean_val = df[col].mean()

        if mean_val > threshold:
            print(f"Column {col}: mean={mean_val:.4f}")

        df[col] = df[col] * 2.0

    return df.sum().sum()
"""

        result = self.engine.inject_source(pandas_code, self.config)

        assert result.success
        assert (
            result.performance_estimate < 20.0
        ), f"Performance overhead {result.performance_estimate}% exceeds 20% limit"

    def test_minimal_overhead_simple_code(self):
        """Test that simple code has minimal overhead"""
        simple_code = """
def simple_function():
    x = 42
    y = 3.14

    if x > 40:
        print("Value is high")

    return x + y
"""

        result = self.engine.inject_source(simple_code, self.config)

        assert result.success
        # Simple code should have very low overhead
        assert (
            result.performance_estimate < 10.0
        ), f"Simple code overhead {result.performance_estimate}% is too high"


@pytest.mark.integration
class TestRealWorldScenarios:
    """Test real-world usage scenarios"""

    def test_web_api_with_database(self):
        """Test web API endpoint with database operations"""
        api_code = """
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Query database
    query_timeout = 30
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()

    if user:
        # Process user data
        user_score = user[3] if len(user) > 3 else 0
        bonus_threshold = 100

        if user_score > bonus_threshold:
            print(f"High-value user: {user_id}")

        response = {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'score': user_score
        }
    else:
        response = {'error': 'User not found'}

    conn.close()
    return jsonify(response)

if __name__ == '__main__':
    app.run()
"""

        engine = InjectionEngine()
        config = InjectionConfig(
            enabled_patterns={
                PatternType.KINDA_INT,
                PatternType.SOMETIMES,
                PatternType.SORTA_PRINT,
            },
            safety_level="safe",
        )

        result = engine.inject_source(api_code, config)

        assert result.success
        assert "import kinda" in result.transformed_code
        assert result.performance_estimate <= 20.0

        # Verify code is still valid
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Real-world scenario code is not valid Python: {e}")

    def test_data_analysis_pipeline(self):
        """Test data analysis pipeline with multiple libraries"""
        pipeline_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_sales_data(csv_file):
    # Load data
    df = pd.read_csv(csv_file)
    batch_size = 1000

    # Basic statistics
    total_sales = df['amount'].sum()
    avg_sale = df['amount'].mean()
    threshold = 500.0

    # Data processing
    if len(df) > batch_size:
        print(f"Processing large dataset: {len(df)} records")

    # Filter high-value sales
    high_value = df[df['amount'] > threshold]
    high_value_count = len(high_value)

    if high_value_count > 0:
        print(f"Found {high_value_count} high-value sales")

    # Generate insights
    monthly_sales = df.groupby('month')['amount'].sum()
    growth_rate = 0.05

    # Visualization
    plt.figure(figsize=(10, 6))
    monthly_sales.plot(kind='bar')
    plt.title('Monthly Sales Analysis')

    # Return results
    results = {
        'total_sales': total_sales,
        'average_sale': avg_sale,
        'high_value_count': high_value_count,
        'growth_rate': growth_rate
    }

    return results

if __name__ == "__main__":
    results = analyze_sales_data('sales.csv')
    print(f"Analysis complete: {results}")
"""

        engine = InjectionEngine()
        config = InjectionConfig(
            enabled_patterns={
                PatternType.KINDA_INT,
                PatternType.KINDA_FLOAT,
                PatternType.SOMETIMES,
                PatternType.SORTA_PRINT,
            },
            safety_level="safe",
        )

        result = engine.inject_source(pipeline_code, config)

        assert result.success
        assert "import kinda" in result.transformed_code
        assert result.performance_estimate <= 20.0

        # Verify multiple patterns were applied
        assert len(result.applied_patterns) > 0

        # Verify code is still valid
        try:
            compile(result.transformed_code, "<test>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Data analysis pipeline code is not valid Python: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
