import magic
import mimetypes


def get_mime_type(file_obj):
    """
    Returns the media_type of a file object.
    """
    initial_pos = file_obj.tell()
    file_obj.seek(0)
    mime_type = magic.from_buffer(file_obj.read(1024), mime=True)
    file_obj.file.seek(initial_pos)
    return mime_type


def build_filename_ext(filename, mime_type):
    """
    Returns a filename with extension fr
    """
    extension = mimetypes.guess_extension(mime_type)
    return ''.join([filename, extension])
