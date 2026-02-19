from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """
    Форма создания пользователя для админки
    """
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля более понятными
        self.fields['email'].required = True
        self.fields['email'].help_text = _('Обязательное поле. Используется для входа.')
        self.fields['username'].help_text = _('Обязательное поле. Не более 150 символов.')
        self.fields['phone'].widget.attrs['placeholder'] = '+7 XXX XXX-XX-XX'


class CustomUserChangeForm(UserChangeForm):
    """
    Форма редактирования пользователя для админки
    """
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        # Скрываем поле password, так как оно редактируется отдельно
        if 'password' in self.fields:
            self.fields['password'].help_text = (
                'Пароль можно изменить <a href="../password/">здесь</a>.'
            )