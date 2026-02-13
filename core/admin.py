#core/admin.py
from django.contrib import admin
from .models import Image, File

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'alt_text', 'width', 'height', 'file_size', 'is_active', 'created_at')
    list_display_links = ('id', 'title')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'alt_text')
    readonly_fields = ('width', 'height', 'file_size', 'created_at', 'updated_at')
    fieldsets = (
        ('Основное', {
            'fields': ('image', 'title', 'alt_text')
        }),
        ('Служебная информация', {
            'fields': ('width', 'height', 'file_size', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'file_size', 'is_active', 'created_at')
    list_display_links = ('id', 'name')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('file_size', 'created_at', 'updated_at')