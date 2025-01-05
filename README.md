# FastAPI Email API

This project provides two endpoints for sending emails using FastAPI. You can send bulk emails with attachments via a CSV file or send custom HTML emails with optional attachments. The endpoints are designed to handle both single and bulk email scenarios.

---

## Features
- **Send Bulk Emails**: Upload a CSV file to send emails to multiple recipients.
- **Send HTML Emails**: Send customized HTML emails with optional attachments.
- **Secure**: Uses form data for email credentials and file uploads.
- **Extensible**: Can be expanded to include additional email use cases.
- **CORS Support**: Configured to handle cross-origin requests.

---

## Endpoints

### 1. **Send Emails via CSV**

**Endpoint**: `/send-email-via-csv/`  
**Method**: `POST`  
**Description**: Upload a CSV file containing recipient email addresses to send bulk emails. Attach a resume PDF to include as an attachment.

#### Parameters
- `sender_email` (Form): The sender's email address.
- `sender_password` (Form): The sender's email password.
- `csv_file` (File): The CSV file containing recipient email addresses.
- `resume_pdf` (File): A PDF file to attach to the email.

#### Example Request
```bash
curl -X POST "http://your-api-domain/send-email-via-csv/" \
-H "accept: application/json" \
-F "sender_email=your_email@example.com" \
-F "sender_password=your_password" \
-F "csv_file=@recipients.csv" \
-F "resume_pdf=@resume.pdf"


## Endpoint: **Send HTML Email**

**Endpoint**: `/send-html-via-email/`  
**Method**: `POST`  
**Description**: Sends a custom HTML email to one or more recipients. The API can accept a single email address or a CSV file containing a list of recipients. Optionally, a PDF attachment can be included.

### Input Parameters (FormData)

| Parameter          | Type           | Description                                                        |
|--------------------|----------------|--------------------------------------------------------------------|
| `sender_email`     | `string` (Form) | The sender's email address.                                        |
| `sender_password`  | `string` (Form) | The sender's email password.                                       |
| `data_source`      | `string` (Form, Optional) | A single recipient's email address. If provided, this is the recipient. |
| `csv`              | `file` (File, Optional) | A CSV file containing a list of recipient emails.                  |
| `html_body`        | `string` (Form) | The HTML content to be included in the email body.                 |
| `temporary_pdf`    | `file` (File, Optional) | A PDF file to attach to the email (optional).                      |

### Example Request

#### 1. **Using curl to Send HTML Email:**

To send an HTML email with an optional PDF attachment:
```bash
curl -X POST "http://your-api-domain/send-html-via-email/" \
-H "accept: application/json" \
-F "sender_email=your_email@example.com" \
-F "sender_password=your_password" \
-F "html_body=<h1>Hello, this is an HTML email!</h1>" \
-F "temporary_pdf=@attachment.pdf"