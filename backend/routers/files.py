"""
File endpoints (all registered under the /api prefix by backend/main.py):

  GET  /api/download-walkthrough   — walkthrough.md as downloadable attachment
  GET  /api/download-project-zip   — entire output directory as ZIP
  POST /api/save-files             — write {filename, content} list to a local folder
"""
from __future__ import annotations

import io
import os
import zipfile
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

router = APIRouter()


# ── Download walkthrough.md ───────────────────────────────────────────────────

@router.get("/download-walkthrough")
async def download_walkthrough(path: str) -> FileResponse:
    """Query param: path = absolute path to the walkthrough.md file on disk."""
    path = os.path.normpath(path)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"File not found: {path}")
    return FileResponse(
        path=path,
        media_type="text/markdown",
        filename="walkthrough.md",
        headers={"Content-Disposition": 'attachment; filename="walkthrough.md"'},
    )


# ── Download project as ZIP ───────────────────────────────────────────────────

@router.get("/download-project-zip")
async def download_project_zip(output_dir: str) -> StreamingResponse:
    """Query param: output_dir = absolute path to the project output directory."""
    output_dir = os.path.normpath(output_dir)
    if not os.path.isdir(output_dir):
        raise HTTPException(
            status_code=404,
            detail=f"Output directory not found: {output_dir}",
        )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_dir):
            # Skip common noise directories
            dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "node_modules", ".venv", "venv")]
            for filename in files:
                full_path = os.path.join(root, filename)
                arcname   = os.path.relpath(full_path, output_dir)
                zf.write(full_path, arcname)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="project.zip"'},
    )


# ── Save files to user-specified folder ──────────────────────────────────────

class FileItem(BaseModel):
    filename: str
    content: str


class SaveFilesRequest(BaseModel):
    output_dir: str
    files: List[FileItem]


@router.post("/save-files")
async def save_files(request: SaveFilesRequest) -> dict:
    output_dir = os.path.normpath(request.output_dir.strip())

    if not output_dir:
        raise HTTPException(status_code=400, detail="output_dir cannot be empty")

    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot create directory '{output_dir}': {exc}",
        )

    saved_paths: list[str] = []
    for file_item in request.files:
        # os.path.basename strips any path-traversal attempts from caller
        fname = os.path.basename(file_item.filename)
        if not fname:
            continue
        fpath = os.path.join(output_dir, fname)
        try:
            with open(fpath, "w", encoding="utf-8") as fh:
                fh.write(file_item.content)
            saved_paths.append(fpath)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to write {fname}: {exc}",
            )

    return {
        "saved":      saved_paths,
        "output_dir": output_dir,
        "count":      len(saved_paths),
    }
