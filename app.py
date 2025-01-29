import re
import smtplib
import spacy
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pdfminer.high_level import extract_text
from docx import Document

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'}

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Helper functions
def extract_text_from_pdf(file_path):
    try:
        return extract_text(file_path)
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error reading DOCX: {e}"

def extract_details(text):
    details = {}
    lines = text.splitlines()
    details["Name"] = lines[0].strip() if lines else "Unknown"

    
    # Age extraction: Regex for common age formats like "Age: 30" or "Age: 30 years"
    age_match = re.search(r"Age[:\-]?\s*(\d+)\s*(?:years?|yrs?)?", text)
    details["Age"] = age_match.group(1) if age_match else "Not Found"

    # Phone number extraction: Regex for 10-digit or international phone numbers
    phone_match = re.search(r"\b\d{10}\b|\+\d{1,3}\s?\d{10}\b", text)
    details["Phone Number"] = phone_match.group() if phone_match else "Not Found"

    # Email extraction: Regex for standard email formats
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    details["Email Address"] = email_match.group() if email_match else "Not Found"

    # LinkedIn Profile extraction: Regex for LinkedIn URLs
    linkedin_match = re.search(r"(https?:\/\/)?([\w]+\.)?linkedin\.com\/[A-z0-9_-]+\/", text)
    details["LinkedIn Profile"] = linkedin_match.group() if linkedin_match else "Not Found"

    # GitHub Profile extraction: Regex for GitHub URLs
    github_match = re.search(r"(https?:\/\/)?(www\.)?github\.com\/[A-z0-9_-]+", text)
    details["GitHub"] = github_match.group() if github_match else "Not Found"

    # Portfolio/Website extraction: Regex for URLs
    website_match = re.search(r"https?:\/\/[^\s]+", text)
    details["Portfolio/Website"] = website_match.group() if website_match else "Not Found"

    # Named Entity Recognition for Location (GPE)
    doc = nlp(text)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    details["Location"] = ", ".join(locations) if locations else "Not Found"

    # Additional fields like Certifications and Achievements
    details["Certifications"] = "N/A"
    details["Achievements"] = "N/A"
    
    # Custom rule or NER for Certifications and Achievements can be added here
    cert_match = re.search(r"(Certified|Certification|Certifications)\s*[:\-]?\s*([A-Za-z0-9\s]+)", text)
    if cert_match:
        details["Certifications"] = cert_match.group(2)
    
    # Extract Achievements (based on custom or NER extraction)
    achievements_match = re.findall(r"(Achievements?:[\s\S]+?)(?=\n|$)", text)
    if achievements_match:
        details["Achievements"] = " | ".join(achievements_match)

    details = {key: (value if value else "N/A") for key, value in details.items()}
    return details

def extract_sections(text, keywords):
    sections = {}
    current_section = None
    text_lines = text.splitlines()

    for line in text_lines:
        line = line.strip()
        if not line:
            continue

        # Check if any keyword is in the current line to identify section headers
        if any(keyword.lower() in line.lower() for keyword in keywords):
            current_section = next((keyword for keyword in keywords if keyword.lower() in line.lower()), None)
            sections[current_section] = []
        elif current_section:
            # Handle bullet points (•, ◦, etc.)
            if line.startswith("•") or line.startswith("◦"):
                line = line[1:].strip()  # Removing the bullet symbol
            sections[current_section].append(line)

    # Ensure sections with no content are marked as "N/A"
    sections = {key: (value if value else ["N/A"]) for key, value in sections.items()}

    # Refine the Skills section using NER or regex (custom extraction)
    if 'Skills' in sections:
        skills = sections['Skills']
        refined_skills = []

        for line in skills:
            # Split by common delimiters like commas or semi-colons
            skill_list = re.split(r'[;,]\s*', line)
            refined_skills.extend([skill.strip() for skill in skill_list if skill.strip()])

        # Ensure the skills are distinct and add to the section
        sections['Skills'] = list(set(refined_skills)) if refined_skills else ["Not Found"]

    # Projects extraction using regex or custom rules (can be expanded based on format)
    if 'Projects' in sections:
        projects = sections['Projects']
        refined_projects = [line for line in projects if 'project' in line.lower()]
        sections['Projects'] = refined_projects if refined_projects else ["Not Found"]

    return sections

def extract_resume_details(text, keywords):
    details = extract_details(text)
    sections = extract_sections(text, keywords)
    return {**details, **sections}

# Routes and other Flask setup remains the same...


def send_email(recipient, subject, body, attachments):
    try:
        sender_email = "your_email@gmail.com"
        sender_password = "your_password"

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        for file_path in attachments:
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            message.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        return {"message": "Email sent successfully"}
    except Exception as e:
        return {"error": str(e)}

# Routes
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if 'resume' not in request.files:
            return jsonify({"error": "No file part"}), 400

        files = request.files.getlist("resume")
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                saved_files.append(file_path)

        resumes = []
        for file_path in saved_files:
            if file_path.lower().endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            elif file_path.lower().endswith(".docx"):
                text = extract_text_from_docx(file_path)
            else:
                continue

            keywords = [
                "Experience", "Education", "Skills", "Projects", "Certifications",
                "Achievements", "Languages", "References"
            ]
            details = extract_details(text)
            sections = extract_sections(text, keywords)
            
            file_url = url_for('uploaded_file', filename=os.path.basename(file_path))
            resumes.append({"details": details, "sections": sections, "file_path": file_path, "file_url": file_url})

        return render_template("results.html", resumes=resumes)

    return render_template("upload.html")

@app.route("/results", methods=["GET"])
def display_results():
    return render_template("results.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/delete", methods=["POST"])
def delete_file():
    file_paths = request.json.get("file_path", [])
    if not isinstance(file_paths, list):
        file_paths = [file_paths]

    errors = []
    for file_path in file_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                errors.append(f"Failed to delete {file_path}: {str(e)}")
        else:
            errors.append(f"File not found: {file_path}")

    if errors:
        return {"error": errors}, 400

    return {"message": "Selected files deleted successfully"}, 200

@app.route("/email", methods=["POST"])
def email_files():
    data = request.json
    recipient = data.get("recipient")
    subject = data.get("subject", "Resume Details")
    body = data.get("body", "Please find the attached files.")
    attachments = data.get("attachments", [])

    response = send_email(recipient, subject, body, attachments)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
