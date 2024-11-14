import re
from pypdf import PdfReader
import os
import tempfile
from flask import Request, Response, jsonify

def extract_health_data(request: Request) -> Response:
    # Define a dictionary of health data terms and their corresponding regex patterns
    health_data_patterns = {
        "FEV1": r'FEV1\s*\(Forced\s*Expiratory\s*Volume\s*in\s*1\s*Second\)\s*:\s*(\d+(\.\d+)?)\s*L',
        "FVC": r'FVC\s*\(Forced\s*Vital\s*Capacity\)\s*:\s*(\d+(\.\d+)?)\s*L',
        "Cholesterol": r'Cholesterol\s*\(Total\)\s*:\s*(\d+(\.\d+)?)\s*mmol/L',
        "HDL": r'HDL\s*\(High-Density\s*Lipoprotein\)\s*:\s*(\d+(\.\d+)?)\s*mmol/L',
        "LDL": r'LDL\s*\(Low-Density\s*Lipoprotein\)\s*:\s*(\d+(\.\d+)?)\s*mmol/L',
        "VLDL": r'VLDL\s*\(Very\s*Low-Density\s*Lipoprotein\)\s*:\s*(\d+(\.\d+)?)\s*mg/dL',
        "Triglycerides": r'Triglycerides\s*\(TG\)\s*:\s*(\d+(\.\d+)?)\s*mmol/L',
        "Creatinine": r'Creatinine\s*\(Cr\)\s*:\s*(\d+(\.\d+)?)\s*mg/dL',
        "Urea": r'Urea\s*:\s*(\d+(\.\d+)?)\s*mg/dL',
        "Hemoglobin": r'Hemoglobin\s*:\s*(\d+(\.\d+)?)\s*mmol/mol',
        "Diastolic Blood Pressure": r'Diastolic\s*Blood\s*Pressure\s*\(DiaBP\)\s*:\s*(\d+(\.\d+)?)\s*mm/Hg',
        "Systolic Blood Pressure": r'Systolic\s*Blood\s*Pressure\s*\(SysBP\)\s*:\s*(\d+(\.\d+)?)\s*mm/Hg'
    }

    # Extract the PDF file from the request
    pdf_file = request.files['file']
    with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
        temp_pdf.write(pdf_file.read())
        temp_pdf_path = temp_pdf.name

    # Read the PDF file
    reader = PdfReader(temp_pdf_path)
    all_text = ""
    for page in reader.pages:
        all_text += page.extract_text()

    # Extract health data
    results = {}
    for term, pattern in health_data_patterns.items():
        match = re.search(pattern, all_text, re.IGNORECASE)
        if match:
            value = match.group(1)
            unit = match.group(3) if len(match.groups()) > 2 else ''
            results[term] = f"{value} {unit}"
        else:
            results[term] = "Not found"

    # Clean up the temporary file
    os.remove(temp_pdf_path)

    # Return JSON response
    return jsonify(results)