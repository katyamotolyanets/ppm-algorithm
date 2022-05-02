from werkzeug.routing import ValidationError

ALLOWED_EXTENSIONS = {'txt', }


class FileValidator:
    messages = {
        "not_exists": 'No file part',
        "empty_filename": 'No selected file',
        "incorrect_extension": 'Not allowed file extension'
    }

    def __init__(self, file):
        self.file = file
        self.filename = file.filename

    def _allowed_file(self):
        return (
                '.' in self.filename and
                self.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    def validate_request_file(self):
        if not self.file:
            self._raise_error('not_exists')
        if not self.filename:
            self._raise_error('empty_filename')
        if not self._allowed_file():
            self._raise_error('incorrect_extension')

    def _raise_error(self, message_key):
        raise ValidationError(self.messages[message_key])

