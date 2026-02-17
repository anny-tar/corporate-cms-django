import os
import shutil
from pathlib import Path
from django.db.models.signals import pre_delete, post_delete, pre_save
from django.dispatch import receiver
from django.core.files.storage import default_storage
from django.db import connection
from .models import Image, File


@receiver(pre_delete, sender=Image)
def cleanup_image_files(sender, instance, **kwargs):
    """Удаляет файл изображения с диска при удалении записи"""
    if instance.image:
        file_path = instance.image.path
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f'Удалён файл изображения: {file_path}')


@receiver(pre_delete, sender=File)
def cleanup_file_files(sender, instance, **kwargs):
    """Удаляет файл документа с диска при удалении записи"""
    if instance.file:
        file_path = instance.file.path
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f'Удалён файл документа: {file_path}')


@receiver(pre_save, sender=Image)
def cleanup_old_image_on_change(sender, instance, **kwargs):
    """Удаляет старый файл изображения при замене на новый"""
    if not instance.pk:
        return
    
    try:
        old_instance = Image.objects.get(pk=instance.pk)
    except Image.DoesNotExist:
        return
    
    if old_instance.image and old_instance.image != instance.image:
        old_path = old_instance.image.path
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f'Удалён старый файл изображения при замене: {old_path}')


@receiver(pre_save, sender=File)
def cleanup_old_file_on_change(sender, instance, **kwargs):
    """Удаляет старый файл документа при замене на новый"""
    if not instance.pk:
        return
    
    try:
        old_instance = File.objects.get(pk=instance.pk)
    except File.DoesNotExist:
        return
    
    if old_instance.file and old_instance.file != instance.file:
        old_path = old_instance.file.path
        if os.path.exists(old_path):
            os.remove(old_path)
            print(f'Удалён старый файл документа при замене: {old_path}')


def cleanup_empty_directories(path, max_depth=3):
    """
    Рекурсивно удаляет пустые директории, поднимаясь вверх по пути.
    max_depth - ограничивает, как далеко вверх можно подниматься
    """
    if max_depth <= 0:
        return
    
    path = Path(path)
    
    # Проверяем, существует ли директория
    if not path.exists() or not path.is_dir():
        return
    
    try:
        # Если директория пуста
        if not any(path.iterdir()):
            # Удаляем её
            path.rmdir()
            print(f'Удалена пустая директория: {path}')
            
            # Поднимаемся на уровень выше и пробуем удалить родителя
            cleanup_empty_directories(path.parent, max_depth - 1)
    except (OSError, PermissionError):
        # Если не удалось удалить (например, директория не пуста или нет прав)
        pass


@receiver(post_delete, sender=Image)
def cleanup_empty_dirs_after_image(sender, instance, **kwargs):
    """
    Удаляет пустые директории после удаления файла изображения.
    Использует транзакцию.on_commit(), чтобы гарантировать,
    что всё произошло после завершения транзакции.
    """
    if instance.image:
        def remove_dirs():
            dir_path = os.path.dirname(instance.image.path)
            cleanup_empty_directories(dir_path)
        
        # Выполняем после подтверждения транзакции
        connection.on_commit(remove_dirs)


@receiver(post_delete, sender=File)
def cleanup_empty_dirs_after_file(sender, instance, **kwargs):
    """Удаляет пустые директории после удаления файла документа"""
    if instance.file:
        def remove_dirs():
            dir_path = os.path.dirname(instance.file.path)
            cleanup_empty_directories(dir_path)
        
        # Выполняем после подтверждения транзакции
        connection.on_commit(remove_dirs)