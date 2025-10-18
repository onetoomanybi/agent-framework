# Validation Helpers - Python
# Used by baby steps to validate project against gap analysis

import os
import sys
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class ValidationResult:
    """Simple result container for validation checks"""
    def __init__(self, passed: bool, message: str, gap_number: Optional[int] = None):
        self.passed = passed
        self.message = message
        self.gap_number = gap_number
    
    def print_result(self):
        icon = "[PASS]" if self.passed else "[FAIL]"
        gap_ref = f" (Gap #{self.gap_number})" if self.gap_number else ""
        print(f"{icon} {self.message}{gap_ref}")


class GapAwareValidator:
    """Base class for all gap-aware validators"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.results: List[ValidationResult] = []
    
    def load_file(self, filename: str) -> str:
        """Load file content"""
        filepath = self.project_root / filename
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        return filepath.read_text()
    
    def add_result(self, result: ValidationResult):
        """Add a validation result"""
        self.results.append(result)
        result.print_result()
    
    def print_summary(self, phase: str):
        """Print validation summary"""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print(f"\n=== {phase} Summary: {passed}/{total} checks passed ===\n")


class Phase1Validator(GapAwareValidator):
    """Validators for Phase 1: Fix Critical Issues"""
    
    def check_import_guard(self) -> ValidationResult:
        """Check 1.1a: Import guard exists (Gap #6)"""
        try:
            content = self.load_file("fabric_ai_foundry_client.py")
            
            # Must have try/except for notebookutils
            has_try = "try:" in content
            has_import = "import notebookutils" in content
            has_except = "except ImportError" in content
            
            if has_try and has_import and has_except:
                return ValidationResult(
                    True, 
                    "Import guard present (try/except for notebookutils)",
                    gap_number=6
                )
            else:
                return ValidationResult(
                    False,
                    "Import guard missing or incomplete",
                    gap_number=6
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking import guard: {e}", gap_number=6)
    
    def check_mock_credentials(self) -> ValidationResult:
        """Check 1.1b: Mock credentials available (Gap #6)"""
        try:
            content = self.load_file("fabric_ai_foundry_client.py")
            
            # Must have mock class when notebookutils unavailable
            has_mock = "MockNotebookUtils" in content or "class " in content and "credentials" in content
            
            # Must have FabricMLCredential class
            has_credential = "class FabricMLCredential" in content
            
            if has_mock and has_credential:
                return ValidationResult(
                    True,
                    "Mock credentials and FabricMLCredential class present",
                    gap_number=6
                )
            else:
                return ValidationResult(
                    False,
                    "Mock credentials or FabricMLCredential class missing",
                    gap_number=6
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking mock credentials: {e}", gap_number=6)
    
    def check_no_hardcoded_secrets(self) -> ValidationResult:
        """Check 1.1c: No hardcoded credentials (Gap #3)"""
        try:
            files_to_check = [
                "fabric_ai_foundry_client.py",
                "agent_lakehouse_tools.py",
                "function_app.py"
            ]
            
            secret_patterns = [
                r'password\s*=\s*["\']',
                r'api_key\s*=\s*["\']',
                r'secret\s*=\s*["\']',
                r'token\s*=\s*["\'].*["\']',
            ]
            
            found_secrets = []
            for filename in files_to_check:
                try:
                    content = self.load_file(filename)
                    for pattern in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            found_secrets.append(filename)
                            break
                except FileNotFoundError:
                    pass
            
            if not found_secrets:
                return ValidationResult(
                    True,
                    "No hardcoded credentials found",
                    gap_number=3
                )
            else:
                return ValidationResult(
                    False,
                    f"Hardcoded credentials found in: {', '.join(found_secrets)}",
                    gap_number=3
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking secrets: {e}", gap_number=3)
    
    def check_sdk_version(self) -> ValidationResult:
        """Check 1.2a: Verify Azure AI Projects SDK installed (Gap #1)"""
        try:
            import subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "azure-ai-projects"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and "1.0.0" in result.stdout:
                return ValidationResult(
                    True,
                    "Azure AI Projects SDK v1.0.0+ installed",
                    gap_number=1
                )
            else:
                return ValidationResult(
                    False,
                    "Azure AI Projects SDK not found or wrong version",
                    gap_number=1
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking SDK: {e}", gap_number=1)
    
    def check_no_deprecated_patterns(self) -> ValidationResult:
        """Check 1.2b: No deprecated connection_string usage (Gap #2)"""
        try:
            content = self.load_file("fabric_ai_foundry_client.py")
            
            # Check for deprecated pattern
            if "from_connection_string" in content:
                return ValidationResult(
                    False,
                    "Deprecated from_connection_string() found",
                    gap_number=2
                )
            
            # Check for modern pattern
            if "endpoint=" in content and "DefaultAzureCredential" in content:
                return ValidationResult(
                    True,
                    "Using modern endpoint + DefaultAzureCredential pattern (not deprecated connection_string)",
                    gap_number=2
                )
            else:
                return ValidationResult(
                    False,
                    "Missing modern endpoint + DefaultAzureCredential pattern",
                    gap_number=2
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking deprecated patterns: {e}", gap_number=2)
    
    def check_csv_parsing_robust(self) -> ValidationResult:
        """Check 1.3a: CSV parsing uses pandas (Gap Context)"""
        try:
            content = self.load_file("agent_lakehouse_tools.py")
            
            # Check for pandas import and usage
            has_pandas_import = "import pandas" in content or "from pandas" in content
            has_pandas_read = "pd.read_csv" in content
            
            # Check for naive split (bad)
            has_naive_split = 'split(\',\')' in content
            
            if has_pandas_import and has_pandas_read and not has_naive_split:
                return ValidationResult(
                    True,
                    "CSV parsing uses pandas (not naive split)",
                    gap_number=None
                )
            else:
                return ValidationResult(
                    False,
                    "CSV parsing not using pandas or still has naive split",
                    gap_number=None
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking CSV parsing: {e}", gap_number=None)
    
    def check_pagination_support(self) -> ValidationResult:
        """Check 1.4a: Pagination parameters present (Gap #8)"""
        try:
            content = self.load_file("agent_lakehouse_tools.py")
            
            # Check for pagination parameters
            has_limit = "limit" in content
            has_offset = "offset" in content or "skip" in content
            
            if has_limit and (has_offset or "skip" in content):
                return ValidationResult(
                    True,
                    "Pagination parameters (limit/offset) present",
                    gap_number=8
                )
            else:
                return ValidationResult(
                    False,
                    "Pagination parameters not found",
                    gap_number=8
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking pagination: {e}", gap_number=8)


class Phase3Validator(GapAwareValidator):
    """Validators for Phase 3: OpenAPI Specification"""
    
    def load_openapi_spec(self) -> dict:
        """Load and parse OpenAPI spec"""
        content = self.load_file("openapi_spec.json")
        return json.loads(content)
    
    def check_operation_ids_present(self) -> ValidationResult:
        """Check 3.1a: Every operation has operationId (Gap #5 - CRITICAL)"""
        try:
            spec = self.load_openapi_spec()
            missing_operations = []
            
            for path, path_item in spec.get("paths", {}).items():
                for method, operation in path_item.items():
                    if isinstance(operation, dict) and "operationId" not in operation:
                        missing_operations.append(f"{method.upper()} {path}")
            
            if not missing_operations:
                return ValidationResult(
                    True,
                    "All operations have operationId (required for Azure AI Agents Service)",
                    gap_number=5
                )
            else:
                return ValidationResult(
                    False,
                    f"Missing operationId on: {', '.join(missing_operations)}",
                    gap_number=5
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking operationIds: {e}", gap_number=5)
    
    def check_only_get_post_methods(self) -> ValidationResult:
        """Check 3.1b: Only GET/POST methods (Gap #9)"""
        try:
            spec = self.load_openapi_spec()
            unsupported_methods = []
            
            for path, path_item in spec.get("paths", {}).items():
                for method in path_item.keys():
                    if method.lower() not in ["get", "post", "parameters", "servers"]:
                        unsupported_methods.append(f"{method.upper()} on {path}")
            
            if not unsupported_methods:
                return ValidationResult(
                    True,
                    "Only GET/POST methods present (Azure AI Agents Service support)",
                    gap_number=9
                )
            else:
                return ValidationResult(
                    False,
                    f"Unsupported HTTP methods found: {', '.join(unsupported_methods)}",
                    gap_number=9
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking HTTP methods: {e}", gap_number=9)
    
    def check_server_url_accessible(self) -> ValidationResult:
        """Check 3.1c: Server URL format (Gap #7)"""
        try:
            spec = self.load_openapi_spec()
            servers = spec.get("servers", [])
            
            if not servers:
                return ValidationResult(
                    False,
                    "No servers defined in OpenAPI spec",
                    gap_number=7
                )
            
            # Check first server URL is not localhost
            server_url = servers[0].get("url", "")
            if "localhost" in server_url or "127.0.0.1" in server_url:
                return ValidationResult(
                    False,
                    f"Server URL is localhost: {server_url} (must be accessible from AI Foundry)",
                    gap_number=7
                )
            
            return ValidationResult(
                True,
                f"Server URL format appropriate for hosting: {server_url}",
                gap_number=7
            )
        except Exception as e:
            return ValidationResult(False, f"Error checking server URL: {e}", gap_number=7)


class Phase4Validator(GapAwareValidator):
    """Validators for Phase 4: Resilience and GUID Usage"""
    
    def check_retry_logic_present(self) -> ValidationResult:
        """Check 4.1a: Retry logic implemented (Gap #8)"""
        try:
            content = self.load_file("agent_lakehouse_tools.py")
            
            # Check for retry keywords
            has_retry = "retry" in content.lower() or "attempt" in content.lower()
            has_timeout = "timeout" in content.lower()
            
            if has_retry and has_timeout:
                return ValidationResult(
                    True,
                    "Retry logic and timeout configuration present",
                    gap_number=8
                )
            else:
                return ValidationResult(
                    False,
                    "Retry logic or timeout configuration missing",
                    gap_number=8
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking retry logic: {e}", gap_number=8)
    
    def check_logging_present(self) -> ValidationResult:
        """Check 4.1c: Logging for observability (Gap #10)"""
        try:
            content = self.load_file("agent_lakehouse_tools.py")
            
            has_logging_import = "import logging" in content
            has_logger = "logger" in content.lower()
            has_log_calls = "logger.info" in content or "logger.debug" in content
            
            if has_logging_import and has_logger and has_log_calls:
                return ValidationResult(
                    True,
                    "Logging implemented for observability (info/debug level)",
                    gap_number=10
                )
            else:
                return ValidationResult(
                    False,
                    "Logging not properly implemented",
                    gap_number=10
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking logging: {e}", gap_number=10)
    
    def check_guid_vs_names(self) -> ValidationResult:
        """Check 4.2a: Using GUIDs not names (Gap #12)"""
        try:
            content = self.load_file("agent_lakehouse_tools.py")
            
            # GUID pattern
            guid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            
            # Check for GUID usage
            has_guid = re.search(guid_pattern, content, re.IGNORECASE) is not None
            
            # Check for name references (risky)
            uses_workspace_name = "workspace_name" in content
            uses_lakehouse_name = "lakehouse_name" in content
            
            if has_guid and not (uses_workspace_name or uses_lakehouse_name):
                return ValidationResult(
                    True,
                    "Uses GUIDs for resource identification (immutable, not names)",
                    gap_number=12
                )
            else:
                return ValidationResult(
                    False,
                    "Using resource names instead of GUIDs (breaks on rename)",
                    gap_number=12
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking GUID usage: {e}", gap_number=12)


class Phase5Validator(GapAwareValidator):
    """Validators for Phase 5: Pre-Deployment"""
    
    def check_product_clarity(self) -> ValidationResult:
        """Check 5.0a: Product is clearly Azure AI Agents Service (Gap #1)"""
        try:
            requirements = self.load_file("requirements.txt")
            
            # Must use azure-ai-projects, not agent-framework
            if "azure-ai-projects" in requirements:
                return ValidationResult(
                    True,
                    "Using Azure AI Agents Service (azure-ai-projects SDK)",
                    gap_number=1
                )
            else:
                return ValidationResult(
                    False,
                    "Azure AI Agents Service SDK (azure-ai-projects) not in requirements",
                    gap_number=1
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking product: {e}", gap_number=1)
    
    def check_otel_present(self) -> ValidationResult:
        """Check 5.3a: OpenTelemetry instrumentation (Gap #10)"""
        try:
            requirements = self.load_file("requirements.txt")
            
            has_otel = "opentelemetry" in requirements.lower() or "azure-monitor" in requirements
            
            if has_otel:
                return ValidationResult(
                    True,
                    "OpenTelemetry/Application Insights instrumentation configured",
                    gap_number=10
                )
            else:
                return ValidationResult(
                    False,
                    "OpenTelemetry/Application Insights not configured",
                    gap_number=10
                )
        except Exception as e:
            return ValidationResult(False, f"Error checking observability: {e}", gap_number=10)


# Main execution functions
def validate_phase_1(project_root: str = "."):
    """Run all Phase 1 validations"""
    print("\n" + "="*60)
    print("PHASE 1: Fix Critical Issues - Baby Step Validation")
    print("="*60 + "\n")
    
    validator = Phase1Validator(project_root)
    
    # Run all checks
    validator.add_result(validator.check_import_guard())
    validator.add_result(validator.check_mock_credentials())
    validator.add_result(validator.check_no_hardcoded_secrets())
    validator.add_result(validator.check_sdk_version())
    validator.add_result(validator.check_no_deprecated_patterns())
    validator.add_result(validator.check_csv_parsing_robust())
    validator.add_result(validator.check_pagination_support())
    
    validator.print_summary("PHASE 1")
    return validator


def validate_phase_3(project_root: str = "."):
    """Run all Phase 3 validations"""
    print("\n" + "="*60)
    print("PHASE 3: OpenAPI Specification - Baby Step Validation")
    print("="*60 + "\n")
    
    validator = Phase3Validator(project_root)
    
    validator.add_result(validator.check_operation_ids_present())
    validator.add_result(validator.check_only_get_post_methods())
    validator.add_result(validator.check_server_url_accessible())
    
    validator.print_summary("PHASE 3")
    return validator


def validate_phase_4(project_root: str = "."):
    """Run all Phase 4 validations"""
    print("\n" + "="*60)
    print("PHASE 4: Resilience & Monitoring - Baby Step Validation")
    print("="*60 + "\n")
    
    validator = Phase4Validator(project_root)
    
    validator.add_result(validator.check_retry_logic_present())
    validator.add_result(validator.check_logging_present())
    validator.add_result(validator.check_guid_vs_names())
    
    validator.print_summary("PHASE 4")
    return validator


def validate_phase_5(project_root: str = "."):
    """Run all Phase 5 validations"""
    print("\n" + "="*60)
    print("PHASE 5: Pre-Deployment - Baby Step Validation")
    print("="*60 + "\n")
    
    validator = Phase5Validator(project_root)
    
    validator.add_result(validator.check_product_clarity())
    validator.add_result(validator.check_otel_present())
    
    validator.print_summary("PHASE 5")
    return validator


if __name__ == "__main__":
    # Allow running specific phase or all
    if len(sys.argv) > 1:
        phase = sys.argv[1]
        if phase == "1":
            validate_phase_1(".")
        elif phase == "3":
            validate_phase_3(".")
        elif phase == "4":
            validate_phase_4(".")
        elif phase == "5":
            validate_phase_5(".")
        else:
            print("Usage: python validation_helpers.py [1|3|4|5]")
    else:
        # Run all phases
        validate_phase_1(".")
        validate_phase_3(".")
        validate_phase_4(".")
        validate_phase_5(".")
