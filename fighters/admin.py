from django.contrib import admin
from django.utils.html import format_html
from .models import StarGGTournament, ChallongeTournament, Post


admin.site.register(StarGGTournament)
class ChallongeTournamentAdmin(admin.ModelAdmin):
    # Define los campos que se mostrarán en el formulario de edición
    fields = ('idTournament','stream_url')
    
    # Campos solo lectura
    readonly_fields = ('name', 'is_completed')
    
    def get_readonly_fields(self, request, obj=None):
        # Si el objeto ya existe, solo 'name' y 'is_completed' serán solo lectura
        if obj:
            return ('name', 'is_completed')
        # Si se está creando un nuevo objeto, solo 'name' y 'is_completed' no se mostrarán
        return ()

    def get_fields(self, request, obj=None):
        # Si se está creando un nuevo objeto, solo mostrar 'idTournament'
        if obj is None:
            return ('idTournament',"flayer_img","stream_url")
        # Si se está editando un objeto, mostrar todos los campos
        return ('idTournament', 'name', 'is_completed',"flayer_img", "game_name", "stream_url")

    def save_model(self, request, obj, form, change):
        if not change:
            # Si se está creando un nuevo objeto, no hacer nada en 'name' e 'is_completed'
            obj.name = 'Pendiente'  # Puedes usar un valor por defecto o dejar en blanco
            obj.is_completed = False  # Puedes usar un valor por defecto
        super().save_model(request, obj, form, change)

admin.site.register(ChallongeTournament, ChallongeTournamentAdmin)

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at', 'thumbnail')  # Mostrar las columnas deseadas, incluida la imagen en miniatura

    def thumbnail(self, obj):
        if obj.img_url:  # Verifica si hay una imagen
            # Renderiza una imagen con tamaño adecuado
            return format_html('<img src="{}" width="100" height="auto" />', obj.img_url.url)
        return ""  # Si no hay imagen, no muestra nada

    thumbnail.short_description = 'Imagen'  # Texto que aparece en el encabezado de la columna

# Registra el modelo con el admin
admin.site.register(Post, PostAdmin)
