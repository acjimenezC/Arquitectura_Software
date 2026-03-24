from django.core.management.base import BaseCommand
from django.core.files import File
from pathlib import Path
from apps.events.models import Evento
import os


class Command(BaseCommand):
    """Asigna imágenes reales a eventos desde carpetas organizadas por categoría"""
    
    # Mapeo de categorías a archivos de imagen en media/events/
    CATEGORIAS = {
        'Empresariales': 'organizacion-de-eventos-empresariales.jpg',
        'Conciertos': 'conciertos.jpg',
        'Deportes': 'eventos-deportivos.jpg',
        'Festivales': 'festivales.jpg',
    }
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Asignar imágenes a TODOS los eventos, incluso los que ya tienen'
        )
        parser.add_argument(
            '--media-path',
            type=str,
            default='media',
            help='Ruta a la carpeta media (default: media) - busca en media/events/'
        )
    
    def get_imagenes_por_categoria(self, media_path):
        """Obtiene las imágenes disponibles por categoría desde media/events/"""
        imagenes = {}
        media_root = Path(media_path) / 'events'  # Buscar en media/events/
        
        self.stdout.write(f"📁 Buscando imágenes en: {media_root}\n")
        
        for categoria, nombre_archivo in self.CATEGORIAS.items():
            ruta_imagen = media_root / nombre_archivo
            
            if ruta_imagen.exists():
                imagenes[categoria] = ruta_imagen
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {categoria}: {nombre_archivo}")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ {categoria}: no encontrado {nombre_archivo}")
                )
                imagenes[categoria] = None
        
        return imagenes
    
    def handle(self, *args, **options):
        media_path = options['media_path']
        
        # Obtener imágenes disponibles
        self.stdout.write("\n📁 Buscando imágenes por categoría...\n")
        imagenes_disponibles = self.get_imagenes_por_categoria(media_path)
        
        # Verificar que todas las imágenes están disponibles
        if not all(imagenes_disponibles.values()):
            self.stdout.write(
                self.style.ERROR("\n❌ Algunas imágenes no fueron encontradas. Verifica media/events/\n")
            )
            return
        
        # Procesamiento
        if options['all']:
            eventos = Evento.objects.all()
            self.stdout.write(
                self.style.WARNING('\n⚠️  Asignando a TODOS los eventos...\n')
            )
        else:
            eventos = Evento.objects.filter(imagen__exact='')
            self.stdout.write('\n🎯 Asignando a eventos sin imagen...\n')
        
        contador = 0
        
        for evento in eventos:
            categoria = evento.categoria
            imagen_path = imagenes_disponibles.get(categoria)
            
            if not imagen_path:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  {evento.nombre}: categoría '{categoria}' sin imagen disponible"
                    )
                )
                continue
            
            # Guardar imagen
            try:
                with open(imagen_path, 'rb') as img_file:
                    nombre_archivo = f"evento_{evento.id}_{imagen_path.stem}.jpg"
                    evento.imagen.save(nombre_archivo, File(img_file), save=True)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ {evento.nombre} ({categoria}): {imagen_path.name}"
                    )
                )
                contador += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"✗ Error en {evento.nombre}: {str(e)}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✅ {contador} evento(s) actualizado(s)\n')
        )
