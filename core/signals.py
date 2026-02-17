import os
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage
from .models import Image, File


@receiver(pre_delete, sender=Image)
def cleanup_image_files(sender, instance, **kwargs):
    """
    Сигнал, срабатывающий ДО удаления записи Image.
    Удаляет файл изображения с диска.
    """
    if instance.image:
        # Проверяем, существует ли файл
        if default_storage.exists(instance.image.name):
            # Удаляем файл
            default_storage.delete(instance.image.name)
            print(f'Удалён файл изображения: {instance.image.name}')


@receiver(pre_delete, sender=File)
def cleanup_file_files(sender, instance, **kwargs):
    """
    Сигнал, срабатывающий ДО удаления записи File.
    Удаляет файл документа с диска.
    """
    if instance.file:
        if default_storage.exists(instance.file.name):
            default_storage.delete(instance.file.name)
            print(f'Удалён файл документа: {instance.file.name}')


# Дополнительно: сигнал для случая, когда файл перезаписывается (опционально)
@receiver(pre_delete, sender=Image)
def cleanup_empty_folders(sender, instance, **kwargs):
    """
    Опционально: пытается удалить пустые папки после удаления файла.
    Срабатывает после удаления записи.
    """
    if instance.image:
        # Получаем путь к папке файла
        dir_path = os.path.dirname(instance.image.path)
        try:
            # Пытаемся удалить папку, если она пуста
            if os.path.exists(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
                print(f'Удалена пустая папка: {dir_path}')
        except OSError:
            pass  # Игнорируем ошибки при удалении папки