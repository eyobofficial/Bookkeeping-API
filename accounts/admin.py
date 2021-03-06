from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from business.models import BusinessAccount
from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser, Profile, Setting


class ProfileInline(admin.StackedInline):
    model = Profile
    extra = 0


class SettingInline(admin.StackedInline):
    model = Setting
    extra = 0


class BusinessAccountInline(admin.StackedInline):
    model = BusinessAccount
    extra = 1


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
            {'fields': ('phone_number', 'email', 'password', 'type')}
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
    inlines = [ProfileInline, SettingInline, BusinessAccountInline]
