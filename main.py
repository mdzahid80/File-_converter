from email import message
from flask import Flask, render_template, request, send_from_directory, session, send_file
import os
from flask_bootstrap import Bootstrap5
from flask_socketio import SocketIO, emit
from flask_login import current_user, logout_user
from pdf2docx import Converter
import img2pdf
import aspose.slides as slides
import time
import asyncio



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
socketio = SocketIO(app)

# Temporary directory path for storing uploaded files
UPLOAD_FOLDER = 'D:\\C++\\Python Mini Projects\\File Converter\\uploads'
DOWNLOAD_FOLDER = 'D:\\C++\\Python Mini Projects\\File Converter\\downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# allowed extensions for file uploads
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'jpg', 'jpeg', 'png', 'pptx'}
# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template("index.html")

#?? 

@app.route('/file-select', methods=['POST'])
async def file_sel():
    if request.method == 'POST':
        # Get uploaded file
        uploaded_file = request.files['file']
        conversion_format = request.form['convert_to']

        # Check if file is selected
        if uploaded_file.filename == '':
            return render_template('converter.html', error='Please select a file to convert.')

        # Check allowed extension
        if not allowed_file(uploaded_file.filename):
            return render_template('converter.html', error='Invalid file format.')

        # Generate a unique filename
        if not uploaded_file.filename.endswith(".jpg"):
            filename = uploaded_file.filename.rsplit('.', 1)[0]
        else:
            filename=uploaded_file.filename

        # Save uploaded file
        uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session['filename'] = filename
        session['conversion_format'] = conversion_format

       
        asyncio.create_task(cleanup_files())
        return render_template("converter.html", msg=uploaded_file, msg1=conversion_format )
    
@app.route('/converter', methods=['GET','POST'])
def converter():

        filename = session.get('filename')
        conversion_format = session.get('conversion_format')
        if not filename:
            return 'No file uploaded'
    
        # Perform conversion based on format (implement conversion logic here)
        converted_filename = convert_file(filename, conversion_format)
        session['converted_file'] = converted_filename

        # Handle conversion errors (replace with specific error handling)
        if not converted_filename:
            return render_template('converter.html', error='Conversion failed.')

        return render_template('download.html', success=True)
    
@app.route('/download')
def download_file():
    file_path = session.get('converted_file')
    if not file_path:
        return 'No file to download'

    return send_file(file_path, as_attachment=True)


def convert_file(filename, conversion_format):
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    converted_filename = None
    
    if conversion_format == 'pdf_to_word':
        converted_filename = "converted_" + os.path.splitext(filename)[0] + ".docx"
        converted_path = os.path.join(app.config['DOWNLOAD_FOLDER'], converted_filename)
        print(converted_path)
        cv = Converter(original_path)
        cv.convert(converted_path, start=0, end=None)
        cv.close()
        

    elif conversion_format == 'img_to_pdf':
        converted_filename = "converted_" + os.path.splitext(filename)[0] + ".pdf"
        converted_path = os.path.join(app.config['DOWNLOAD_FOLDER'], converted_filename)
        # convert all files ending in .jpg in a directory and its subdirectories
        dirname = UPLOAD_FOLDER
        imgs = []
        for r, _, f in os.walk(dirname):
            for fname in f:
                if not fname.endswith(".jpg"):
                    continue
                imgs.append(os.path.join(r, fname))
        with open(converted_path,"wb") as f:
            f.write(img2pdf.convert(imgs))


    elif conversion_format == 'pdf_to_ppt':
        converted_filename = "converted_" + os.path.splitext(filename)[0] + ".pptx"
        converted_path = os.path.join(app.config['DOWNLOAD_FOLDER'], converted_filename)
        with slides.Presentation() as pres:
            # import PDF data to the slide
            pres.slides.add_from_pdf(original_path)
            # save the PPT file
            pres.save(converted_path, slides.export.SaveFormat.PPTX)
        
    elif conversion_format == 'original':
        # Return the original filename for downloading without conversion
        converted_filename = filename

    else:
        # Handle unsupported conversion formats
        return None
    
    return converted_path



async def cleanup_files():
    print("cleanup_files started")
        
    UP_file_path = os.path.join(app.config['UPLOAD_FOLDER'], session['filename'])
    DW_file_path = (session['converted_file'])
    if(UP_file_path or DW_file_path):
        print("UP_file_path")
        print("DW_file_path")
        await asyncio.sleep(60)
        if os.path.exists(UP_file_path):
            print("remove_start")
            os.remove(UP_file_path)
            print("removed upload")
        if os.path.exists(DW_file_path):
            os.remove(DW_file_path)
            print("removed download")
    return

if __name__ == "__main__":
    app.run(debug=True, port=5001)