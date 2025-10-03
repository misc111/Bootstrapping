"""
Comprehensive Test Suite for Bootstrap Animation Application
Tests all components with detailed error reporting for debugging
"""

import sys
import traceback
from typing import Callable, Any


class TestRunner:
    """Test runner with detailed error reporting."""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.failures = []

    def run_test(self, test_name: str, test_func: Callable) -> bool:
        """Run a single test with error handling."""
        self.tests_run += 1
        print(f"\n{'='*70}")
        print(f"TEST {self.tests_run}: {test_name}")
        print('='*70)

        try:
            result = test_func()
            if result:
                print(f"✓ PASSED: {test_name}")
                self.tests_passed += 1
                return True
            else:
                print(f"✗ FAILED: {test_name} - Test returned False")
                self.tests_failed += 1
                self.failures.append((test_name, "Test returned False"))
                return False
        except Exception as e:
            print(f"\n✗ FAILED: {test_name}")
            print(f"\nError Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print(f"\nFull Traceback:")
            print("-" * 70)
            traceback.print_exc()
            print("-" * 70)
            self.tests_failed += 1
            self.failures.append((test_name, str(e)))
            return False

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✓")
        print(f"Failed: {self.tests_failed} ✗")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")

        if self.failures:
            print("\n" + "="*70)
            print("FAILED TESTS SUMMARY")
            print("="*70)
            for i, (test_name, error) in enumerate(self.failures, 1):
                print(f"\n{i}. {test_name}")
                print(f"   Error: {error}")

        print("\n" + "="*70)
        if self.tests_failed == 0:
            print("🎉 ALL TESTS PASSED! 🎉")
        else:
            print(f"⚠️  {self.tests_failed} TEST(S) FAILED")
        print("="*70 + "\n")

        return self.tests_failed == 0


def test_python_version() -> bool:
    """Test Python version compatibility."""
    print(f"Python version: {sys.version}")
    major, minor = sys.version_info[:2]
    print(f"Version info: {major}.{minor}")

    if major < 3:
        print(f"✗ Python 3.x required, found {major}.{minor}")
        return False

    if major == 3 and minor < 8:
        print(f"⚠️  Warning: Python 3.8+ recommended, found {major}.{minor}")

    print(f"✓ Python version {major}.{minor} is compatible")
    return True


def test_import_standard_libs() -> bool:
    """Test standard library imports."""
    required_modules = ['os', 'sys', 'subprocess', 'typing', 'traceback']

    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ Failed to import {module}: {e}")
            return False

    return True


def test_import_numpy() -> bool:
    """Test NumPy import and basic functionality."""
    try:
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")

        # Test basic operations
        arr = np.array([1, 2, 3, 4, 5])
        mean = np.mean(arr)
        print(f"✓ NumPy operations working (test mean: {mean})")

        return True
    except ImportError as e:
        print(f"✗ NumPy not installed: {e}")
        return False
    except Exception as e:
        print(f"✗ NumPy error: {e}")
        return False


def test_import_pandas() -> bool:
    """Test Pandas import and basic functionality."""
    try:
        import pandas as pd
        print(f"✓ Pandas version: {pd.__version__}")

        # Test basic DataFrame
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        print(f"✓ Pandas operations working (test df shape: {df.shape})")

        return True
    except ImportError as e:
        print(f"✗ Pandas not installed: {e}")
        return False
    except Exception as e:
        print(f"✗ Pandas error: {e}")
        return False


def test_import_chainladder() -> bool:
    """Test chainladder import and basic functionality."""
    try:
        import chainladder as cl
        print(f"✓ chainladder version: {cl.__version__}")

        # Test loading sample data
        tri = cl.load_sample('genins')
        print(f"✓ Sample triangle loaded: shape {tri.shape}")

        # Test basic model
        model = cl.Chainladder().fit(tri)
        print(f"✓ Chainladder model fitted successfully")

        return True
    except ImportError as e:
        print(f"✗ chainladder not installed: {e}")
        print("\nTo install: pip install chainladder")
        return False
    except Exception as e:
        print(f"✗ chainladder error: {e}")
        return False


def test_import_plotly() -> bool:
    """Test Plotly import and basic functionality."""
    try:
        import plotly
        import plotly.graph_objects as go
        print(f"✓ Plotly version: {plotly.__version__}")

        # Test creating a simple figure
        fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6]))
        print(f"✓ Plotly figure creation working")

        return True
    except ImportError as e:
        print(f"✗ Plotly not installed: {e}")
        print("\nTo install: pip install plotly")
        return False
    except Exception as e:
        print(f"✗ Plotly error: {e}")
        return False


