import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from schemas import AuditReport, SeverityLevel

# Used for loading .env variables if present
load_dotenv()

class CodeAuditorEngine:
    def __init__(self):
        # Initializes the client using the GEMINI_API_KEY from your .env file
        self.client = genai.Client()
        # Using gemini-3.5-flash-lite for high throughput and reliable structured outputs
        self.model_name = "gemini-3.5-flash-lite"

    def audit_snippet(self, code: str, language: str = "Auto-detect", user_comments: str = "") -> AuditReport:
        # ---------------------------------------------------------
        # LAYER 1: DETERMINISTIC FAILSAFES (No API Quota Used)
        # ---------------------------------------------------------
        if not code or not code.strip():
            return AuditReport(
                is_valid_code=False,
                rejection_reason="No code provided. The input was empty.",
                health_score=0,
                findings=[]
            )

        # Hard limit to prevent massive file dumps causing timeouts
        if len(code) > 30000:
            return AuditReport(
                is_valid_code=False,
                rejection_reason="Code exceeds the maximum allowed length of 30,000 characters.",
                health_score=0,
                findings=[]
            )

        # ---------------------------------------------------------
        # LAYER 2: PROMPT ENGINEERING & CONTEXT INJECTION
        # ---------------------------------------------------------
        context_block = user_comments.strip() if user_comments.strip() else "None provided. Analyze against standard production best practices."
        
        prompt = f"""
You are an expert Senior Software Engineer and Security Auditor.
Review the following code snippet and return a structured JSON evaluation.

LANGUAGE SPECIFIED / DETECTED: {language}

DEVELOPER CONTEXT / CONSTRAINTS:
{context_block}

SOURCE CODE TO AUDIT:
{code}
INSTRUCTIONS:
1. VALIDATION GATE: Verify if the input is actual source code. If it is an essay, recipe, or random text, set is_valid_code to false and ignore remaining steps.
2. Analyze for security vulnerabilities, memory leaks, algorithmic inefficiencies, and structural flaws.
3. Determine the current and achievable optimized Big-O time and space complexity.
4. Provide a cleanly refactored version of the code that resolves the flagged issues.
"""
        # ---------------------------------------------------------
        # LAYER 3: STRUCTURED INFERENCE & SCORING
        # ---------------------------------------------------------
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AuditReport,
                    temperature=0.1, # Low temperature forces analytical, deterministic responses
                )
            )
            
            # The SDK automatically parses the JSON into your Pydantic AuditReport schema
            report: AuditReport = response.parsed
            
            # Post-processing: Calculate the exact Health Score deterministically
            if report.is_valid_code:
                score = 100
                for finding in report.findings:
                    if finding.severity == SeverityLevel.HIGH:
                        score -= 15
                    elif finding.severity == SeverityLevel.MEDIUM:
                        score -= 5
                    elif finding.severity == SeverityLevel.LOW:
                        score -= 2
                
                # Floor the score at 0
                report.health_score = max(0, score)
                
                # Arbitrary passed checks calculation based on lack of severe issues
                report.passed_checks = max(0, 20 - len(report.findings))

            return report

        except Exception as e:
            # Graceful fallback for network timeouts or API quota limits
            return AuditReport(
                is_valid_code=False,
                rejection_reason=f"Audit Engine API Error: {str(e)}",
                health_score=0,
                findings=[]
            )