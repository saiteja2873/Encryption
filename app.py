from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import PyPDF2

app = Flask(__name__, static_url_path='/static')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def encrypt_pdf(input_path, output_path, password):
    with open(input_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        pdf_writer = PyPDF2.PdfWriter()

        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        pdf_writer.encrypt(password)

        with open(output_path, 'wb') as encrypted_file:
            pdf_writer.write(encrypted_file)

def decrypt_pdf(input_path, output_path, password):
    with open(input_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)

        if pdf_reader.is_encrypted:
            pdf_reader.decrypt(password)

        pdf_writer = PyPDF2.PdfWriter()

        for page_num in range(len(pdf_reader.pages)):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        with open(output_path, 'wb') as decrypted_file:
            pdf_writer.write(decrypted_file)

@app.route('/')
def index():
    return render_template('pdf_form.html')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    if 'pdf_file' not in request.files:
        return redirect(request.url)

    file = request.files['pdf_file']
    operation = request.form['operation']
    password = request.form['password']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if operation == 'encrypt':
            output_filename = 'encrypted_' + filename
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            encrypt_pdf(file_path, output_path, password)
        elif operation == 'decrypt':
            output_filename = 'decrypted_' + filename
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            decrypt_pdf(file_path, output_path, password)

        return redirect(url_for('download_file', filename=output_filename))
    else:
        return redirect(request.url)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
