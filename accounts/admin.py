from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, Profile, Setting


class ProfileInline(admin.StackedInline):
    model = Profile
    exta = 0



class SettingInline(admin.StackedInline):
    model = Setting
    exta = 0


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = (
        'phone_number', 'email', 'is_active', 'is_staff',
        'is_superuser', 'last_login'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    filter_horizontal = ('user_permissions', 'groups')
    search_fields = ('email', 'phone_number')
    fieldsets = (
        (None,
            {'fields': ('phone_number', 'email', 'password')}
        ),
        ('Permissions',
            {
                'fields': (
                            'is_staff', 'is_active', 'is_superuser',
                            'groups', 'user_permissions'
                        )
            }
        ),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone_number', 'email', 'password1',
                'password2', 'is_staff', 'is_active'
            )}
        ),
    )
    ordering = ('email',)
    inlines = [ProfileInline, SettingInline]

