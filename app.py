from flask import Flask, render_template, request, send_file
import pandas as pd
import re
from io import BytesIO

app = Flask(__name__)

# Refined Regular expression patterns to extract website URLs and emails
website_pattern = r"https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s<>]*)?"
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Function to extract data
def extract_business_data(text):
    lines = text.strip().split("\n")
    business_data = []
    
    business_name, website, email = None, None, None
    for line in lines:
        # Check if the line is a valid URL
        if re.match(website_pattern, line):
            website = re.match(website_pattern, line).group(0).strip()
        
        # Check if the line contains an email
        elif re.search(email_pattern, line):
            email = re.search(email_pattern, line).group(0).strip()
        
        # If the line is neither, assume it's a business name
        else:
            if business_name is not None and (website or email):
                # Append only if either website or email is present
                business_data.append({
                    "Business Name": business_name,
                    "Website": website if website else None,
                    "Email": email if email else None
                })
            business_name, website, email = line.strip(), None, None
    
    # Append the last business data if either website or email is present
    if business_name is not None and (website or email):
        business_data.append({
            "Business Name": business_name,
            "Website": website if website else None,
            "Email": email if email else None
        })
    
    return business_data


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        input_text = request.form['input_text']
        
        # Extract business data from input text
        business_data_list = extract_business_data(input_text)
        
        # Convert data to a DataFrame
        df = pd.DataFrame(business_data_list)
        
        # Save the DataFrame to a BytesIO object (Excel file in memory)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        output.seek(0)

        # Send the generated file for download
        return send_file(output, download_name="business_contact_data.xlsx", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
