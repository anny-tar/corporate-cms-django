from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .forms import CustomUserCreationForm, CustomUserChangeForm

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Админка для кастомной модели пользователя
    """
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Поля, отображаемые в списке пользователей
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'role_display', 'phone', 'is_active', 'date_joined'
    )
    list_display_links = ('id', 'username', 'email')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    
    # Поля для формы добавления/редактирования
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        (_('Персональная информация'), {
            'fields': ('first_name', 'last_name', 'role', 'phone')
        }),
        (_('Права доступа'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        (_('Важные даты'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
    )
    
    # Поля для формы создания (она проще)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 
                      'role', 'phone', 'password1', 'password2'),
        }),
    )
    
    def role_display(self, obj):
        """
        Отображение роли с эмодзи для наглядности
        """
        icons = {
            'admin': '👑 Администратор',
            'content_manager': '📝 Контент-менеджер',
            'crm_manager': '📊 CRM-менеджер',
        }
        return icons.get(obj.role, obj.role)
    role_display.short_description = 'Роль'
    role_display.admin_order_field = 'role'
    
    def get_readonly_fields(self, request, obj=None):
        """
        Делаем некоторые поля только для чтения при редактировании
        """
        if obj:  # Редактирование существующего пользователя
            return ('last_login', 'date_joined', 'is_superuser')
        return ()
    
    def save_model(self, request, obj, form, change):
        """
        Сохраняем пользователя с дополнительной логикой
        """
        if not change:  # Если создаётся новый пользователь
            # Устанавливаем пароль, если он был введён
            if 'password1' in form.cleaned_data:
                obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)