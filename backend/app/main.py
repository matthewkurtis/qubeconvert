import os
import sys
from datetime import datetime
from typing import List

from app import convert_pdf
from fastapi import FastAPI, File, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://0.0.0.0:8000", "http://localhost:80", "http://0.0.0.0:80", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]
)


@app.post("/uploadfiles/")
async def upload_files(uploaded_files: List[UploadFile] = File(...)):
    # Process the uploaded files here
    upload_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    message = f"Successfully uploaded {len(uploaded_files)} files. Date is: {upload_timestamp}"
    # return message
    files = []
    for file in uploaded_files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Invalid file type")
        else:
            read_file = file.file
            files.append(read_file)
    csv = convert_pdf.csv_to_pdf_web(files)
    download_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return StreamingResponse(
        iter(csv),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=qube-transactions_{download_timestamp}.csv"}
)

