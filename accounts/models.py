from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями.
    Username остаётся обязательным как в базовой модели.
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Администратор')
        CONTENT_MANAGER = 'content_manager', _('Контент-менеджер')
        CRM_MANAGER = 'crm_manager', _('CRM-менеджер')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONTENT_MANAGER,
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    
    # Поле email уже есть в AbstractUser, но сделаем его уникальным
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _('Пользователь с таким email уже существует.'),
        }
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        """
        Автоматически устанавливаем is_staff и is_superuser в зависимости от роли.
        
        Логика работы:
        1. Если пользователь создаётся через createsuperuser, у него уже будут
           установлены флаги is_staff=True и is_superuser=True, но роль будет
           по умолчанию CONTENT_MANAGER. Мы должны это исправить.
        
        2. Если пользователь создаётся через админку или код с явно указанной
           ролью ADMIN, мы должны убедиться, что флаги is_staff и is_superuser
           установлены правильно.
        
        3. Для контент-менеджеров и CRM-менеджеров is_superuser должен быть False,
           но is_staff должен быть True (чтобы они могли заходить в админку).
        
        4. Если роль не соответствует флагам (например, кто-то вручную выставил
           is_superuser=True у контент-менеджера), мы приводим флаги в соответствие
           с ролью, так как роль у нас первична.
        """
        
        # ШАГ 1: Обработка суперпользователя, созданного через createsuperuser
        # Проверяем: это новая запись? (нет pk) И у неё is_superuser=True?
        # И роль при этом всё ещё CONTENT_MANAGER (значение по умолчанию)?
        if not self.pk and self.is_superuser and self.role == self.Role.CONTENT_MANAGER:
            # Значит, пользователь создаётся через createsuperuser
            # Меняем роль на ADMIN, так как суперпользователь должен быть администратором
            self.role = self.Role.ADMIN
            print(f'[DEBUG] Суперпользователь {self.username} автоматически получил роль ADMIN')
        
        # ШАГ 2: Устанавливаем флаги в соответствии с ролью
        # Роль ADMIN -> is_staff=True, is_superuser=True
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        
        # Роль CONTENT_MANAGER или CRM_MANAGER -> is_staff=True, is_superuser=False
        elif self.role in [self.Role.CONTENT_MANAGER, self.Role.CRM_MANAGER]:
            self.is_staff = True
            self.is_superuser = False
        
        # На всякий случай (если вдруг роль какая-то другая)
        else:
            self.is_staff = False
            self.is_superuser = False
        
        # ШАГ 3: Валидация — если флаги не соответствуют роли, но роль указана явно,
        # мы уже исправили флаги выше. Но если флаги были установлены вручную,
        # а роль осталась старая, мы тоже всё исправили.
        # Это гарантирует, что роль всегда определяет права.
        
        # ШАГ 4: Автозаполнение username из email (как в учебнике Дронова)
        # Если username не указан, но есть email
        if not self.username and self.email:
            # Берём часть email до @
            base_username = self.email.split('@')[0]
            # Проверяем, не занят ли такой username
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            self.username = username
            print(f'[DEBUG] Для пользователя {self.email} автоматически создан username: {self.username}')
        
        # ШАГ 5: Вызов родительского метода save
        super().save(*args, **kwargs)
    
    def promote_to_admin(self):
        """
        Метод для повышения пользователя до администратора.
        Можно вызвать из консоли или кода.
        """
        self.role = self.Role.ADMIN
        self.save()  # save() сам выставит правильные флаги
        print(f'Пользователь {self.username} повышен до администратора')
    
    def demote_to_content_manager(self):
        """
        Метод для понижения пользователя до контент-менеджера.
        """
        self.role = self.Role.CONTENT_MANAGER
        self.save()
        print(f'Пользователь {self.username} понижен до контент-менеджера')
    
    def demote_to_crm_manager(self):
        """
        Метод для понижения пользователя до CRM-менеджера.
        """
        self.role = self.Role.CRM_MANAGER
        self.save()
        print(f'Пользователь {self.username} понижен до CRM-менеджера')