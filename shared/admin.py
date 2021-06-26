from django.contrib import admin


from .models import PhotoUpload


@admin.register(PhotoUpload)
class PhotoUploadAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'created_at')
    list_filter = ('created_at', )
