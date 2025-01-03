from fastapi import FastAPI, File, UploadFile, Form , HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Optional
import shutil
from app import send_email_in_HTML, send_emails_from_csv

app = FastAPI()


@app.post("/send-email-via-csv/")
async def send_emails_from_csv_api(
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    csv_file: UploadFile = File(...),
    resume_pdf: UploadFile = File(...),
):
    csv_path = f"/tmp/{csv_file.filename}"
    pdf_path = f"/tmp/{resume_pdf.filename}"
    
    with open(csv_path, "wb") as csv_file:
        shutil.copyfileobj(csv_file.file, csv_file)
        
    with open(pdf_path, "wb") as pdf_file:
        shutil.copyfileobj(resume_pdf.file, pdf_file)
        
    try:
        send_emails_from_csv(sender_email, sender_password, csv_path, pdf_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
    
    return JSONResponse(content={"message": "Emails sent successfully!"})       

@app.post("/send-html-via-email/")
async def send_html_inemail(
    sender_email: str = Form(...),
    sender_password: str = Form(...),
    data_source: str = Form(...),
    html_body: str = Form(...),
    temporary_pdf: Optional[UploadFile] = File(None),
):
    temp_pdf_path = None
    
    if temporary_pdf:
        temp_pdf_path = f"/tmp/{temporary_pdf.filename}"
        with open(temp_pdf_path, "wb") as temp_pdf_file:
            shutil.copyfileobj(temporary_pdf.file, temp_pdf_file)
            
    if data_source.endswith(".csv"):
        try:
            send_email_in_HTML(sender_email, sender_password, data_source, html_body, temp_pdf_path)  
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}, error in html email")  
        
    else:
        # Assume data_source is a single email address
        try:
            send_email_in_HTML(sender_email, sender_password, data_source, html_body, temp_pdf_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error occurred: {str(e)}")   
        
    return JSONResponse(content={"message": "HTML in email sent successfully!"})      



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)       
             