import os
import time


from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.exceptions import NotFound
from flask import send_from_directory
from werkzeug.routing import ValidationError
from werkzeug.utils import secure_filename

from server.services import compressing
from server.validation import FileValidator

UPLOAD_FOLDER = './uploaded_files'

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000


app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)


@app.route('/', methods=['GET', 'POST'])
def main():
    return render_template('index.html')


@app.route('/compress', methods=['POST'])
def compress_view():
    # compress(inp, bitout)
    try:
        file = request.files.get('file', None)
        FileValidator(file).validate_request_file()

        filename = f"{time.strftime('%H%M%S')}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        compressing(file, filepath)
        file.save(filepath)
        return redirect(url_for('download_file', name=filename))
    except ValidationError as err:
        flash(str(err))
        return redirect('/')


@app.route('/uploads/<name>')
def download_file(name):
    try:
        return send_from_directory(directory=app.config["UPLOAD_FOLDER"],
                                   path=name,
                                   environ="WSGIEnvironment",
                                   as_attachment=True)
    except NotFound:
        flash('File with that name not found')
        return redirect('/')


@app.route('/decompress', methods=['POST'])
def decompress_view():
    try:
        file = request.files.get('file', None)
        FileValidator(file).validate_request_file()

        filename = f"{time.strftime('%H%M%S')}_{secure_filename(file.filename)}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))
    except ValidationError as err:
        flash(str(err))
        return redirect('/')
