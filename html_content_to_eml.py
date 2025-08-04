import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

class HTMLToEMLConverter:
    def __init__(self):
        pass
    
    def html_to_eml(self, html_content, subject="No Subject", 
                    sender="noreply@example.com", recipient="recipient@example.com",
                    cc=None, bcc=None, plain_text=None, attachments=None):
        """
        Convert HTML content to EML format
        
        Args:
            html_content (str): The HTML content to convert
            subject (str): Email subject line
            sender (str): Sender email address
            recipient (str): Recipient email address (can be list)
            cc (list): CC recipients (optional)
            bcc (list): BCC recipients (optional)
            plain_text (str): Plain text version (optional)
            attachments (list): List of file paths to attach (optional)
        
        Returns:
            str: EML formatted string
        """
        # Create message container
        msg = MIMEMultipart('alternative')
        
        # Set headers
        msg['Subject'] = subject
        msg['From'] = sender
        
        # Handle recipients
        if isinstance(recipient, list):
            msg['To'] = ', '.join(recipient)
        else:
            msg['To'] = recipient
            
        if cc:
            msg['Cc'] = ', '.join(cc) if isinstance(cc, list) else cc
            
        if bcc:
            msg['Bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc
            
        # Add date
        msg['Date'] = email.utils.formatdate(localtime=True)
        
        # Create plain text version if not provided
        if plain_text is None:
            # Basic HTML to text conversion (you might want to use html2text library for better conversion)
            import re
            plain_text = re.sub('<[^<]+?>', '', html_content)
            plain_text = plain_text.strip()
        
        # Create text parts
        if plain_text:
            text_part = MIMEText(plain_text, 'plain', 'utf-8')
            msg.attach(text_part)
            
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for file_path in attachments:
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(file_path)}'
                    )
                    msg.attach(part)
        
        return msg.as_string()
    
    def save_eml(self, eml_content, filename):
        """Save EML content to a file"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(eml_content)
        print(f"EML file saved as: {filename}")

# Example usage
def example_usage():
    converter = HTMLToEMLConverter()
    
    # Sample HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
            .header { background-color: #f0f0f0; padding: 20px; }
            .content { padding: 20px; }
            .footer { background-color: #333; color: white; padding: 10px; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Welcome to Our Newsletter</h1>
        </div>
        <div class="content">
            <h2>Important Updates</h2>
            <p>Dear Valued Customer,</p>
            <p>We're excited to share some important updates with you:</p>
            <ul>
                <li>New product features launched</li>
                <li>Improved customer support</li>
                <li>Special discount offers</li>
            </ul>
            <p>Thank you for being a loyal customer!</p>
        </div>
        <div class="footer">
            <p>&copy; 2025 Your Company Name. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    # Convert to EML
    eml_content = converter.html_to_eml(
        html_content=html_content,
        subject="Monthly Newsletter - Important Updates",
        sender="newsletter@company.com",
        recipient="customer@example.com",
        plain_text="Dear Valued Customer,\n\nWe're excited to share some important updates with you:\n- New product features launched\n- Improved customer support\n- Special discount offers\n\nThank you for being a loyal customer!"
    )
    
    # Save to file
    converter.save_eml(eml_content, "newsletter.eml")
    
    # Print the EML content
    print("Generated EML content:")
    print("-" * 50)
    print(eml_content)

# Advanced example with multiple recipients and attachments
def advanced_example():
    converter = HTMLToEMLConverter()
    
    html_content = """
    <html>
    <body>
        <h2>Project Status Report</h2>
        <p>Hi Team,</p>
        <p>Please find the attached project status report.</p>
        <table border="1" style="border-collapse: collapse;">
            <tr>
                <th>Task</th>
                <th>Status</th>
                <th>Due Date</th>
            </tr>
            <tr>
                <td>Design Phase</td>
                <td>Complete</td>
                <td>2025-07-15</td>
            </tr>
            <tr>
                <td>Development</td>
                <td>In Progress</td>
                <td>2025-08-30</td>
            </tr>
        </table>
        <p>Best regards,<br>Project Manager</p>
    </body>
    </html>
    """
    
    eml_content = converter.html_to_eml(
        html_content=html_content,
        subject="Project Status Report - Week 31",
        sender="pm@company.com",
        recipient=["team@company.com", "stakeholder@company.com"],
        cc=["manager@company.com"],
        # attachments=["report.pdf", "charts.xlsx"]  # Uncomment if you have files
    )
    
    converter.save_eml(eml_content, "project_report.eml")

# Utility function for batch conversion
def convert_html_files_to_eml(html_directory, output_directory):
    """Convert all HTML files in a directory to EML format"""
    converter = HTMLToEMLConverter()
    
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(html_directory):
        if filename.endswith('.html') or filename.endswith('.htm'):
            html_path = os.path.join(html_directory, filename)
            
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Generate EML filename
            base_name = os.path.splitext(filename)[0]
            eml_filename = f"{base_name}.eml"
            eml_path = os.path.join(output_directory, eml_filename)
            
            # Convert and save
            eml_content = converter.html_to_eml(
                html_content=html_content,
                subject=f"Email from {base_name}",
                sender="system@example.com",
                recipient="recipient@example.com"
            )
            
            with open(eml_path, 'w', encoding='utf-8') as f:
                f.write(eml_content)
            
            print(f"Converted: {filename} -> {eml_filename}")

if __name__ == "__main__":
    # Run the basic example
    example_usage()
    
    # Uncomment to run advanced example
    # advanced_example()
    
    # Uncomment to convert a directory of HTML files
    # convert_html_files_to_eml("html_files", "eml_output")
