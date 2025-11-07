"""
Layer 4: Email Delivery System
Sends structured user data to an external destination via SMTP (no third-party services)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()


class EmailSender:
    """Handles sending structured data via email using SMTP"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.sender_password = os.getenv("SENDER_PASSWORD")
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            print("⚠️  Warning: Email credentials not fully configured in .env file")
    
    def send_user_data(self, session_data: Dict) -> bool:
        """
        Send collected user data via email
        
        Args:
            session_data: Dictionary containing session information
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"New User Data Collected - Session {session_data['session_id'][:8]}"
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Create HTML content
            html_content = self._create_html_email(session_data)
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
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
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
            print("✅ SMTP connection successful")
            return True
        except Exception as e:
            print(f"❌ SMTP connection failed: {str(e)}")
            return False


if __name__ == "__main__":
    # Test the email sender
    email_sender = EmailSender()
    
    # Test connection
    email_sender.test_connection()
    
    # Test sending (with sample data)
    sample_session = {
        "session_id": "test-session-123",
        "timestamp": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "status": "complete",
        "data": {
            "name": "Test User",
            "email": "testuser@example.com",
            "income": "$75k-$100k"
        }
    }
    
    # Uncomment to actually send test email
    # email_sender.send_user_data(sample_session)

