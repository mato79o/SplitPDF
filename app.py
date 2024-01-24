from flask import Flask, request, jsonify, render_template, send_file, redirect, url_for
import PyPDF2
import io
import base64
from flask_cors import CORS
from flask import Response

app = Flask(__name__)
CORS(app)

# A global list to store base64 encoded pages
encoded_pages = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global encoded_pages
    file = request.files.get('file')
    if file and allowed_file(file.filename):
        try:
            # Read and split the PDF file
            reader = PyPDF2.PdfReader(file.stream)
            encoded_pages.clear()  # Clear the previous session's data

            for page_number in range(len(reader.pages)):
                writer = PyPDF2.PdfWriter()
                writer.add_page(reader.pages[page_number])
                output = io.BytesIO()
                writer.write(output)
                encoded_page = base64.b64encode(output.getvalue()).decode('utf-8')
                encoded_pages.append(encoded_page)

                print(f'Obdelava strani {page_number + 1} je uspešna.')

            # Redirect to the preview page after processing
            return redirect(url_for('preview_page'))
        except Exception as e:
            return jsonify({'error': 'Failed to process file'}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/preview')
def preview_page():
    global encoded_pages  # Dodaj to, da lahko dostopate do globalnega seznama
    
    # Tiskaj dolžino seznama encoded_pages
    print("Dolžina seznama encoded_pages:", len(encoded_pages))

    # Render the preview page with the encoded pages
    return render_template('preview.html', pages=encoded_pages)

@app.route('/download/<int:page_number>')
def download_page(page_number):
    # Provide a download for the individual PDF page
    try:
        if 0 <= page_number < len(encoded_pages):
            pdf_data = base64.b64decode(encoded_pages[page_number])
            response = Response(io.BytesIO(pdf_data))
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=page_{page_number + 1}.pdf'
            return response
        else:
            return jsonify({'error': 'Page number out of range'}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to download file'}), 500

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}

if __name__ == '__main__':
    app.run(debug=False)
