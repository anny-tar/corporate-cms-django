import os
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from PIL import Image as PilImage


def validate_image_file(value):
    """Валидатор для изображений"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
    if ext not in valid_extensions:
        raise ValidationError(f'Неподдерживаемый формат изображения. Разрешены: {", ".join(valid_extensions)}')
    
    # Проверка MIME-типа (базовая)
    valid_mimes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp', 'image/svg+xml']
    if hasattr(value.file, 'content_type'):
        if value.file.content_type not in valid_mimes:
            raise ValidationError(f'Неподдерживаемый MIME-тип изображения')


def validate_document_file(value):
    """Валидатор для документов"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx', 
        '.ppt', '.pptx', '.txt', '.rtf', '.odt'
    ]
    if ext not in valid_extensions:
        raise ValidationError(f'Неподдерживаемый формат файла. Разрешены: {", ".join(valid_extensions)}')


class StatusModel(models.Model):
    """
    Абстрактная базовая модель для всех сущностей,
    которым требуется управление активностью и отслеживание времени.
    """
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создан'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлён'
    )

    class Meta:
        abstract = True


class SortableModel(models.Model):
    """
    Абстрактная базовая модель для всех сущностей,
    которые должны сортироваться вручную.
    """
    order = models.PositiveIntegerField(
        default=0,
        db_index=True,
        verbose_name='Порядок'
    )

    class Meta:
        abstract = True
        ordering = ['order']


class Image(StatusModel):
    """
    Централизованное хранение всех изображений сайта.
    """
    image = models.ImageField(
        upload_to='images/%Y/%m/%d/',
        validators=[validate_image_file],
        verbose_name='Изображение'
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Alt текст'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Название'
    )
    width = models.PositiveIntegerField(
        editable=False,
        null=True,
        blank=True,
        verbose_name='Ширина (пиксели)'
    )
    height = models.PositiveIntegerField(
        editable=False,
        null=True,
        blank=True,
        verbose_name='Высота (пиксели)'
    )
    file_size = models.PositiveIntegerField(
        editable=False,
        null=True,
        blank=True,
        verbose_name='Размер файла (байты)'
    )
    file_type = models.CharField(
        max_length=50,
        editable=False,
        blank=True,
        verbose_name='Тип файла'
    )

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['-created_at']

    def __str__(self):
        if self.title:
            return self.title
        if self.alt_text:
            return self.alt_text
        return f'Изображение #{self.id}'

    def save(self, *args, **kwargs):
        """При сохранении обновляем метаданные файла"""
        # Обновляем размер файла
        if self.image:
            self.file_size = self.image.size
            
            # Определяем тип файла по расширению
            ext = os.path.splitext(self.image.name)[1].lower()
            type_map = {
                '.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG',
                '.gif': 'GIF', '.bmp': 'BMP', '.webp': 'WEBP',
                '.svg': 'SVG'
            }
            self.file_type = type_map.get(ext, ext.upper().replace('.', ''))
            
            # Обновляем размеры изображения (если это не SVG)
            if ext != '.svg':
                try:
                    # Открываем файл через PIL для получения размеров
                    img = PilImage.open(self.image)
                    self.width, self.height = img.size
                except Exception as e:
                    # Если не удалось определить размеры, оставляем null
                    self.width = None
                    self.height = None
            else:
                # Для SVG размеры не определяем
                self.width = None
                self.height = None
                
        super().save(*args, **kwargs)


class File(StatusModel):
    """
    Централизованное хранение всех документов сайта.
    """
    file = models.FileField(
        upload_to='files/%Y/%m/%d/',
        validators=[validate_document_file],
        verbose_name='Файл'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    file_size = models.PositiveIntegerField(
        editable=False,
        null=True,
        blank=True,
        verbose_name='Размер файла (байты)'
    )
    file_type = models.CharField(
        max_length=50,
        editable=False,
        blank=True,
        verbose_name='Тип файла'
    )

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """При сохранении обновляем метаданные файла"""
        if self.file:
            self.file_size = self.file.size
            
            # Определяем тип файла по расширению
            ext = os.path.splitext(self.file.name)[1].lower()
            type_map = {
                '.pdf': 'PDF',
                '.doc': 'DOC', '.docx': 'DOCX',
                '.xls': 'XLS', '.xlsx': 'XLSX',
                '.ppt': 'PPT', '.pptx': 'PPTX',
                '.txt': 'TXT',
                '.rtf': 'RTF',
                '.odt': 'ODT'
            }
            self.file_type = type_map.get(ext, ext.upper().replace('.', ''))
            
        super().save(*args, **kwargs)