def test_import_dash() -> bool:
    """Test Dash import and basic functionality."""
    try:
        import dash
        from dash import dcc, html
        print(f"✓ Dash version: {dash.__version__}")

        # Test basic app creation
        app = dash.Dash(__name__)
        print(f"✓ Dash app creation working")

        return True
    except ImportError as e:
        print(f"✗ Dash not installed: {e}")
        print("\nTo install: pip install dash")
        return False
    except Exception as e:
        print(f"✗ Dash error: {e}")
        return False


def test_import_dash_bootstrap() -> bool:
    """Test Dash Bootstrap Components import."""
    try:
        import dash_bootstrap_components as dbc
        print(f"✓ dash-bootstrap-components version: {dbc.__version__}")

        # Test basic component
        card = dbc.Card("Test")
        print(f"✓ Bootstrap components working")

        return True
    except ImportError as e:
        print(f"✗ dash-bootstrap-components not installed: {e}")
        print("\nTo install: pip install dash-bootstrap-components")
        return False
    except Exception as e:
        print(f"✗ dash-bootstrap-components error: {e}")
        return False


def test_bootstrap_engine_import() -> bool:
    """Test bootstrap_engine module import."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP
        print(f"✓ bootstrap_engine module imported")
        print(f"✓ AnimatedBootstrapODP class available")

        return True
    except ImportError as e:
        print(f"✗ Failed to import bootstrap_engine: {e}")
        print("\nCheck that bootstrap_engine.py exists in the current directory")
        return False
    except Exception as e:
        print(f"✗ bootstrap_engine error: {e}")
        return False


def test_visualization_import() -> bool:
    """Test visualization module import."""
    try:
        from visualization import BootstrapVisualizer
        print(f"✓ visualization module imported")
        print(f"✓ BootstrapVisualizer class available")

        return True
    except ImportError as e:
        print(f"✗ Failed to import visualization: {e}")
        print("\nCheck that visualization.py exists in the current directory")
        return False
    except Exception as e:
        print(f"✗ visualization error: {e}")
        return False


def test_callbacks_import() -> bool:
    """Test callbacks module import."""
    try:
        from callbacks import register_callbacks
        print(f"✓ callbacks module imported")
        print(f"✓ register_callbacks function available")

        return True
    except ImportError as e:
        print(f"✗ Failed to import callbacks: {e}")
        print("\nCheck that callbacks.py exists in the current directory")
        return False
    except Exception as e:
        print(f"✗ callbacks error: {e}")
        return False


def test_bootstrap_engine_initialization() -> bool:
    """Test AnimatedBootstrapODP initialization."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP

        print("Initializing AnimatedBootstrapODP...")
        engine = AnimatedBootstrapODP(random_state=42)
        print(f"✓ Engine initialized successfully")

        # Check attributes
        attrs = ['triangle', 'base_model', 'fitted_values', 'actual_incremental',
                 'fitted_incremental', 'residual_pool', 'random_state']
        for attr in attrs:
            if not hasattr(engine, attr):
                print(f"✗ Missing attribute: {attr}")
                return False
            print(f"✓ Attribute '{attr}' present")

        print(f"✓ All required attributes present")
        return True

    except Exception as e:
        print(f"✗ Engine initialization failed: {e}")
        return False


