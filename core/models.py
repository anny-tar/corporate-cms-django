#core/models.py
from django.db import models
import os
from django.db import models
from PIL import Image as PilImage

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
        verbose_name='Ширина'
    )
    height = models.PositiveIntegerField(
        editable=False,
        null=True,
        verbose_name='Высота'
    )
    file_size = models.PositiveIntegerField(
        editable=False,
        null=True,
        verbose_name='Размер файла (байт)'
    )

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return self.title or self.alt_text or f'Изображение {self.id}'

    def save(self, *args, **kwargs):
        """При сохранении автоматически определяем размеры и вес"""
        if self.image and not self.file_size:
            self.file_size = self.image.size
            
        # Если есть файл изображения, но нет размеров
        if self.image and not (self.width and self.height):
            try:
                img = PilImage.open(self.image.path)
                self.width, self.height = img.size
            except:
                pass
                
        super().save(*args, **kwargs)

class File(StatusModel):
    """
    Централизованное хранение всех документов сайта.
    """
    file = models.FileField(
        upload_to='files/%Y/%m/%d/',
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
        verbose_name='Размер файла (байт)'
    )

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)