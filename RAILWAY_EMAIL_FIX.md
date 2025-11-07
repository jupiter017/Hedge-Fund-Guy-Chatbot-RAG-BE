# 🚨 Railway SMTP Issue - Solutions

## Problem

Railway (and many cloud platforms) **block outgoing SMTP connections** on ports 25, 465, and 587 for security reasons.

**Error**:
```
OSError: [Errno 101] Network is unreachable
```

This happens when trying to connect to `smtp.gmail.com:587`.

---

## ✅ Solutions (Choose One)

### Solution 1: Use SendGrid (Recommended - FREE tier available)

SendGrid has a generous free tier (100 emails/day) and works perfectly on Railway.

#### 1. Sign up for SendGrid
- Go to: https://sendgrid.com/
- Create free account (100 emails/day free)
- Get API key from Settings → API Keys

#### 2. Install SendGrid SDK
```bash
pip install sendgrid
```

Add to `requirements.txt`:
```
sendgrid==6.11.0
```

#### 3. Create new email sender

Create `backend/email_sender_sendgrid.py`:

```python
"""
Email Delivery using SendGrid API (Works on Railway)
"""

import os
from typing import Dict
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class EmailSenderSendGrid:
    """Handles sending structured data via email using SendGrid API"""
    
    def __init__(self, data_storage=None):
        self.api_key = os.getenv("SENDGRID_API_KEY")
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.data_storage = data_storage
        
        if not self.api_key:
            print("⚠️  Warning: SENDGRID_API_KEY not configured in .env file")
        if not self.sender_email:
            print("⚠️  Warning: SENDER_EMAIL not configured in .env file")
    
    def get_recipient_email(self) -> str:
        """Get recipient email from database settings or fallback to .env"""
        if self.data_storage:
            db_email = self.data_storage.get_setting("recipient_email")
            if db_email:
                return db_email
        
        return os.getenv("RECIPIENT_EMAIL", "")
    
    def send_user_data(self, session_data: Dict) -> bool:
        """
        Send collected user data via email using SendGrid
        
        Args:
            session_data: Dictionary containing session information
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Get recipient email
            recipient_email = self.get_recipient_email()
            
            if not recipient_email:
                print("❌ No recipient email configured")
                return False
            
            if not self.api_key or not self.sender_email:
                print("❌ SendGrid API key or sender email not configured")
                return False
            
            # Create HTML content
            html_content = self._create_html_email(session_data)
            
            # Create message
            message = Mail(
                from_email=Email(self.sender_email),
                to_emails=To(recipient_email),
                subject=f"New User Data Collected - Session {session_data['session_id'][:8]}",
                html_content=Content("text/html", html_content)
            )
            
            # Send email via SendGrid API
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Email sent successfully to {recipient_email}")
                return True
            else:
                print(f"⚠️  Email sent with status code: {response.status_code}")
                return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {type(e).__name__} - {str(e)}")
            return False
    
    def _create_html_email(self, session_data: Dict) -> str:
        """Create formatted HTML email content"""
        data = session_data['data']
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 5px 5px 0 0;
                    text-align: center;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 20px;
                    border: 1px solid #ddd;
                }}
                .data-item {{
                    background: white;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #667eea;
                    border-radius: 3px;
                }}
                .label {{
                    font-weight: bold;
                    color: #667eea;
                    text-transform: uppercase;
                    font-size: 12px;
                    margin-bottom: 5px;
                }}
                .value {{
                    font-size: 16px;
                    color: #333;
                }}
                .meta {{
                    background: #e9ecef;
                    padding: 15px;
                    margin-top: 20px;
                    border-radius: 3px;
                    font-size: 12px;
                    color: #6c757d;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #999;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏦 Insomniac Hedge Fund Guy</h1>
                <p>New User Data Collection</p>
            </div>
            
            <div class="content">
                <h2>Collected User Information</h2>
                
                <div class="data-item">
                    <div class="label">Name</div>
                    <div class="value">{data.get('name', 'Not provided')}</div>
                </div>
                
                <div class="data-item">
                    <div class="label">Email Address</div>
                    <div class="value">{data.get('email', 'Not provided')}</div>
                </div>
                
                <div class="data-item">
                    <div class="label">Income Level</div>
                    <div class="value">{data.get('income', 'Not provided')}</div>
                </div>
                
                <div class="meta">
                    <strong>Session Details:</strong><br>
                    Session ID: {session_data['session_id']}<br>
                    Started: {session_data['timestamp']}<br>
                    Completed: {session_data.get('completed_at', 'N/A')}<br>
                    Status: {session_data['status']}
                </div>
            </div>
            
            <div class="footer">
                <p>This is an automated message from the Insomniac Hedge Fund Guy AI Chatbot System</p>
                <p>Data collected on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
        </body>
        </html>
        """
        
        return html
```