def test_bootstrap_engine_metadata() -> bool:
    """Test getting triangle metadata."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP

        engine = AnimatedBootstrapODP(random_state=42)
        metadata = engine.get_triangle_metadata()
        print(f"✓ Metadata retrieved")

        # Check metadata contents
        required_keys = ['n_origin', 'n_dev', 'origin_labels', 'development_labels',
                        'actual_incremental', 'fitted_incremental', 'residuals',
                        'residual_pool', 'base_reserve']

        for key in required_keys:
            if key not in metadata:
                print(f"✗ Missing metadata key: {key}")
                return False
            print(f"✓ Metadata key '{key}': {type(metadata[key]).__name__}")

        print(f"\nMetadata Summary:")
        print(f"  Triangle size: {metadata['n_origin']} × {metadata['n_dev']}")
        print(f"  Base reserve: ${metadata['base_reserve']:,.2f}")
        print(f"  Residual pool size: {len(metadata['residual_pool'])}")

        return True

    except Exception as e:
        print(f"✗ Metadata retrieval failed: {e}")
        return False


def test_bootstrap_single_iteration() -> bool:
    """Test running a single bootstrap iteration."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP

        engine = AnimatedBootstrapODP(random_state=42)
        print("Running single iteration...")

        result = engine.run_single_iteration(0)
        print(f"✓ Single iteration completed")

        # Check result structure
        required_keys = ['iteration', 'sampling_details', 'bootstrap_incremental',
                        'bootstrap_cumulative', 'reserve_estimate']

        for key in required_keys:
            if key not in result:
                print(f"✗ Missing result key: {key}")
                return False
            print(f"✓ Result key '{key}' present")

        print(f"\nIteration Results:")
        print(f"  Reserve estimate: ${result['reserve_estimate']:,.2f}")
        print(f"  Samples taken: {len(result['sampling_details'])}")
        print(f"  Bootstrap triangle shape: {result['bootstrap_incremental'].shape}")

        # Verify sampling details
        if len(result['sampling_details']) > 0:
            sample = result['sampling_details'][0]
            print(f"\nFirst sample detail keys: {list(sample.keys())}")

        return True

    except Exception as e:
        print(f"✗ Single iteration failed: {e}")
        return False


def test_bootstrap_multiple_iterations() -> bool:
    """Test running multiple bootstrap iterations."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP
        import numpy as np

        engine = AnimatedBootstrapODP(random_state=42)
        n_iterations = 10
        print(f"Running {n_iterations} iterations...")

        summary = engine.run_bootstrap(n_iterations=n_iterations)
        print(f"✓ {n_iterations} iterations completed")

        # Check summary structure
        required_keys = ['n_iterations', 'reserve_estimates', 'mean', 'std', 'percentiles']
        for key in required_keys:
            if key not in summary:
                print(f"✗ Missing summary key: {key}")
                return False
            print(f"✓ Summary key '{key}' present")

        print(f"\nBootstrap Summary:")
        print(f"  Iterations: {summary['n_iterations']}")
        print(f"  Mean reserve: ${summary['mean']:,.2f}")
        print(f"  Std deviation: ${summary['std']:,.2f}")
        print(f"  5th percentile: ${summary['percentiles']['5']:,.2f}")
        print(f"  95th percentile: ${summary['percentiles']['95']:,.2f}")

        # Verify variation
        if summary['std'] == 0:
            print(f"⚠️  Warning: Zero standard deviation (no variation)")
        else:
            print(f"✓ Proper variation detected")

        return True

    except Exception as e:
        print(f"✗ Multiple iterations failed: {e}")
        return False


def test_visualizer_initialization() -> bool:
    """Test BootstrapVisualizer initialization."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP
        from visualization import BootstrapVisualizer

        engine = AnimatedBootstrapODP(random_state=42)
        metadata = engine.get_triangle_metadata()

        print("Initializing visualizer...")
        visualizer = BootstrapVisualizer(metadata)
        print(f"✓ Visualizer initialized")

        # Check attributes
        attrs = ['metadata', 'n_origin', 'n_dev', 'origin_labels', 'dev_labels']
        for attr in attrs:
            if not hasattr(visualizer, attr):
                print(f"✗ Missing attribute: {attr}")
                return False
            print(f"✓ Attribute '{attr}' present")

        return True

    except Exception as e:
        print(f"✗ Visualizer initialization failed: {e}")
        return False


def test_visualizer_triangle_heatmap() -> bool:
    """Test creating triangle heatmap visualization."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP
        from visualization import BootstrapVisualizer

        engine = AnimatedBootstrapODP(random_state=42)
        metadata = engine.get_triangle_metadata()
        visualizer = BootstrapVisualizer(metadata)

        print("Creating triangle heatmap...")
        fig = visualizer.create_triangle_heatmap(
            metadata['actual_incremental'],
            "Test Triangle"
        )
        print(f"✓ Triangle heatmap created")
        print(f"  Figure type: {type(fig).__name__}")

        return True

    except Exception as e:
        print(f"✗ Triangle heatmap creation failed: {e}")
        return False


def test_visualizer_residual_scatter() -> bool:
    """Test creating residual pool scatter plot."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP
        from visualization import BootstrapVisualizer

        engine = AnimatedBootstrapODP(random_state=42)
        metadata = engine.get_triangle_metadata()
        visualizer = BootstrapVisualizer(metadata)

        print("Creating residual scatter plot...")
        fig = visualizer.create_residual_pool_scatter(metadata['residual_pool'])
        print(f"✓ Residual scatter plot created")

        return True

    except Exception as e:
        print(f"✗ Residual scatter plot creation failed: {e}")
        return False


