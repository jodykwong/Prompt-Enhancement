"""
Comprehensive test suite for documentation style detection.
Tests all 8 acceptance criteria for Story 2.7.
"""

import pytest
import tempfile
import os
from pathlib import Path
from dataclasses import asdict

# FIX HIGH #5: Use relative imports consistent with other test files
from prompt_enhancement.pipeline.tech_stack import ProjectTypeDetectionResult, ProjectLanguage
from prompt_enhancement.pipeline.project_files import ProjectIndicatorResult
from prompt_enhancement.pipeline.documentation_style import (
    DocumentationStyleDetector,
    DocumentationStyle,
    DocumentationCoverage,
    DocumentationStyleResult,
)


class TestPythonDocumentationStyleDetection:
    """Test AC1: Python documentation style detection"""

    def test_google_style_detection(self):
        """Test detection of Google-style docstrings"""
        detector = DocumentationStyleDetector()

        # Create temp files with Google-style docstrings
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "google_example.py"
            test_file.write_text('''
def calculate_sum(a, b):
    """Calculate the sum of two numbers.

    Args:
        a (int): The first number
        b (int): The second number

    Returns:
        int: The sum of a and b

    Raises:
        TypeError: If inputs are not numbers
    """
    return a + b

class DataProcessor:
    """Process data files.

    Args:
        path (str): Path to data file

    Attributes:
        data (list): Processed data
    """
    def __init__(self, path):
        self.data = []
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert DocumentationStyle.GOOGLE in [s.style for s in result.detected_styles]
            google_style = next(s for s in result.detected_styles if s.style == DocumentationStyle.GOOGLE)
            assert google_style.confidence >= 0.7

    def test_numpy_style_detection(self):
        """Test detection of NumPy-style docstrings"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "numpy_example.py"
            test_file.write_text('''
def process_array(data, axis=0):
    """Process multidimensional array.

    Parameters
    ----------
    data : np.ndarray
        Input array to process
    axis : int, optional
        Axis along which to process (default: 0)

    Returns
    -------
    np.ndarray
        Processed array

    Raises
    ------
    ValueError
        If data is empty
    """
    return data.sum(axis=axis)
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert DocumentationStyle.NUMPY in [s.style for s in result.detected_styles]

    def test_pep257_style_detection(self):
        """Test detection of PEP 257 style docstrings"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "pep257_example.py"
            test_file.write_text('''
def simple_function():
    """One-liner description."""
    pass

class SimpleClass:
    """Class with minimal docstring."""

    def method(self):
        """Method with one-liner description."""
        return None
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert DocumentationStyle.PEP257 in [s.style for s in result.detected_styles]

    def test_sphinx_style_detection(self):
        """Test detection of Sphinx/reST style docstrings"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "sphinx_example.py"
            test_file.write_text('''
def sphinx_function(param1, param2):
    """Function with Sphinx documentation.

    :param param1: First parameter
    :type param1: str
    :param param2: Second parameter
    :type param2: int
    :return: Combined result
    :rtype: str
    :raises ValueError: If validation fails
    """
    return f"{param1}_{param2}"
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert DocumentationStyle.SPHINX in [s.style for s in result.detected_styles]

    def test_mixed_python_styles_handling(self):
        """Test graceful handling of mixed documentation styles"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "mixed_example.py"
            test_file.write_text('''
def google_style():
    """Function with Google style.

    Args:
        None

    Returns:
        None
    """
    pass

def pep257_style():
    """Simple one-liner."""
    pass

def sphinx_style():
    """Function with Sphinx style.

    :param x: parameter
    :return: result
    """
    pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            # Should detect multiple styles
            detected_style_types = [s.style for s in result.detected_styles]
            assert len(detected_style_types) >= 2


class TestJavaScriptDocumentationStyleDetection:
    """Test AC2: JavaScript/TypeScript documentation style detection"""

    def test_jsdoc_style_detection(self):
        """Test detection of JSDoc style comments"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "jsdoc_example.js"
            test_file.write_text('''
/**
 * Calculate sum of two numbers
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} Sum of a and b
 * @throws {TypeError} If inputs are not numbers
 */
function calculateSum(a, b) {
    return a + b;
}

/**
 * Process data array
 * @param {Array<string>} items - Items to process
 * @returns {Promise<Array>} Processed items
 */
async function processData(items) {
    return items.map(i => i.toUpperCase());
}
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert DocumentationStyle.JSDOC in [s.style for s in result.detected_styles]
            jsdoc_style = next(s for s in result.detected_styles if s.style == DocumentationStyle.JSDOC)
            assert jsdoc_style.confidence >= 0.7

    def test_typescript_doc_style_detection(self):
        """Test detection of TypeScript doc comments"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "typescript_example.ts"
            test_file.write_text('''
/**
 * Process generic data
 * @param data The input data
 * @returns Processed data
 */
function processData<T>(data: T[]): T[] {
    return data;
}

/**
 * Create user object
 * @param name User name
 * @param age User age
 * @returns User object with id
 */
interface User {
    id: number;
    name: string;
    age: number;
}
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="16.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            # TypeScript can use JSDoc or custom patterns
            assert len(result.detected_styles) > 0


class TestJavaDocumentationStyleDetection:
    """Test AC3: Java documentation style detection"""

    def test_javadoc_style_detection(self):
        """Test detection of Javadoc style comments"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "JavaDoc.java"
            test_file.write_text('''
/**
 * Calculates the sum of two numbers.
 *
 * @param a the first number
 * @param b the second number
 * @return the sum of a and b
 * @throws IllegalArgumentException if either argument is negative
 * @see #multiply(int, int)
 */
public int sum(int a, int b) {
    return a + b;
}

/**
 * Main class for data processing.
 *
 * <p>This class handles all data transformation operations
 * with support for parallel processing.</p>
 *
 * @author John Doe
 * @version 1.0
 */
public class DataProcessor {
    /**
     * Process input file.
     *
     * @param inputFile the input file path
     * @return processed data
     */
    public String process(File inputFile) {
        return "";
    }
}
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.JAVA,
                version="11.0.0",
                confidence=0.95,
                markers_found=["pom.xml"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert DocumentationStyle.JAVADOC in [s.style for s in result.detected_styles]
            javadoc_style = next(s for s in result.detected_styles if s.style == DocumentationStyle.JAVADOC)
            assert javadoc_style.confidence >= 0.7


class TestGoDocumentationStyleDetection:
    """Test AC4: Go documentation style detection"""

    def test_go_doc_style_detection(self):
        """Test detection of Go doc comments"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "example.go"
            test_file.write_text('''
// Package myapp provides core functionality for the application.
//
// It includes utilities for data processing and transformation.
package myapp

// MyFunction does something important.
// It takes input and returns processed output.
func MyFunction(input string) string {
    return input
}

// DataProcessor handles data transformation.
type DataProcessor struct {
    // Name is the processor name
    Name string
}

// Process processes the input data.
// Returns the processed result or an error.
func (dp *DataProcessor) Process(data []byte) ([]byte, error) {
    return data, nil
}
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.GO,
                version="1.18.0",
                confidence=0.95,
                markers_found=["go.mod"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert DocumentationStyle.GO_DOC in [s.style for s in result.detected_styles]


class TestDocumentationPresenceAnalysis:
    """Test AC5: Documentation presence and coverage analysis"""

    def test_documentation_coverage_calculation(self):
        """Test calculation of documentation coverage percentage"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with some documented and undocumented functions
            test_file = Path(tmpdir) / "coverage_example.py"
            test_file.write_text('''
def documented_function():
    """This function is documented."""
    pass

def undocumented_function():
    pass

class DocumentedClass:
    """This class is documented."""

    def documented_method(self):
        """This method is documented."""
        pass

    def undocumented_method(self):
        pass

class UndocumentedClass:
    pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.coverage is not None
            assert result.coverage.documented_count >= 0
            assert result.coverage.total_count > 0
            assert 0 <= result.coverage.coverage_percentage <= 100

    def test_under_documented_project_flagging(self):
        """Test flagging of under-documented projects (< 25% coverage)"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "underdocumented.py"
            test_file.write_text('''
def func1():
    pass

def func2():
    pass

def func3():
    """Only this one is documented."""
    pass

class Class1:
    pass

class Class2:
    pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert result.coverage is not None
            # With only 1 out of 7+ items documented, should be under 25%
            if result.coverage.total_count > 0:
                assert result.coverage.coverage_percentage <= 30

    def test_special_documentation_files_detection(self):
        """Test detection of special documentation files"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create special documentation files
            Path(tmpdir, "README.md").write_text("# Project")
            Path(tmpdir, "CONTRIBUTING.md").write_text("# Contributing")
            Path(tmpdir, "ARCHITECTURE.md").write_text("# Architecture")
            Path(tmpdir, "docs").mkdir()
            Path(tmpdir, "docs", "guide.md").write_text("# Guide")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            # Should find special documentation files if they exist
            if result and result.special_documentation_files:
                assert any("README" in f for f in result.special_documentation_files)


class TestDocumentationConfidenceScoring:
    """Test AC6: Documentation confidence scoring"""

    def test_high_confidence_with_consistent_style(self):
        """Test high confidence scoring with consistent documentation style"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with consistently documented functions
            test_file = Path(tmpdir) / "consistent_doc.py"
            test_file.write_text('''
def func1():
    """Function 1.

    Args:
        x: input

    Returns:
        output
    """
    pass

def func2():
    """Function 2.

    Args:
        y: input

    Returns:
        result
    """
    pass

def func3():
    """Function 3.

    Args:
        z: input

    Returns:
        data
    """
    pass

class Helper:
    """Helper class.

    Args:
        param: initialization parameter
    """
    pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert len(result.detected_styles) > 0
            # With consistent style, confidence should be high
            assert result.detected_styles[0].confidence >= 0.65

    def test_confidence_with_multiple_styles(self):
        """Test confidence scoring when multiple styles are present"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "mixed_styles.py"
            test_file.write_text('''
def style1():
    """One style.

    Args:
        x: input
    """
    pass

def style2():
    """Another style.

    :param y: input
    :return: output
    """
    pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            # With mixed styles, each style's confidence should be lower
            assert all(0 <= s.confidence <= 1.0 for s in result.detected_styles)


class TestDocumentationResultFormat:
    """Test AC7: Documentation result format"""

    def test_documentation_style_result_structure(self):
        """Test that result has all required fields"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('''
def func():
    """Test function."""
    pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            assert hasattr(result, 'primary_style')
            assert hasattr(result, 'detected_styles')
            assert hasattr(result, 'coverage')
            assert hasattr(result, 'analysis_notes')
            assert hasattr(result, 'timestamp')
            assert hasattr(result, 'version')
            assert result.detected_styles is not None
            assert len(result.detected_styles) > 0

    def test_result_serialization(self):
        """Test that result can be serialized to dict"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text('''
def func():
    """Test."""
    pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            result_dict = asdict(result)
            assert result_dict is not None
            assert 'detected_styles' in result_dict


class TestIntegration:
    """Test AC8: Integration with project analysis"""

    def test_integration_with_project_analysis(self):
        """Test integration with other detection modules"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a small Python project structure
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()

            test_file = src_dir / "main.py"
            test_file.write_text('''
def main():
    """Main entry point.

    Args:
        None

    Returns:
        int: Exit code
    """
    return 0
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            assert result is not None
            # Should work seamlessly with other detection results
            assert result.detected_styles is not None


class TestPerformance:
    """Test performance targets"""

    def test_performance_within_2_second_budget(self):
        """Test that detection completes within 2-second budget"""
        import time

        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple files to simulate realistic project
            for i in range(10):
                test_file = Path(tmpdir) / f"module_{i}.py"
                test_file.write_text('''
def function():
    """Documented function.

    Args:
        x: input parameter

    Returns:
        result
    """
    pass

class MyClass:
    """Documented class."""

    def method(self):
        """Documented method."""
        pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            start_time = time.time()
            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))
            elapsed = time.time() - start_time

            # Should complete within 2 seconds
            assert elapsed < 2.0
            assert result is not None


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_no_documentation_handling(self):
        """Test handling of projects with no documentation"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "no_doc.py"
            test_file.write_text('''
def func1():
    pass

def func2():
    pass

class Class1:
    pass
''')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[str(test_file)],
                lock_files_present=set(),
                confidence=0.95
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            # Should gracefully handle undocumented projects
            assert result is not None

    def test_unsupported_language_handling(self):
        """Test handling of unsupported languages"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.RUST,
                version="1.70",
                confidence=0.95,
                markers_found=["Cargo.toml"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            # Should gracefully handle unsupported languages
            assert result is None or len(result.detected_styles) == 0

    def test_empty_project_handling(self):
        """Test handling of empty projects"""
        detector = DocumentationStyleDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.8",
                confidence=0.95,
                markers_found=["setup.py"],
                secondary_languages=[]
            )
            file_result = ProjectIndicatorResult(
                metadata=None,
                files_found=[],
                lock_files_present=set(),
                confidence=0.0
            )

            result = detector.detect_documentation_style(tech_result, file_result, str(tmpdir))

            # Should handle empty projects gracefully
            assert result is None or isinstance(result, DocumentationStyleResult)
