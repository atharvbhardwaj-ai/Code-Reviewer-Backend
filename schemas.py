from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class SeverityLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class CodeFinding(BaseModel):
    line_number: Optional[int] = Field(
        default=None, 
        description="Line number where the issue occurs, or null if it applies across the whole snippet."
    )
    severity: SeverityLevel = Field(
        description="Severity level: HIGH (-15 pts), MEDIUM (-5 pts), LOW (-2 pts)."
    )
    category: str = Field(
        description="Category such as 'Memory Leak', 'SQL Injection', 'Complexity', or 'Style'."
    )
    title: str = Field(
        description="Short, clear title describing the flaw."
    )
    description: str = Field(
        description="Detailed explanation of the flaw, inefficiency, or vulnerability."
    )
    suggested_fix: str = Field(
        description="Actionable guidance on how to fix or refactor the issue."
    )

class AuditReport(BaseModel):
    is_valid_code: bool = Field(
        description="True if the input is recognizable source code; False if natural language text, essays, or junk."
    )
    rejection_reason: Optional[str] = Field(
        default=None, 
        description="Explanation if the input fails the validation gate."
    )
    language_detected: Optional[str] = Field(
        default=None, 
        description="Programming language detected (e.g., C++, Python, Java, JavaScript, Go)."
    )
    health_score: Optional[int] = Field(
        default=100, 
        description="Calculated health score between 0 and 100 based on detected issue severities."
    )
    passed_checks: Optional[int] = Field(
        default=0, 
        description="Estimated count of standard code-quality benchmarks passed (e.g., bounds safety, clean syntax)."
    )
    summary: Optional[str] = Field(
        default=None, 
        description="Executive 2-sentence summary of the code quality and audit outcome."
    )
    findings: List[CodeFinding] = Field(
        default_factory=list, 
        description="List of detected bugs, vulnerabilities, and optimization opportunities."
    )
    time_complexity_current: Optional[str] = Field(
        default=None, 
        description="Estimated current Big-O time complexity (e.g., O(N^2))."
    )
    time_complexity_optimized: Optional[str] = Field(
        default=None, 
        description="Achievable Big-O time complexity after refactoring (e.g., O(N log N))."
    )
    space_complexity_current: Optional[str] = Field(
        default=None, 
        description="Estimated current Big-O auxiliary space complexity (e.g., O(N))."
    )
    space_complexity_optimized: Optional[str] = Field(
        default=None, 
        description="Achievable Big-O auxiliary space complexity after refactoring (e.g., O(1))."
    )
    refactored_code: Optional[str] = Field(
        default=None, 
        description="Complete, corrected, and clean refactored version of the input code."
    )