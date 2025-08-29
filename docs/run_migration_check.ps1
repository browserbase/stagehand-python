# PowerShell script to run migration analysis and validation
# Usage: .\docs\run_migration_check.ps1 [path_to_analyze]

param(
    [string]$Path = ".",
    [switch]$Validate,
    [switch]$Help
)

if ($Help) {
    Write-Host "Stagehand Migration Helper" -ForegroundColor Green
    Write-Host "=========================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\docs\run_migration_check.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Path <path>     Path to analyze (default: current directory)"
    Write-Host "  -Validate        Run migration validation after analysis"
    Write-Host "  -Help           Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\docs\run_migration_check.ps1                    # Analyze current directory"
    Write-Host "  .\docs\run_migration_check.ps1 -Path .\examples   # Analyze examples directory"
    Write-Host "  .\docs\run_migration_check.ps1 -Validate          # Run analysis and validation"
    exit 0
}

Write-Host "🔍 Stagehand Migration Analysis" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Run migration analysis
Write-Host ""
Write-Host "Running migration analysis on: $Path" -ForegroundColor Yellow
Write-Host ""

try {
    python docs/migration_utility.py $Path
    $analysisResult = $LASTEXITCODE
} catch {
    Write-Host "❌ Failed to run migration analysis: $_" -ForegroundColor Red
    exit 1
}

# Run validation if requested
if ($Validate) {
    Write-Host ""
    Write-Host "Running migration validation..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        python docs/validate_migration.py
        $validationResult = $LASTEXITCODE
    } catch {
        Write-Host "❌ Failed to run migration validation: $_" -ForegroundColor Red
        exit 1
    }
    
    if ($validationResult -eq 0) {
        Write-Host ""
        Write-Host "🎉 Migration validation completed successfully!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Migration validation completed with issues." -ForegroundColor Yellow
        Write-Host "Please review the output above and address any errors." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📚 Additional Resources:" -ForegroundColor Cyan
Write-Host "• Migration Guide: docs/migration_guide.md"
Write-Host "• Troubleshooting: docs/troubleshooting.md"
Write-Host "• Examples: examples/ directory"

if ($analysisResult -ne 0 -or ($Validate -and $validationResult -ne 0)) {
    exit 1
} else {
    exit 0
}