import os
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from schemas import AuditReport
from auditor import CodeAuditorEngine

# Initialize the FastAPI app
app = FastAPI(
    title="Prism Audit Engine API",
    version="1.0.0",
    description="Automated Static Analysis and AI Security Review Pipeline"
)

# Enable CORS so NiceGUI Streamlit (port 8501) can query this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the auditor engine once at server startup
engine = CodeAuditorEngine()

# Extension-to-Language lookup table for file uploads
EXTENSION_MAP = {
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "React JSX",
    ".tsx": "React TSX",
    ".go": "Go",
    ".rs": "Rust",
    ".cs": "C#",
    ".php": "PHP",
    ".rb": "Ruby",
}


# -------------------------------------------------------------
# REQUEST SCHEMAS (Input Contracts)
# -------------------------------------------------------------
class AuditTextRequest(BaseModel):
    code: str = Field(..., description="Raw source code snippet to review.")
    language: Optional[str] = Field("Auto-detect", description="Target programming language.")
    user_comments: Optional[str] = Field("", description="Optional developer context or hardware constraints.")


# -------------------------------------------------------------
# API ROUTES
# -------------------------------------------------------------
@app.get("/")
def health_check():
    """Simple status check to confirm server is running."""
    return {
        "status": "online",
        "service": "PRISM Audit Engine",
        "engine_model": engine.model_name
    }


@app.post("/api/v1/audit", response_model=AuditReport)
def audit_text_snippet(payload: AuditTextRequest):
    """
    Audits source code passed directly as raw text.
    Used by the 'Paste Code' tab in the frontend.
    """
    report = engine.audit_snippet(
        code=payload.code,
        language=payload.language or "Auto-detect",
        user_comments=payload.user_comments or ""
    )
    return report


@app.post("/api/v1/audit-file", response_model=AuditReport)
async def audit_uploaded_file(
    file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    user_comments: Optional[str] = Form("")
):
    """
    Audits source code submitted as a file upload (.py, .cpp, .java, etc.).
    Automatically sniffs the programming language from the file extension.
    """
    # 1. Determine language from extension if not explicitly specified
    filename = file.filename or ""
    _, ext = os.path.splitext(filename.lower())

    resolved_language = language
    if not resolved_language or resolved_language == "Auto-detect":
        resolved_language = EXTENSION_MAP.get(ext, "Auto-detect")

    # 2. Safely read and decode file contents
    try:
        content_bytes = await file.read()
        raw_code = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            # Fallback for Windows-1252 / Latin-1 encoded legacy files
            raw_code = content_bytes.decode("latin-1")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Unable to decode file. Please ensure it is a valid UTF-8 text/source file."
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File read failure: {str(e)}")

    # 3. Forward to the auditor engine
    report = engine.audit_snippet(
        code=raw_code,
        language=resolved_language,
        user_comments=user_comments or ""
    )
    return report