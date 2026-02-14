from django.contrib import admin
from django.utils.html import format_html
from .models import Image, File


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail_preview', 'id', 'title', 'file_type', 
        'dimensions_display', 'file_size_display', 'is_active', 'created_at'
    )
    list_display_links = ('thumbnail_preview', 'id', 'title')
    list_filter = ('file_type', 'is_active', 'created_at')
    search_fields = ('title', 'alt_text')
    readonly_fields = ('width', 'height', 'file_size', 'file_type', 'created_at', 'updated_at', 'image_preview')
    fieldsets = (
        ('Основное', {
            'fields': ('image', 'image_preview', 'title', 'alt_text')
        }),
        ('Метаданные файла', {
            'fields': ('file_type', ('width', 'height'), 'file_size'),
            'classes': ('wide',)
        }),
        ('Статус и даты', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        """Превью изображения в списке"""
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px; border-radius: 4px;" />',
                obj.image.url
            )
        return '-'
    thumbnail_preview.short_description = 'Превью'

    def image_preview(self, obj):
        """Превью изображения на странице редактирования"""
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 100%; border: 1px solid #ddd; '
                'border-radius: 4px; padding: 5px;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Предпросмотр'

    def dimensions_display(self, obj):
        """Отображение размеров"""
        if obj.width and obj.height:
            return f'{obj.width} × {obj.height} px'
        return '—'
    dimensions_display.short_description = 'Размеры'

    def file_size_display(self, obj):
        """Отображение размера файла в человекочитаемом формате"""
        if obj.file_size:
            size = obj.file_size
            if size < 1024:
                return f'{size} Б'
            elif size < 1024 * 1024:
                return f'{size / 1024:.1f} КБ'
            else:
                return f'{size / (1024 * 1024):.1f} МБ'
        return '—'
    file_size_display.short_description = 'Размер'


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'file_type_display', 'file_size_display', 
        'is_active', 'created_at'
    )
    list_display_links = ('id', 'name')
    list_filter = ('file_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('file_size', 'file_type', 'created_at', 'updated_at', 'file_link')
    fieldsets = (
        ('Основное', {
            'fields': ('file', 'file_link', 'name', 'description')
        }),
        ('Метаданные файла', {
            'fields': ('file_type', 'file_size'),
            'classes': ('wide',)
        }),
        ('Статус и даты', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def file_link(self, obj):
        """Ссылка на файл"""
        if obj.pk and obj.file:
            return format_html(
                '<a href="{}" target="_blank">Открыть файл</a>',
                obj.file.url
            )
        return '-'
    file_link.short_description = 'Ссылка'

    def file_type_display(self, obj):
        """Отображение типа файла с иконкой эмодзи"""
        icons = {
            'PDF': '📄',
            'DOC': '📝', 'DOCX': '📝',
            'XLS': '📊', 'XLSX': '📊',
            'PPT': '📽️', 'PPTX': '📽️',
            'TXT': '📃',
            'RTF': '📃',
            'ODT': '📃',
        }
        icon = icons.get(obj.file_type, '📁')
        return f'{icon} {obj.file_type}'
    file_type_display.short_description = 'Тип'

    def file_size_display(self, obj):
        """Отображение размера файла в человекочитаемом формате"""
        if obj.file_size:
            size = obj.file_size
            if size < 1024:
                return f'{size} Б'
            elif size < 1024 * 1024:
                return f'{size / 1024:.1f} КБ'
            else:
                return f'{size / (1024 * 1024):.1f} МБ'
        return '—'
    file_size_display.short_description = 'Размер'