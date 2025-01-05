from fastapi import FastAPI, File, UploadFile, Form , HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Optional
import shutil
import uvicorn
import os
import tempfile
from src.app import send_email_in_HTML, send_email_from_csv
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Specify allowed HTTP methods, e.g., ["GET", "POST"]
    allow_headers=["*"],  # Specify allowed headers
)

@app.post("/send-email-via-csv/")
async def send_emails_from_csv_api(
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    csv_file: UploadFile = File(...),
    resume_pdf: UploadFile = File(...),
):
    csv_path = None
    pdf_path = None

    if csv_file and resume_pdf:
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate the full file paths using the temporary directory and the uploaded files' names
            csv_path = os.path.join(temp_dir, csv_file.filename)
            pdf_path = os.path.join(temp_dir, resume_pdf.filename)

            try:
                # Save the CSV file to the temporary directory
                with open(csv_path, "wb") as temp_csv_file:
                    shutil.copyfileobj(csv_file.file, temp_csv_file)

                # Save the PDF file to the temporary directory
                with open(pdf_path, "wb") as temp_pdf_file:
                    shutil.copyfileobj(resume_pdf.file, temp_pdf_file)

                # Try sending the email with the temporary paths
                send_email_from_csv(sender_email, sender_password, csv_path, pdf_path)
            except Exception as e:
                # Handle any exceptions and raise HTTP error
                raise HTTPException(status_code=500, detail=str(e))

            # Return success response
            return JSONResponse(content={"message": "Emails sent successfully!"})       

@app.post("/send-html-via-email/")
async def send_html_inemail(
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    data_source: Optional[str] = Form(None),  # Used for single email
    csv: Optional[UploadFile] = File(None),  # Used for CSV file
    html_body: str = Form(...),
    temporary_pdf: Optional[UploadFile] = File(None),  # Optional PDF attachment
):
    temp_pdf_path = None  # Initialize PDF path
    if data_source and csv:
        raise HTTPException(
            status_code=400,
            detail="Both 'data_source' and 'csv' cannot be provided at the same time. Provide only one.",
        )
        
    # else:    
    # Handle PDF attachment
    if temporary_pdf:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_pdf_path = os.path.join(temp_dir, temporary_pdf.filename)
            with open(temp_pdf_path, "wb") as temp_pdf_file:
                shutil.copyfileobj(temporary_pdf.file, temp_pdf_file)

    # Check if CSV file is provided
            if csv:
                if csv.filename.endswith(".csv"):
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_csv_path = os.path.join(temp_dir, csv.filename)
                        with open(temp_csv_path, "wb") as temp_csv_file:
                            shutil.copyfileobj(csv.file, temp_csv_file)
                        
                        try:
                            print("Processing CSV file...")
                            # Call your email-sending function with the parsed CSV
                            send_email_in_HTML(sender_email, sender_password, temp_csv_path, html_body, temp_pdf_path)
                            print("Processed CSV file.")
                        except Exception as e:
                            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}, error in html email with CSV and PDF")
                else:
                    raise HTTPException(status_code=400, detail="Uploaded file is not a valid CSV.")
            else:
                # Handle single email address in `data_source`
                if data_source:
                    try:
                        print("Processing single email...")
                        send_email_in_HTML(sender_email, sender_password, data_source, html_body, temp_pdf_path)
                        print("Processed single email.")
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}, error in html email with single email")
                else:
                    raise HTTPException(status_code=400, detail="No valid email or CSV file provided.")

    else:
        if csv:
                if csv.filename.endswith(".csv"):                        
                        try:
                            print("Processing CSV file...")
                            # Call your email-sending function with the parsed CSV
                            send_email_in_HTML(sender_email, sender_password, temp_csv_path, html_body, temp_pdf_path)
                            print("Processed CSV file.")
                        except Exception as e:
                            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}, error in html email with CSV and no PDF")
                else:
                    raise HTTPException(status_code=400, detail="Uploaded file is not a valid CSV.")
        else:
            # Handle single email address in `data_source`
            if data_source:
                try:
                    print("Processing single email...")
                    send_email_in_HTML(sender_email, sender_password, data_source, html_body, temp_pdf_path)
                    print("Processed single email.")
                except Exception as e:
                    raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}, error in html email with single email, no CSV , no PDF")
            else:
                raise HTTPException(status_code=400, detail="No valid email or CSV file provided.")
    
    return JSONResponse(content={"message": "HTML email sent successfully!"})


if __name__ == "__main__":
    
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)       
             