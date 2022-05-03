import os
import time

from flask import Flask, render_template, request, redirect, flash, url_for
from werkzeug.exceptions import NotFound
from flask import send_from_directory
from werkzeug.routing import ValidationError
from werkzeug.utils import secure_filename

from server.services import compressing, decompressing
from server.validation import FileValidator

UPLOAD_FOLDER = './uploaded_files'
template_dir = os.path.abspath('server/templates')
static_dir = os.path.abspath('server/static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)
app.add_url_rule(
    "/", endpoint="main", build_only=True
)


@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        try:
            file = request.files.get('file', None)
            FileValidator(file).validate_request_file()
            filename = f"{time.strftime('%H%M%S')}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if 'decompress' in request.args:
                context = decompressing(file, filepath)
            else:
                context = compressing(file, filepath)
            return redirect(url_for('main', **context))
        except ValidationError as err:
            flash(str(err))
            return redirect('/')
        except Exception:
            flash("Incorrect file data")
            return redirect('/')
    return render_template('index.html', **request.args)


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
