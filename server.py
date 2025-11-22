#!/usr/bin/env python3
import sys
import base64
import uuid
import threading
from pathlib import Path
from typing import Annotated, Optional
from datetime import datetime, timedelta
from enum import Enum

from arcade_mcp_server import Context, MCPApp

sys.path.insert(0, str(Path(__file__).parent))

_diagram_jobs = {}
MAX_JOBS_IN_MEMORY = 3
JOB_EXPIRY_MINUTES = 10


class JobStatus(str, Enum):
    QUEUED = "queued"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"


def _cleanup_old_jobs():
    cutoff = datetime.now() - timedelta(minutes=JOB_EXPIRY_MINUTES)
    expired = [jid for jid, job in _diagram_jobs.items() if job.get("created", datetime.now()) < cutoff]
    for jid in expired:
        del _diagram_jobs[jid]
    
    if len(_diagram_jobs) > MAX_JOBS_IN_MEMORY:
        completed = [(jid, job.get("completed", datetime.min)) for jid, job in _diagram_jobs.items() if job.get("status") == JobStatus.COMPLETE]
        completed.sort(key=lambda x: x[1])
        for jid, _ in completed[:len(_diagram_jobs) - MAX_JOBS_IN_MEMORY]:
            del _diagram_jobs[jid]


def _generate_diagram_background(job_id, api_key, prompt, aspect_ratio, resolution, filename_prefix, output_dir):
    from generator import DiagramGenerator
    
    try:
        _diagram_jobs[job_id]["status"] = JobStatus.GENERATING
        _diagram_jobs[job_id]["started"] = datetime.now()
        
        generator = DiagramGenerator(api_key=api_key, output_dir=output_dir or Path.cwd())
        result = generator.generate_from_prompt(prompt, aspect_ratio, resolution, filename_prefix)
        
        if result.success:
            with open(result.file_path, 'rb') as f:
                image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            Path(result.file_path).unlink()
            
            _diagram_jobs[job_id]["status"] = JobStatus.COMPLETE
            _diagram_jobs[job_id]["completed"] = datetime.now()
            _diagram_jobs[job_id]["result"] = {
                "success": True,
                "width": result.width,
                "height": result.height,
                "model": result.model_used,
                "filename": Path(result.file_path).name,
                "base64": image_base64
            }
        else:
            _diagram_jobs[job_id]["status"] = JobStatus.FAILED
            _diagram_jobs[job_id]["completed"] = datetime.now()
            _diagram_jobs[job_id]["result"] = {"success": False, "error": result.error}
    except Exception as e:
        _diagram_jobs[job_id]["status"] = JobStatus.FAILED
        _diagram_jobs[job_id]["completed"] = datetime.now()
        _diagram_jobs[job_id]["result"] = {"success": False, "error": str(e)}


app = MCPApp(name="blueprint_mcp", version="3.0.0", log_level="INFO")


@app.tool(requires_secrets=["GOOGLE_API_KEY"])
def start_diagram_job(
    context: Context,
    description: Annotated[str, "Diagram description with specific components and labels"],
    diagram_type: Annotated[Optional[str], "Type: architecture, flowchart, data_flow, sequence, infographic, generic"] = "generic",
    aspect_ratio: Annotated[Optional[str], "Ratio: 1:1, 16:9, 9:16, 4:3, 3:4, 21:9"] = "16:9",
    resolution: Annotated[Optional[str], "Resolution: 1K, 2K"] = "2K",
    output_dir: Annotated[Optional[str], "Output directory"] = None,
) -> Annotated[str, "Job ID"]:
    """Start diagram generation."""
    from prompts import DiagramType, AspectRatio, ImageSize, optimize_prompt_for_nano_banana
    
    try:
        api_key = context.get_secret("GOOGLE_API_KEY")
        job_id = str(uuid.uuid4())
        
        try:
            dtype = DiagramType(diagram_type.lower())
        except ValueError:
            dtype = DiagramType.GENERIC
        
        optimized_prompt = optimize_prompt_for_nano_banana(
            description, dtype, AspectRatio(aspect_ratio), ImageSize(resolution), emphasis_on_text=True
        )
        
        _cleanup_old_jobs()
        _diagram_jobs[job_id] = {"status": JobStatus.QUEUED, "created": datetime.now()}
        
        threading.Thread(
            target=_generate_diagram_background,
            args=(job_id, api_key, optimized_prompt, aspect_ratio, resolution, f"diagram_{diagram_type}", Path(output_dir) if output_dir else None),
            daemon=True
        ).start()
        
        return f"Job ID: {job_id}\nWait 30 seconds, then check_job_status"
    except Exception as e:
        return f"Error: {str(e)}"


@app.tool
def check_job_status(
    context: Context,
    job_id: Annotated[str, "Job ID"],
) -> Annotated[str, "Job status"]:
    """Check generation progress."""
    _cleanup_old_jobs()
    
    if job_id not in _diagram_jobs:
        return "Job not found"
    
    job = _diagram_jobs[job_id]
    status = job["status"]
    elapsed = (datetime.now() - job["created"]).total_seconds()
    
    if status == JobStatus.COMPLETE:
        return f"Complete ({elapsed:.0f}s) - Ready to download"
    elif status == JobStatus.FAILED:
        return f"Failed: {job.get('result', {}).get('error', 'Unknown')}"
    elif status == JobStatus.GENERATING:
        return f"Generating ({elapsed:.0f}s elapsed, typically 30-60s)"
    else:
        return f"Queued ({elapsed:.0f}s elapsed)"


@app.tool
def download_diagram(
    context: Context,
    job_id: Annotated[str, "Job ID"],
) -> Annotated[str, "Base64 PNG"]:
    """Download diagram. Format: IMAGE|filename|width|height|base64"""
    _cleanup_old_jobs()
    
    if job_id not in _diagram_jobs:
        return "Job not found"
    
    job = _diagram_jobs[job_id]
    
    if job["status"] != JobStatus.COMPLETE:
        return f"Job not ready (status: {job['status']})"
    
    result = job.get("result", {})
    if not result.get("success"):
        return f"Failed: {result.get('error')}"
    
    response = f"IMAGE|{result['filename']}|{result['width']}|{result['height']}|{result['base64']}"
    del _diagram_jobs[job_id]
    
    return response


def main():
    transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    app.run(transport=transport, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
