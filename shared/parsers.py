from rest_framework.parsers import FileUploadParser


class PhotoUploadParser(FileUploadParser):
    """
    Restrict the content-type (as reported by the client during upload)
    to only accept images types.

    However, the client can lie about the content-type of the file that
    is being uploaded. Thus, additional validation is needed in the view
    to ensure an image file is sent by the client.
    """
    media_type = 'image/*'

    def get_filename(self, stream, media_type, parser_context):
        return '_'
