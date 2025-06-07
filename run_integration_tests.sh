#!/bin/bash

# Integration Test Runner for Stagehand Python
# This script helps run integration tests locally with different configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --local          Run only local integration tests (default)"
    echo "  --browserbase    Run only Browserbase integration tests"
    echo "  --all            Run all integration tests"
    echo "  --slow           Include slow tests"
    echo "  --e2e            Run end-to-end tests"
    echo "  --observe        Run only observe tests"
    echo "  --act            Run only act tests"
    echo "  --extract        Run only extract tests"
    echo "  --smoke          Run smoke tests"
    echo "  --coverage       Generate coverage report"
    echo "  --verbose        Verbose output"
    echo "  --help           Show this help"
    echo ""
    echo "Environment variables:"
    echo "  BROWSERBASE_API_KEY     Browserbase API key"
    echo "  BROWSERBASE_PROJECT_ID  Browserbase project ID"
    echo "  MODEL_API_KEY          API key for AI model"
    echo "  OPENAI_API_KEY         OpenAI API key"
    echo ""
    echo "Examples:"
    echo "  $0 --local                Run basic local tests"
    echo "  $0 --browserbase          Run Browserbase tests"
    echo "  $0 --all --coverage       Run all tests with coverage"
    echo "  $0 --observe --local      Run only observe tests locally"
    echo "  $0 --slow --local         Run slow local tests"
}

# Default values
RUN_LOCAL=true
RUN_BROWSERBASE=false
RUN_SLOW=false
RUN_E2E=false
RUN_SMOKE=false
GENERATE_COVERAGE=false
VERBOSE=false
TEST_TYPE=""
MARKERS=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --local)
            RUN_LOCAL=true
            RUN_BROWSERBASE=false
            shift
            ;;
        --browserbase)
            RUN_LOCAL=false
            RUN_BROWSERBASE=true
            shift
            ;;
        --all)
            RUN_LOCAL=true
            RUN_BROWSERBASE=true
            shift
            ;;
        --slow)
            RUN_SLOW=true
            shift
            ;;
        --e2e)
            RUN_E2E=true
            shift
            ;;
        --observe)
            TEST_TYPE="observe"
            shift
            ;;
        --act)
            TEST_TYPE="act"
            shift
            ;;
        --extract)
            TEST_TYPE="extract"
            shift
            ;;
        --smoke)
            RUN_SMOKE=true
            shift
            ;;
        --coverage)
            GENERATE_COVERAGE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

print_section "Stagehand Python Integration Test Runner"

# Check dependencies
print_section "Checking Dependencies"

if ! command -v python &> /dev/null; then
    print_error "Python is not installed"
    exit 1
fi
print_success "Python found: $(python --version)"

if ! command -v pytest &> /dev/null; then
    print_error "pytest is not installed. Run: pip install pytest"
    exit 1
fi
print_success "pytest found: $(pytest --version)"

if ! command -v playwright &> /dev/null; then
    print_error "Playwright is not installed. Run: pip install playwright && playwright install"
    exit 1
fi
print_success "Playwright found"

# Check environment variables
print_section "Environment Check"

if [[ "$RUN_LOCAL" == true ]]; then
    if [[ -z "$MODEL_API_KEY" && -z "$OPENAI_API_KEY" ]]; then
        print_warning "No MODEL_API_KEY or OPENAI_API_KEY found. Some tests may fail."
    else
        print_success "AI model API key found"
    fi
fi

if [[ "$RUN_BROWSERBASE" == true ]]; then
    if [[ -z "$BROWSERBASE_API_KEY" || -z "$BROWSERBASE_PROJECT_ID" ]]; then
        print_error "BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID are required for Browserbase tests"
        exit 1
    else
        print_success "Browserbase credentials found"
    fi
fi

# Build test markers
build_markers() {
    local markers_list=()
    
    if [[ "$RUN_LOCAL" == true && "$RUN_BROWSERBASE" == false ]]; then
        markers_list+=("local")
    elif [[ "$RUN_BROWSERBASE" == true && "$RUN_LOCAL" == false ]]; then
        markers_list+=("browserbase")
    fi
    
    if [[ "$RUN_SLOW" == false ]]; then
        markers_list+=("not slow")
    fi
    
    if [[ "$RUN_E2E" == true ]]; then
        markers_list+=("e2e")
    fi
    
    if [[ "$RUN_SMOKE" == true ]]; then
        markers_list+=("smoke")
    fi
    
    # Join markers with " and " properly
    if [[ ${#markers_list[@]} -gt 0 ]]; then
        local first=true
        MARKERS=""
        for marker in "${markers_list[@]}"; do
            if [[ "$first" == true ]]; then
                MARKERS="$marker"
                first=false
            else
                MARKERS="$MARKERS and $marker"
            fi
        done
    fi
}

# Build test path
build_test_path() {
    local test_path="tests/integration/"
    
    if [[ -n "$TEST_TYPE" ]]; then
        test_path="${test_path}test_${TEST_TYPE}_integration.py"
    fi
    
    echo "$test_path"
}

# Run tests
run_tests() {
    local test_path=$(build_test_path)
    build_markers
    
    print_section "Running Tests"
    print_success "Test path: $test_path"
    
    if [[ -n "$MARKERS" ]]; then
        print_success "Test markers: $MARKERS"
    fi
    
    # Build pytest command
    local pytest_cmd="pytest $test_path"
    
    if [[ -n "$MARKERS" ]]; then
        pytest_cmd="$pytest_cmd -m \"$MARKERS\""
    fi
    
    if [[ "$VERBOSE" == true ]]; then
        pytest_cmd="$pytest_cmd -v -s"
    else
        pytest_cmd="$pytest_cmd -v"
    fi
    
    if [[ "$GENERATE_COVERAGE" == true ]]; then
        pytest_cmd="$pytest_cmd --cov=stagehand --cov-report=html --cov-report=term-missing"
    fi
    
    pytest_cmd="$pytest_cmd --tb=short --maxfail=5"
    
    echo "Running: $pytest_cmd"
    echo ""
    
    # Execute the command
    eval $pytest_cmd
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed (exit code: $exit_code)"
        exit $exit_code
    fi
}

# Generate summary
generate_summary() {
    print_section "Test Summary"
    
    if [[ "$RUN_LOCAL" == true ]]; then
        print_success "Local tests: Enabled"
    fi
    
    if [[ "$RUN_BROWSERBASE" == true ]]; then
        print_success "Browserbase tests: Enabled"
    fi
    
    if [[ "$RUN_SLOW" == true ]]; then
        print_success "Slow tests: Included"
    fi
    
    if [[ -n "$TEST_TYPE" ]]; then
        print_success "Test type: $TEST_TYPE"
    fi
    
    if [[ "$GENERATE_COVERAGE" == true ]]; then
        print_success "Coverage report generated: htmlcov/index.html"
    fi
}

# Main execution
main() {
    run_tests
    generate_summary
}

# Run main function
main 