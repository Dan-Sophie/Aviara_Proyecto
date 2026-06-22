"""
Script para cargar los productos iniciales de Aviara.
Corre con: python manage.py shell < cargar_productos.py
"""

from productos.models import Categoria, Detalle_Avicola, Detalle_Agricola

# ── Crear categorías ──────────────────────────────────────────────────────────
cat_avicola, _ = Categoria.objects.get_or_create(nombre_categoria='Avícola')
cat_agricola, _ = Categoria.objects.get_or_create(nombre_categoria='Agrícola')

print("✅ Categorías listas")

# ── Productos avícolas ────────────────────────────────────────────────────────
avicolas = [
    # (nombre, talla, color, calidad, presentacion, precio)
    ('Huevo tipo A blanco',       'A',   'Blanco', 'A',   'x30', 12000),
    ('Huevo tipo A rojo',         'A',   'Rojo',   'A',   'x30', 12000),
    ('Huevo tipo AA blanco',      'AA',  'Blanco', 'AA',  'x30', 14000),
    ('Huevo tipo AA rojo',        'AA',  'Rojo',   'AA',  'x30', 14000),
    ('Huevo tipo AAA blanco',     'AAA', 'Blanco', 'AAA', 'x30', 16000),
    ('Huevo tipo AAA rojo',       'AAA', 'Rojo',   'AAA', 'x30', 16000),
    ('Huevo tipo A café',         'A',   'Café',   'A',   'x30', 12500),
    ('Huevo tipo AA café',        'AA',  'Café',   'AA',  'x30', 14500),
    ('Huevo tipo AAA café',       'AAA', 'Café',   'AAA', 'x30', 16500),
    ('Huevo tipo A criollo',      'A',   'Criollo','A',   'x30', 13000),
    ('Huevo tipo AA criollo',     'AA',  'Criollo','AA',  'x30', 15000),
    ('Huevo tipo AAA criollo',    'AAA', 'Criollo','AAA', 'x30', 17000),
    ('Huevo blanco extra grande', 'XL',  'Blanco', 'AAA', 'x30', 18000),
    ('Huevo rojo extra grande',   'XL',  'Rojo',   'AAA', 'x30', 18000),
    ('Huevo criollo extra grande','XL',  'Criollo','AAA', 'x30', 19000),
]

for nombre, talla, color, calidad, presentacion, precio in avicolas:
    obj, created = Detalle_Avicola.objects.get_or_create(
        nombre=nombre,
        defaults={
            'descripcion': f'Huevo {color.lower()} talla {talla}. Fresco y de alta calidad.',
            'precio': precio,
            'unidad_medida': 'cubeta',
            'stock': 100,
            'stock_minimo_global': 10,
            'categoria': cat_avicola,
            'talla': talla,
            'color_huevo': color,
            'tipo_empaque': 'Cubeta plástica',
            'categoria_calidad': calidad,
            'limpieza': True,
            'presentacion': presentacion,
        }
    )
    print(f"  {'✅ Creado' if created else '⚠️  Ya existe'}: {nombre}")

print(f"\n✅ Productos avícolas listos")

# ── Productos agrícolas ───────────────────────────────────────────────────────
agricolas = [
    # (nombre, variedad, madurez, precio, unidad)
    ('Lechuga',    'Batavia',   'Lista para consumo', 2500,  'und'),
    ('Tomate',     'Chonto',    'En maduración',      3000,  'kg'),
    ('Cebolla',    'Cabezona',  'Lista para consumo', 2800,  'kg'),
    ('Zanahoria',  'Chantenay', 'Lista para consumo', 2500,  'kg'),
    ('Pepino',     'Common',    'En maduración',      2000,  'und'),
    ('Espinaca',   'Gigante',   'Lista para consumo', 3500,  'atado'),
    ('Acelga',     'Común',     'Lista para consumo', 3000,  'atado'),
    ('Brócoli',    'Premium',   'Lista para consumo', 4000,  'und'),
    ('Coliflor',   'Blanca',    'Lista para consumo', 4500,  'und'),
    ('Repollo',    'Liso',      'Lista para consumo', 3000,  'und'),
    ('Pimentón',   'Rojo',      'En maduración',      5000,  'kg'),
    ('Yuca',       'Criolla',   'Lista para consumo', 2000,  'kg'),
    ('Fresa',      'Dorada',    'Lista para consumo', 6000,  '250g'),
    ('Mora',       'Castilla',  'Lista para consumo', 5500,  '250g'),
    ('Uva',        'Isabella',  'Lista para consumo', 7000,  '500g'),
    ('Maracuyá',   'Amarilla',  'En maduración',      4000,  'kg'),
]

for nombre, variedad, madurez, precio, unidad in agricolas:
    obj, created = Detalle_Agricola.objects.get_or_create(
        nombre=nombre,
        defaults={
            'descripcion': f'{nombre} fresco(a) de cultivo propio. Cosechado con buenas prácticas agrícolas.',
            'precio': precio,
            'unidad_medida': unidad,
            'stock': 50,
            'stock_minimo_global': 5,
            'categoria': cat_agricola,
            'variedad': variedad,
            'estado_madurez': madurez,
            'tratamiento': 'Lavado y seleccionado',
            'humedad_optima': '80-90%',
            'fecha_cosecha': None,
        }
    )
    print(f"  {'✅ Creado' if created else '⚠️  Ya existe'}: {nombre}")

print(f"\n✅ Productos agrícolas listos")
print("\n🎉 ¡Todo cargado! Entra al admin para editar precios, stock e imágenes.")