def test_visualizer_distribution() -> bool:
    """Test creating reserve distribution histogram."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP
        from visualization import BootstrapVisualizer

        engine = AnimatedBootstrapODP(random_state=42)
        metadata = engine.get_triangle_metadata()
        visualizer = BootstrapVisualizer(metadata)

        # Run some iterations to get data
        engine.run_bootstrap(n_iterations=10)

        print("Creating distribution histogram...")
        fig = visualizer.create_reserve_distribution(
            engine.reserve_estimates,
            base_reserve=metadata['base_reserve']
        )
        print(f"✓ Distribution histogram created")

        return True

    except Exception as e:
        print(f"✗ Distribution histogram creation failed: {e}")
        return False


def test_visualizer_animation_frame() -> bool:
    """Test creating animation frame."""
    try:
        from bootstrap_engine import AnimatedBootstrapODP
        from visualization import BootstrapVisualizer

        engine = AnimatedBootstrapODP(random_state=42)
        metadata = engine.get_triangle_metadata()
        visualizer = BootstrapVisualizer(metadata)

        # Run one iteration
        result = engine.run_single_iteration(0)

        print("Creating animation frame...")
        fig = visualizer.create_sampling_animation_frame(result, frame_idx=0)
        print(f"✓ Animation frame created")

        return True

    except Exception as e:
        print(f"✗ Animation frame creation failed: {e}")
        return False


def test_dash_app_creation() -> bool:
    """Test creating Dash application."""
    try:
        import dash
        import dash_bootstrap_components as dbc

        print("Creating Dash app...")
        app = dash.Dash(
            __name__,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True
        )
        print(f"✓ Dash app created")
        print(f"  App type: {type(app).__name__}")

        return True

    except Exception as e:
        print(f"✗ Dash app creation failed: {e}")
        return False


def test_file_existence() -> bool:
    """Test that all required files exist."""
    import os

    required_files = [
        'app.py',
        'bootstrap_engine.py',
        'visualization.py',
        'callbacks.py',
        'requirements.txt',
        'README.md'
    ]

    optional_files = [
        'assets/styles.css',
        'test_bootstrap.py',
        'QUICKSTART.md',
        'START_HERE.md'
    ]

    print("Checking required files...")
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename}")
        else:
            print(f"✗ Missing: {filename}")
            all_exist = False

    print("\nChecking optional files...")
    for filename in optional_files:
        if os.path.exists(filename):
            print(f"✓ {filename}")
        else:
            print(f"⚠️  Optional file not found: {filename}")

    return all_exist


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("BOOTSTRAP ANIMATION - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("\nThis test suite will verify that all components are working correctly.")
    print("Detailed error messages will help identify and fix any issues.\n")

    runner = TestRunner()

    # Run tests in order
    tests = [
        ("Python Version Check", test_python_version),
        ("Standard Library Imports", test_import_standard_libs),
        ("NumPy Import & Functionality", test_import_numpy),
        ("Pandas Import & Functionality", test_import_pandas),
        ("Chainladder Import & Functionality", test_import_chainladder),
        ("Plotly Import & Functionality", test_import_plotly),
        ("Dash Import & Functionality", test_import_dash),
        ("Dash Bootstrap Components Import", test_import_dash_bootstrap),
        ("Bootstrap Engine Module Import", test_bootstrap_engine_import),
        ("Visualization Module Import", test_visualization_import),
        ("Callbacks Module Import", test_callbacks_import),
        ("File Existence Check", test_file_existence),
        ("Bootstrap Engine Initialization", test_bootstrap_engine_initialization),
        ("Bootstrap Engine Metadata", test_bootstrap_engine_metadata),
        ("Bootstrap Single Iteration", test_bootstrap_single_iteration),
        ("Bootstrap Multiple Iterations", test_bootstrap_multiple_iterations),
        ("Visualizer Initialization", test_visualizer_initialization),
        ("Visualizer Triangle Heatmap", test_visualizer_triangle_heatmap),
        ("Visualizer Residual Scatter", test_visualizer_residual_scatter),
        ("Visualizer Distribution", test_visualizer_distribution),
        ("Visualizer Animation Frame", test_visualizer_animation_frame),
        ("Dash App Creation", test_dash_app_creation),
    ]

    for test_name, test_func in tests:
        runner.run_test(test_name, test_func)

    # Print summary
    success = runner.print_summary()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
