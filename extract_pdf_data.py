import PyPDF2
import pdfplumber
import mysql.connector
import os
import json  # Import JSON for converting the table to a string format

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        print(f"Processing PDF at path: {pdf_path}")

        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in range(len(reader.pages)):
                text += reader.pages[page].extract_text() or ''
            return text.strip()
    except FileNotFoundError:
        print(f"The file at {pdf_path} was not found.")
        return None

# Function to extract tables from PDF
def extract_tables_from_pdf(pdf_path):
    try:
        tables_list = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    tables_list.append(table)
        return tables_list if tables_list else None
    except Exception as e:
        print(f"Error extracting tables: {e}")
        return None

# Function to store text in MySQL database
def store_text_in_db(pdf_name, text):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Update with your password if set
            database="pdf_processor"
        )
        cursor = conn.cursor()
        cursor.execute("INSERT INTO pdf_text_data (pdf_name, text_content) VALUES (%s, %s)", (pdf_name, text))
        conn.commit()
        cursor.close()
        conn.close()
        print("Text successfully stored in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to store tables in MySQL database (formatted as string without extra brackets)
def store_tables_in_db(pdf_name, tables):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Update with your password if set
            database="pdf_processor"
        )
        cursor = conn.cursor()

        # Flatten the table to remove extra brackets
        for table in tables:
            table_str = ""
            for row in table:
                table_str += "[" + ", ".join(f'"{item}"' for item in row) + "],\n"  # Format each row as string

            # Clean up the trailing comma and newline
            table_str = table_str.strip().rstrip(',')

        # Store the formatted table (as a plain string) in the database
        cursor.execute("INSERT INTO pdf_table_data (pdf_name, table_data) VALUES (%s, %s)", (pdf_name, table_str))
        conn.commit()
        cursor.close()
        conn.close()
        print("Tables successfully stored in the database.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Main execution
pdf_path = r"C:\Users\Sanjay Bairy\OneDrive\Desktop\detailstable.pdf"  # Replace with actual PDF path

if os.path.exists(pdf_path):
    pdf_name = os.path.basename(pdf_path)
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if text:
        print("Extracted Text from PDF:")
        print(text)
        store_text_in_db(pdf_name, text)
    else:
        print("No text extracted from the PDF.")

    # Extract tables
    tables = extract_tables_from_pdf(pdf_path)
    if tables:
        print("Extracted Tables from PDF:")
        store_tables_in_db(pdf_name, tables)  
    else:
        print("No tables found in the PDF.")
else:
    print(f"File not found at {pdf_path}")
