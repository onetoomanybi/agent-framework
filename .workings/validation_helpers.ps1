# Validation Helpers - PowerShell
# Used by baby steps to validate project against gap analysis

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("1", "3", "4", "5", "all")]
    [string]$Phase = "all",
    
    [Parameter(Mandatory=$false)]
    [string]$ProjectRoot = "."
)

# ===== UTILITY FUNCTIONS =====

function Write-ValidationResult {
    param(
        [Parameter(Mandatory=$true)]
        [bool]$Passed,
        
        [Parameter(Mandatory=$true)]
        [string]$Message,
        
        [Parameter(Mandatory=$false)]
        [int]$GapNumber = $null
    )
    
    $icon = if ($Passed) { "✅" } else { "❌" }
    $gapRef = if ($GapNumber) { " (Gap #$GapNumber)" } else { "" }
    Write-Host "$icon $Message$gapRef"
}

function Test-FileExists {
    param([string]$FilePath)
    Test-Path -Path $FilePath -PathType Leaf
}

function Get-FileContent {
    param([string]$FileName)
    $filePath = Join-Path $ProjectRoot $FileName
    if (-not (Test-FileExists $filePath)) {
        throw "File not found: $FileName"
    }
    Get-Content $filePath -Raw
}

# ===== PHASE 1 VALIDATORS =====

