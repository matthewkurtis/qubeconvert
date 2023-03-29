import os
import sys

print(sys.path)
from datetime import datetime
from typing import List

from fastapi import FastAPI, File, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from app import convert_pdf

# from convert_pdf import csv_to_pdf_web

# # # Add the directory containing my_module.py to the Python path
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))


app = FastAPI()

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

