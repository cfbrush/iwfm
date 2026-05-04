#!/bin/bash

# run_tests.sh
# Unix shell script to run all unit tests for the iwfm package
# Logs output to files and provides summary statistics
# Copyright (C) 2025-2026 University of California

# Propagate pytest's exit code through the `tee` pipeline so the per-file
# loop's `if pytest ... | tee ...; then` actually reflects pytest's status
# rather than tee's (which is always 0).
set -o pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="${SCRIPT_DIR}/tests"
LOG_DIR="${SCRIPT_DIR}/test_logs"
PYTHON_CMD="${SCRIPT_DIR}/.venv/bin/python"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create log directory if it doesn't exist
mkdir -p "${LOG_DIR}"

# Log files
MAIN_LOG="${LOG_DIR}/test_run_${TIMESTAMP}.log"
SUMMARY_LOG="${LOG_DIR}/test_summary_${TIMESTAMP}.log"
ERROR_LOG="${LOG_DIR}/test_errors_${TIMESTAMP}.log"

# Colors for output (if terminal supports them)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
    echo "${message}" >> "${MAIN_LOG}"
}

# Function to check if Python virtual environment is available
check_python_env() {
    if [[ ! -f "${PYTHON_CMD}" ]]; then
        print_status "${RED}" "ERROR: Python virtual environment not found at ${PYTHON_CMD}"
        print_status "${YELLOW}" "Please run: python -m venv .venv && source .venv/bin/activate && pip install pytest"
        exit 1
    fi
    
    # Check if pytest is installed
    if ! "${PYTHON_CMD}" -c "import pytest" 2>/dev/null; then
        print_status "${RED}" "ERROR: pytest not installed in virtual environment"
        print_status "${YELLOW}" "Installing pytest..."
        "${PYTHON_CMD}" -m pip install pytest
    fi
}

# Function to run a specific test file
run_test_file() {
    local test_file=$1
    local test_name=$(basename "${test_file}" .py)
    
    print_status "${BLUE}" "Running ${test_name}..."
    
    # Run the test and capture output
    if "${PYTHON_CMD}" -m pytest "${test_file}" -v --tb=short 2>&1 | tee -a "${MAIN_LOG}"; then
        print_status "${GREEN}" "✓ ${test_name} completed"
        return 0
    else
        print_status "${RED}" "✗ ${test_name} had failures"
        return 1
    fi
}

# Function to run all tests with coverage if available
run_all_tests() {
    print_status "${BLUE}" "Running all tests together..."
    
    # Try to install coverage if not available
    if "${PYTHON_CMD}" -c "import coverage" 2>/dev/null; then
        print_status "${YELLOW}" "Running tests with coverage..."
        "${PYTHON_CMD}" -m coverage run -m pytest "${TEST_DIR}" -v --tb=short 2>&1 | tee -a "${MAIN_LOG}"
        "${PYTHON_CMD}" -m coverage report 2>&1 | tee -a "${MAIN_LOG}"
        "${PYTHON_CMD}" -m coverage html --directory="${LOG_DIR}/htmlcov" 2>&1 | tee -a "${MAIN_LOG}"
    else
        print_status "${YELLOW}" "Running tests without coverage..."
        "${PYTHON_CMD}" -m pytest "${TEST_DIR}" -v --tb=short 2>&1 | tee -a "${MAIN_LOG}"
    fi
}

# Function to generate summary report
generate_summary() {
    local total_files=$1
    local passed_files=$2
    local failed_files=$3
    
    {
        echo "=================================================="
        echo "IWFM Package Test Summary - $(date)"
        echo "=================================================="
        echo "Total test files run: ${total_files}"
        echo "Passed: ${passed_files}"
        echo "Failed: ${failed_files}"
        echo ""
        echo "Test files:"
        
        for test_file in "${TEST_DIR}"/test_*.py; do
            if [[ -f "${test_file}" ]]; then
                echo "  - $(basename "${test_file}")"
            fi
        done
        
        echo ""
        echo "Logs saved to:"
        echo "  - Main log: ${MAIN_LOG}"
        echo "  - Summary: ${SUMMARY_LOG}"
        echo "  - Errors: ${ERROR_LOG}"
        echo ""
        echo "To view detailed results: cat ${MAIN_LOG}"
        echo "To view only errors: cat ${ERROR_LOG}"
        
    } | tee "${SUMMARY_LOG}"
}

# Main script execution
main() {
    print_status "${GREEN}" "=========================================="
    print_status "${GREEN}" "IWFM Package Unit Test Runner"
    print_status "${GREEN}" "Started: $(date)"
    print_status "${GREEN}" "=========================================="
    
    # Check environment
    check_python_env
    
    # Change to script directory
    cd "${SCRIPT_DIR}" || exit 1
    
    # Initialize counters
    local total_files=0
    local passed_files=0
    local failed_files=0
    
    print_status "${YELLOW}" "Test directory: ${TEST_DIR}"
    print_status "${YELLOW}" "Python command: ${PYTHON_CMD}"
    print_status "${YELLOW}" "Logs will be saved to: ${LOG_DIR}"
    echo ""
    
    # Find and run individual test files
    if [[ -d "${TEST_DIR}" ]]; then
        for test_file in "${TEST_DIR}"/test_*.py; do
            if [[ -f "${test_file}" ]]; then
                ((total_files++))
                if run_test_file "${test_file}"; then
                    ((passed_files++))
                else
                    ((failed_files++))
                    # Extract errors to separate log
                    echo "=== Errors from $(basename "${test_file}") ===" >> "${ERROR_LOG}"
                    grep -A 5 -B 5 "FAILED\|ERROR\|AssertionError\|Exception" "${MAIN_LOG}" | tail -20 >> "${ERROR_LOG}"
                fi
                echo "" >> "${MAIN_LOG}"
            fi
        done
    else
        print_status "${RED}" "ERROR: Test directory ${TEST_DIR} not found"
        exit 1
    fi
    
    echo "" | tee -a "${MAIN_LOG}"
    print_status "${BLUE}" "=========================================="
    print_status "${BLUE}" "Running comprehensive test suite..."
    print_status "${BLUE}" "=========================================="
    
    # Run all tests together for final summary
    run_all_tests
    
    echo "" | tee -a "${MAIN_LOG}"
    print_status "${GREEN}" "=========================================="
    print_status "${GREEN}" "Test run completed: $(date)"
    print_status "${GREEN}" "=========================================="
    
    # Generate summary
    generate_summary "${total_files}" "${passed_files}" "${failed_files}"
    
    # Set exit code based on results
    if [[ ${failed_files} -eq 0 ]]; then
        print_status "${GREEN}" "All tests passed! 🎉"
        exit 0
    else
        print_status "${RED}" "Some tests failed. Check ${ERROR_LOG} for details."
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --clean        Clean previous test logs"
        echo "  --install-deps Install test dependencies"
        echo ""
        echo "Environment variables:"
        echo "  PYTEST_ARGS   Additional arguments to pass to pytest"
        echo ""
        echo "Examples:"
        echo "  $0                    # Run all tests"
        echo "  $0 --clean           # Clean logs and run tests"
        echo "  PYTEST_ARGS='-x' $0  # Stop on first failure"
        exit 0
        ;;
    --clean)
        print_status "${YELLOW}" "Cleaning previous test logs..."
        rm -rf "${LOG_DIR}"
        mkdir -p "${LOG_DIR}"
        ;;
    --install-deps)
        print_status "${YELLOW}" "Installing test dependencies..."
        "${PYTHON_CMD}" -m pip install pytest coverage pytest-cov
        exit 0
        ;;
esac

# Run main function
main "$@"