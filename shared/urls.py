from django.urls import path


from .views import PhotoUploadCreateView, PhotoUploadRetrieveView


app_name = 'shared'

urlpatterns = [
    path(
        'photos/uploads/',
        PhotoUploadCreateView.as_view(),
        name='photo-upload-create'
    ),
    path(
        'photos/uploads/<uuid:pk>/',
        PhotoUploadRetrieveView.as_view(),
        name='photo-upload-detail'
    )
]
