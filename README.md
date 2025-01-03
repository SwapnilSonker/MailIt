# EmailScrawl API

## Overview

EmailScrawl provides two main APIs to handle email sending functionalities. Below is a brief description of each API and their capabilities.

## API Endpoints

### 1. Authentication API

**Endpoint:** `/send-email-via-csv/`

**Description:** This API allows users to authenticate using the following parameters:
- `password`
- `email`
- `csv`
- `file`

### 2. Email Sending API

**Endpoint:** `/send-html-via-email/`

**Description:** This API allows users to send emails with the following features:
- Supports both HTML body and normal email body
- Emails can be sent to either a predefined environment list or a specific email address

## Usage

### Authentication API

To authenticate, send a POST request to `/api/authenticate` with the required parameters.

### Email Sending API

To send an email, send a POST request to `/api/send-email` with the email content and recipient details.

## Example

### Authentication Request

```http
POST /send-email-via-csv/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "yourpassword",
    "csv": "path/to/csvfile.csv",
    "file": "path/to/file"
}
```

### Email Sending Request

```http
POST /send-html-via-email/
Content-Type: application/json

{
    "to": "recipient@example.com",
    "subject": "Your Subject",
    "body": "This is the email body",
    "htmlBody": "<h1>This is the HTML email body</h1>"
}
```

## Conclusion

EmailScrawl's APIs provide a robust solution for email authentication and sending, supporting various formats and recipient configurations.