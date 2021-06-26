from PIL import Image

from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import permissions, status
from rest_framework.exceptions import ParseError, UnsupportedMediaType
from rest_framework.generics import RetrieveAPIView
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from shared import schema as shared_schema

from .models import PhotoUpload
from .serializers import PhotoUploadSerializer
from .parsers import PhotoUploadParser
from .utils.filetypes import get_mime_type


class PhotoUploadCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [PhotoUploadParser]

    @swagger_auto_schema(
        operation_id='photo-upload-create',
        responses={
            201: PhotoUploadSerializer(),
            400: shared_schema.photo_upload_400_response,
            401: shared_schema.unauthorized_401_response,
            415: shared_schema.photo_upload_415_response
        },
        manual_parameters=[
            openapi.Parameter(
                'filename',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description=_('The filename including the extension.')
            )
        ],
        tags=['Photos']
    )
    def post(self, request, filename, format=None):
        """
        Photo Upload Create

        Upload a new photo for an authenticated user. Files are uploaded
        as a form data. Only image files are accepted by the endpoint.
        The filename *must* be included at the end of the endpoint.

        **HTTP Request** <br />
        `POST /photos/uploads/<filename>`

        **URL Parameters** <br />
        - `filename`: The filename of the uploaded (including the extension)

        **Response Body** <br />
        - Photo ID
        - Photo URL
        - Created Date & Time
        """
        file_obj = request.data.get('file')

        if file_obj is None:
            raise ParseError(_('No image file included.'))

        # Media/Mime Type
        media_type = get_mime_type(file_obj)

        try:
            img = Image.open(file_obj)
            img.verify()
        except:
            err_message = _(f'Unsupported file type.')
            raise UnsupportedMediaType(media_type, detail=err_message)

        upload = PhotoUpload.objects.create(owner=request.user)
        upload.photo.save(file_obj.name, file_obj, save=True)
        serializer = PhotoUploadSerializer(upload)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name='get',
    decorator=swagger_auto_schema(
        operation_id='photo-upload-detail',
        responses={
            200: PhotoUploadSerializer(),
            401: shared_schema.unauthorized_401_response,
            404: shared_schema.not_found_404_response
        },
        tags=['Photos']
    )
)
class PhotoUploadRetrieveView(RetrieveAPIView):
    """
    get:
    Photo Upload Detail

    Returns an uploaded photo object by the current authenticated user, using
    the photo ID.

    **HTTP Request** <br />
    `GET /photos/uploads/<photo_id>/`

    **URL Parameters** <br />
    - `photo_id`: The ID of the uploaded photo object.

    **Response Body** <br />
    - Photo ID
    - Photo URL
    - Created Date & Time
    """
    queryset = PhotoUpload.objects.all()
    serializer_class = PhotoUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