#### 4. Update api.py to use SendGrid

```python
# In api.py, change import:
from email_sender_sendgrid import EmailSenderSendGrid

# In startup_event():
email_sender = EmailSenderSendGrid(data_storage=data_storage)
```

#### 5. Set environment variables in Railway

```
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
SENDER_EMAIL=your-verified-sender@example.com
RECIPIENT_EMAIL=recipient@example.com
```

---

### Solution 2: Use Mailgun

Similar to SendGrid, Mailgun provides API-based email sending.

1. Sign up at https://www.mailgun.com/ (Free tier: 100 emails/day)
2. Install: `pip install mailgun`
3. Get API key and domain
4. Use Mailgun API instead of SMTP

---

### Solution 3: Use AWS SES

If you're already using AWS:

1. Set up AWS SES
2. Install: `pip install boto3`
3. Use boto3 to send emails
4. More complex setup but very reliable

---

### Solution 4: Disable Email (Temporary Solution)

If you don't need emails right now, you can disable them:

In `api.py`, comment out or modify:

```python
# In startup_event():
email_sender = None  # Disable email temporarily
print("⚠️  Email sending disabled")

# Or wrap email sending in a check:
if email_sender and os.getenv("ENABLE_EMAIL", "false").lower() == "true":
    asyncio.create_task(send_email_async(email_sender, session_data))
```

**Note**: User data is still saved in the PostgreSQL database. You can retrieve it from the Admin Dashboard.

---

## 📊 Comparison

| Solution | Free Tier | Setup Difficulty | Railway Compatible |
|----------|-----------|------------------|-------------------|
| SendGrid | 100/day | Easy | ✅ Yes |
| Mailgun | 100/day | Easy | ✅ Yes |
| AWS SES | 62,000/month | Medium | ✅ Yes |
| SMTP (Gmail) | Unlimited | Easy | ❌ No (blocked) |
| Disable | N/A | Very Easy | ✅ Yes |

---

## 🚀 Quick Fix: Use SendGrid (Recommended)

```bash
# 1. Install SendGrid
pip install sendgrid

# 2. Create the new file
# (Copy the code above to backend/email_sender_sendgrid.py)

# 3. Update requirements.txt
echo "sendgrid==6.11.0" >> backend/requirements.txt

# 4. Update api.py import
# Change: from email_sender import EmailSender
# To: from email_sender_sendgrid import EmailSenderSendGrid

# 5. Set Railway environment variables
# SENDGRID_API_KEY=your-key
# SENDER_EMAIL=your-email@example.com

# 6. Deploy to Railway
git add .
git commit -m "Switch to SendGrid for email delivery"
git push
```

---

## 🔍 Why SMTP Doesn't Work on Railway

Railway blocks outgoing connections on common SMTP ports (25, 465, 587) to:
- Prevent spam
- Reduce abuse
- Improve security

This is standard practice for most cloud platforms (Heroku, Vercel, Fly.io, etc.).

**Solution**: Use HTTP-based email APIs (SendGrid, Mailgun, SES) which work perfectly! ✅

---

## Need Help?

If you want me to implement SendGrid for you, just ask! It's a 5-minute change.

