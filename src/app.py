from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import smtplib
from pydantic import BaseModel , EmailStr
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms.huggingface_hub import HuggingFaceHub
from langchain.memory import ConversationBufferMemory
from typing import Literal
from pydantic_core import ValidationError
from src.groq_embeddings import generate_embeddings



# loading the huggingface api key
load_dotenv()

os.environ['HUGGINGFACEHUB_API_TOKEN'] = os.getenv('HUGGINGFACEHUB_API_TOKEN')
gmail_password = os.getenv('GMAIL_PASSWORD')
    

# function to generate email subject and body
def generate_subject_and_body(job_title:str, prompt_type:Literal['subject', 'body'], skills) -> str:
    chat_memory = ConversationBufferMemory(input_key="job_title" , memory_key="chat_memory")
    
    # skills = generate_embeddings(resume_pdf, "summarise the skill section")
    
    example_subject = "Exciting Opportunity for a Frontend Engineer with React and JavaScript Expertise"
    example_body = """Dear Hiring Manager,

    I am writing to express my interest in the Frontend Engineer position at your company. With expertise in skills and measures required in this domain, I am confident that my skills will be a valuable asset to your team. I am particularly drawn to your company's commitment to innovation, and I would love the opportunity to contribute to your dynamic team.

    Thank You
    """
    
    
    if prompt_type == "subject":
        detailed_prompt = f"""You are an expert email subject generator. Your task is to generate an attractive, concise, and engaging email subject for a {job_title} job position. The subject should be relevant to the job title, including key skills such as, and it should be compelling enough for an employer to open the email.

                        Example Subject: {example_subject}

                        Generate a similar subject for the job title "{job_title}"."""
    else:  # for 'body'
        detailed_prompt = f"""You are an expert email body generator. Write a detailed and persuasive email body for a {job_title} job application. The body should highlight key {skills} such as , express enthusiasm about the role, and be unique and professional.

                        Example Body:
                        {example_body}

                        Generate a similar body for the job title "{job_title}"."""
  
    
    prompt = PromptTemplate(
        input_variables={"job_title": job_title},
        template= detailed_prompt,
    )
    
    llm = HuggingFaceHub(repo_id = "google/flan-t5-large", model_kwargs = {"temperature": 0.7 , "max_length": 500})
    
    chain = LLMChain(llm=llm, memory=chat_memory, prompt=prompt, verbose=True)
    
    result = chain.run({"job_title": job_title})
    
    return result   


    
class Email_Validation(BaseModel):
    your_email: EmailStr
    to_email: EmailStr
    password: str
    company_name: str



def send_email(your_email , to_email, password, body, subject, resume_pdf=None):
    
    try:
        msg = MIMEMultipart()
        msg["From"] = your_email
        msg["To"] = to_email
        msg["Subject"] = subject
        
        if any(tag in body.lower() for tag in ["<html>", "<body>", "<div>", "<p>", "<h1>", "<h2>", "<h3>", "<ul>", "<ol>", "<li>"]):
            msg.attach(MIMEText(body, 'html'))
        else:    
            msg.attach(MIMEText(body, 'plain'))
        
        if resume_pdf:
            try:
                with open(resume_pdf, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                # Encode the file in base64
                encoders.encode_base64(part)

                # Add the header with the PDF file name
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={resume_pdf.split('/')[-1]}"
                )

                # Attach the file to the email
                msg.attach(part)
            except Exception as e:
                print(f"Error attaching the PDF file: {e}")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(your_email , password)
            server.sendmail(your_email, to_email, msg.as_string())
            
        print("Email sent successfully")    
    except Exception as e:
        print(f"Error: {e}")
                    

def send_email_from_csv(sender_email, sender_password,csv_file, resume_pdf):
    try:
        data = pd.read_csv(csv_file)
        skills = generate_embeddings(
            resume_pdf, 
            "take out the most important details and impressive details from the file and make it detailed and professional"
            )
    except FileNotFoundError:
        print(f"Error: The file '{csv_file}' was not found.")
        return
    
    for _, row in data.iterrows():
        
        
        if row['Email'] == "N/A" or pd.isna(row['Email']):
            # print(f"Error: Email address not found for {row['Company Name']}.")
            continue
        
        
        if pd.isna(row['Company Name']):
        #    print(f"Skipping row due to missing job title : {row.to_dict()}")
           continue
        try:
            Email = Email_Validation(
                your_email = sender_email,
                to_email = row['Email'],
                password = sender_password,
                company_name= row['Company Name'] if row['Email'] != "N/A" else "Unknown"
            )
            
            
            
            job_title = row['Job Title'].strip()
        
            
            if not pd.isna(row['Email']) or row['Email'] != "N/A" or not pd.isna(row['Company Name']):
                
                
                subject =  generate_subject_and_body(job_title, "subject", skills)
                # print("subject ->", type(subject))
                
                body = generate_subject_and_body(job_title, "body", skills)
                # print("body ->", body)
                
                send_email(Email.your_email, Email.to_email, Email.password, body, subject, resume_pdf)
            
        except ValidationError as e:
            print(f"Validation Error: {e}")    
        except Exception as e:
            print(e)    

def send_email_in_HTML(sender_email, sender_password,data_source,htmlbody, temporary_pdf=None):
    if data_source.endswith(".csv"):
        try:
            data = pd.read_csv(data_source)
        except FileNotFoundError:
            print(f"Error: The file '{data_source}' was not found.")
            return
        
        for _, row in data.iterrows():
            
            if row['Email'] == "N/A" or pd.isna(row['Email']):
                continue
            if pd.isna(row['Company Name']):
                continue
            try:
                Email = Email_Validation(
                    your_email = sender_email,
                    to_email = row['Email'],
                    password = sender_password,
                    company_name= row['Company Name'] if row['Email'] != "N/A" else "Unknown"
                )
                
                job_title = row['Job Title'].strip()
                
                subject = f"For {job_title} job position"
            
                if not pd.isna(row['Email']) or row['Email'] != "N/A" or not pd.isna(row['Company Name']):
                    
                    send_email(Email.your_email, Email.to_email, Email.password, htmlbody, subject, temporary_pdf)
            except ValidationError as e:
                print(f"Validation Error: {e}")
    else:
        recipient_email = data_source
        try:
            Email = Email_Validation(
                your_email=sender_email,
                to_email=recipient_email,
                password=sender_password,
                company_name="Unknown"
            )
            
            subject = "Email containing code"
            send_email(Email.your_email, Email.to_email, Email.password, htmlbody, subject, temporary_pdf)
        except ValidationError as e:
            print(f"Validation Error: {e}")                
     