function Test-ImportGuard {
    # Check 1.1a: Import guard exists (Gap #6)
    try {
        $content = Get-FileContent "fabric_ai_foundry_client.py"
        $hasTry = $content -match "try:"
        $hasImport = $content -match "import notebookutils"
        $hasExcept = $content -match "except ImportError"
        
        if ($hasTry -and $hasImport -and $hasExcept) {
            Write-ValidationResult $true "Import guard present (try/except for notebookutils)" -GapNumber 6
            return $true
        } else {
            Write-ValidationResult $false "Import guard missing or incomplete" -GapNumber 6
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking import guard: $_" -GapNumber 6
        return $false
    }
}

function Test-MockCredentials {
    # Check 1.1b: Mock credentials available (Gap #6)
    try {
        $content = Get-FileContent "fabric_ai_foundry_client.py"
        $hasMock = $content -match "MockNotebookUtils|class.*credentials"
        $hasCredential = $content -match "class FabricMLCredential"
        
        if ($hasMock -and $hasCredential) {
            Write-ValidationResult $true "Mock credentials and FabricMLCredential class present" -GapNumber 6
            return $true
        } else {
            Write-ValidationResult $false "Mock credentials or FabricMLCredential class missing" -GapNumber 6
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking mock credentials: $_" -GapNumber 6
        return $false
    }
}

function Test-NoHardcodedSecrets {
    # Check 1.1c: No hardcoded credentials (Gap #3)
    try {
        $filesToCheck = @("fabric_ai_foundry_client.py", "agent_lakehouse_tools.py", "function_app.py")
        $foundSecrets = @()
        
        foreach ($fileName in $filesToCheck) {
            try {
                $content = Get-FileContent $fileName
                
                if ($content -match 'password\s*=\s*["\']' -or
                    $content -match 'api_key\s*=\s*["\']' -or
                    $content -match 'secret\s*=\s*["\']' -or
                    $content -match 'token\s*=\s*["\'].*["\']') {
                    $foundSecrets += $fileName
                }
            }
            catch {
                # File doesn't exist, skip
            }
        }
        
        if ($foundSecrets.Count -eq 0) {
            Write-ValidationResult $true "No hardcoded credentials found" -GapNumber 3
            return $true
        } else {
            Write-ValidationResult $false "Hardcoded credentials found in: $($foundSecrets -join ', ')" -GapNumber 3
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking secrets: $_" -GapNumber 3
        return $false
    }
}

function Test-SDKVersion {
    # Check 1.2a: Verify Azure AI Projects SDK installed (Gap #1)
    try {
        $output = & pip show azure-ai-projects 2>$null
        
        if ($output -and $output -match "Version: 1\.") {
            Write-ValidationResult $true "Azure AI Projects SDK v1.0.0+ installed" -GapNumber 1
            return $true
        } else {
            Write-ValidationResult $false "Azure AI Projects SDK not found or wrong version" -GapNumber 1
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking SDK: $_" -GapNumber 1
        return $false
    }
}

function Test-NoDeprecatedPatterns {
    # Check 1.2b: No deprecated connection_string usage (Gap #2)
    try {
        $content = Get-FileContent "fabric_ai_foundry_client.py"
        
        if ($content -match "from_connection_string") {
            Write-ValidationResult $false "Deprecated from_connection_string() found" -GapNumber 2
            return $false
        }
        
        if ($content -match "endpoint=" -and $content -match "DefaultAzureCredential") {
            Write-ValidationResult $true "Using modern endpoint + DefaultAzureCredential pattern (not deprecated connection_string)" -GapNumber 2
            return $true
        } else {
            Write-ValidationResult $false "Missing modern endpoint + DefaultAzureCredential pattern" -GapNumber 2
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking deprecated patterns: $_" -GapNumber 2
        return $false
    }
}

function Test-CSVParsingRobust {
    # Check 1.3a: CSV parsing uses pandas (Gap Context)
    try {
        $content = Get-FileContent "agent_lakehouse_tools.py"
        
        $hasPandasImport = $content -match "import pandas|from pandas"
        $hasPandasRead = $content -match "pd\.read_csv"
        $hasNaiveSplit = $content -match "split\(','\)"
        
        if ($hasPandasImport -and $hasPandasRead -and -not $hasNaiveSplit) {
            Write-ValidationResult $true "CSV parsing uses pandas (not naive split)"
            return $true
        } else {
            Write-ValidationResult $false "CSV parsing not using pandas or still has naive split"
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking CSV parsing: $_"
        return $false
    }
}

function Test-PaginationSupport {
    # Check 1.4a: Pagination parameters present (Gap #8)
    try {
        $content = Get-FileContent "agent_lakehouse_tools.py"
        
        $hasLimit = $content -match "limit"
        $hasOffset = $content -match "offset|skip"
        
        if ($hasLimit -and $hasOffset) {
            Write-ValidationResult $true "Pagination parameters (limit/offset) present" -GapNumber 8
            return $true
        } else {
            Write-ValidationResult $false "Pagination parameters not found" -GapNumber 8
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking pagination: $_" -GapNumber 8
        return $false
    }
}

# ===== PHASE 3 VALIDATORS =====

function Test-OperationIdsPresent {
    # Check 3.1a: Every operation has operationId (Gap #5 - CRITICAL)
    try {
        $specPath = Join-Path $ProjectRoot "openapi_spec.json"
        $spec = Get-Content $specPath | ConvertFrom-Json
        
        $missingOperations = @()
        foreach ($path in $spec.paths.PSObject.Properties) {
            foreach ($method in $path.Value.PSObject.Properties) {
                if ($method.Value -is [PSCustomObject]) {
                    if (-not $method.Value.operationId) {
                        $missingOperations += "$($method.Name.ToUpper()) $($path.Name)"
                    }
                }
            }
        }
        
        if ($missingOperations.Count -eq 0) {
            Write-ValidationResult $true "All operations have operationId (required for Azure AI Agents Service)" -GapNumber 5
            return $true
        } else {
            Write-ValidationResult $false "Missing operationId on: $($missingOperations -join ', ')" -GapNumber 5
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking operationIds: $_" -GapNumber 5
        return $false
    }
}

function Test-OnlyGETandPOST {
    # Check 3.1b: Only GET/POST methods (Gap #9)
    try {
        $specPath = Join-Path $ProjectRoot "openapi_spec.json"
        $spec = Get-Content $specPath | ConvertFrom-Json
        
        $unsupportedMethods = @()
        foreach ($path in $spec.paths.PSObject.Properties) {
            foreach ($method in $path.Value.PSObject.Properties) {
                if ($method.Name.ToLower() -notin @("get", "post", "parameters", "servers")) {
                    $unsupportedMethods += "$($method.Name.ToUpper()) on $($path.Name)"
                }
            }
        }
        
        if ($unsupportedMethods.Count -eq 0) {
            Write-ValidationResult $true "Only GET/POST methods present (Azure AI Agents Service support)" -GapNumber 9
            return $true
        } else {
            Write-ValidationResult $false "Unsupported HTTP methods found: $($unsupportedMethods -join ', ')" -GapNumber 9
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking HTTP methods: $_" -GapNumber 9
        return $false
    }
}

function Test-ServerUrlAccessible {
    # Check 3.1c: Server URL format (Gap #7)
    try {
        $specPath = Join-Path $ProjectRoot "openapi_spec.json"
        $spec = Get-Content $specPath | ConvertFrom-Json
        
        if ($spec.servers.Count -eq 0) {
            Write-ValidationResult $false "No servers defined in OpenAPI spec" -GapNumber 7
            return $false
        }
        
        $serverUrl = $spec.servers[0].url
        if ($serverUrl -match "localhost|127\.0\.0\.1") {
            Write-ValidationResult $false "Server URL is localhost: $serverUrl (must be accessible from AI Foundry)" -GapNumber 7
            return $false
        }
        
        Write-ValidationResult $true "Server URL format appropriate for hosting: $serverUrl" -GapNumber 7
        return $true
    }
    catch {
        Write-ValidationResult $false "Error checking server URL: $_" -GapNumber 7
        return $false
    }
}

# ===== PHASE 4 VALIDATORS =====

function Test-RetryLogicPresent {
    # Check 4.1a: Retry logic implemented (Gap #8)
    try {
        $content = Get-FileContent "agent_lakehouse_tools.py"
        
        $hasRetry = $content -match "retry|attempt"
        $hasTimeout = $content -match "timeout"
        
        if ($hasRetry -and $hasTimeout) {
            Write-ValidationResult $true "Retry logic and timeout configuration present" -GapNumber 8
            return $true
        } else {
            Write-ValidationResult $false "Retry logic or timeout configuration missing" -GapNumber 8
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking retry logic: $_" -GapNumber 8
        return $false
    }
}

function Test-LoggingPresent {
    # Check 4.1c: Logging for observability (Gap #10)
    try {
        $content = Get-FileContent "agent_lakehouse_tools.py"
        
        $hasImport = $content -match "import logging"
        $hasLogger = $content -match "logger"
        $hasLogCalls = $content -match "logger\.info|logger\.debug"
        
        if ($hasImport -and $hasLogger -and $hasLogCalls) {
            Write-ValidationResult $true "Logging implemented for observability (info/debug level)" -GapNumber 10
            return $true
        } else {
            Write-ValidationResult $false "Logging not properly implemented" -GapNumber 10
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking logging: $_" -GapNumber 10
        return $false
    }
}

function Test-GUIDvsNames {
    # Check 4.2a: Using GUIDs not names (Gap #12)
    try {
        $content = Get-FileContent "agent_lakehouse_tools.py"
        
        $hasGUID = $content -match "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
        $usesWorkspaceName = $content -match "workspace_name"
        $usesLakehouseName = $content -match "lakehouse_name"
        
        if ($hasGUID -and -not ($usesWorkspaceName -or $usesLakehouseName)) {
            Write-ValidationResult $true "Uses GUIDs for resource identification (immutable, not names)" -GapNumber 12
            return $true
        } else {
            Write-ValidationResult $false "Using resource names instead of GUIDs (breaks on rename)" -GapNumber 12
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking GUID usage: $_" -GapNumber 12
        return $false
    }
}

# ===== PHASE 5 VALIDATORS =====

function Test-ProductClarity {
    # Check 5.0a: Product is clearly Azure AI Agents Service (Gap #1)
    try {
        $content = Get-FileContent "requirements.txt"
        
        if ($content -match "azure-ai-projects") {
            Write-ValidationResult $true "Using Azure AI Agents Service (azure-ai-projects SDK)" -GapNumber 1
            return $true
        } else {
            Write-ValidationResult $false "Azure AI Agents Service SDK (azure-ai-projects) not in requirements" -GapNumber 1
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking product: $_" -GapNumber 1
        return $false
    }
}

function Test-OTelPresent {
    # Check 5.3a: OpenTelemetry instrumentation (Gap #10)
    try {
        $content = Get-FileContent "requirements.txt"
        
        if ($content -match "opentelemetry|azure-monitor") {
            Write-ValidationResult $true "OpenTelemetry/Application Insights instrumentation configured" -GapNumber 10
            return $true
        } else {
            Write-ValidationResult $false "OpenTelemetry/Application Insights not configured" -GapNumber 10
            return $false
        }
    }
    catch {
        Write-ValidationResult $false "Error checking observability: $_" -GapNumber 10
        return $false
    }
}

# ===== PHASE EXECUTION =====

function Invoke-Phase1Validation {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "PHASE 1: Fix Critical Issues - Baby Step Validation" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $results = @()
    $results += Test-ImportGuard
    $results += Test-MockCredentials
    $results += Test-NoHardcodedSecrets
    $results += Test-SDKVersion
    $results += Test-NoDeprecatedPatterns
    $results += Test-CSVParsingRobust
    $results += Test-PaginationSupport
    
    $passed = @($results | Where-Object { $_ -eq $true }).Count
    Write-Host ""
    Write-Host "PHASE 1 Summary: $passed/$($results.Count) checks passed" -ForegroundColor Yellow
    Write-Host ""
}

function Invoke-Phase3Validation {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "PHASE 3: OpenAPI Specification - Baby Step Validation" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $results = @()
    $results += Test-OperationIdsPresent
    $results += Test-OnlyGETandPOST
    $results += Test-ServerUrlAccessible
    
    $passed = @($results | Where-Object { $_ -eq $true }).Count
    Write-Host ""
    Write-Host "PHASE 3 Summary: $passed/$($results.Count) checks passed" -ForegroundColor Yellow
    Write-Host ""
}

function Invoke-Phase4Validation {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "PHASE 4: Resilience & Monitoring - Baby Step Validation" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $results = @()
    $results += Test-RetryLogicPresent
    $results += Test-LoggingPresent
    $results += Test-GUIDvsNames
    
    $passed = @($results | Where-Object { $_ -eq $true }).Count
    Write-Host ""
    Write-Host "PHASE 4 Summary: $passed/$($results.Count) checks passed" -ForegroundColor Yellow
    Write-Host ""
}

function Invoke-Phase5Validation {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "PHASE 5: Pre-Deployment - Baby Step Validation" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    $results = @()
    $results += Test-ProductClarity
    $results += Test-OTelPresent
    
    $passed = @($results | Where-Object { $_ -eq $true }).Count
    Write-Host ""
    Write-Host "PHASE 5 Summary: $passed/$($results.Count) checks passed" -ForegroundColor Yellow
    Write-Host ""
}

# Main execution
switch ($Phase) {
    "1" { Invoke-Phase1Validation }
    "3" { Invoke-Phase3Validation }
    "4" { Invoke-Phase4Validation }
    "5" { Invoke-Phase5Validation }
    "all" {
        Invoke-Phase1Validation
        Invoke-Phase3Validation
        Invoke-Phase4Validation
        Invoke-Phase5Validation
    }
    default {
        Write-Host "Usage: .\validation_helpers.ps1 -Phase [1|3|4|5|all]"
    }
}
