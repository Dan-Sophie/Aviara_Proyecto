from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0001_initial'),
    ]

    operations = [
        # Campo stock en Producto
        migrations.AddField(
            model_name='producto',
            name='stock',
            field=models.PositiveIntegerField(default=0, verbose_name='Stock disponible'),
        ),
        # Campo fecha_cosecha en Detalle_Agricola
        migrations.AddField(
            model_name='detalle_agricola',
            name='fecha_cosecha',
            field=models.DateField(blank=True, null=True, verbose_name='Fecha estimada de cosecha'),
        ),
        # Campo presentacion en Detalle_Avicola
        migrations.AddField(
            model_name='detalle_avicola',
            name='presentacion',
            field=models.CharField(
                choices=[('x6', 'Media docena (x6)'), ('x15', 'Media cubeta (x15)'), ('x30', 'Cubeta (x30)')],
                default='x30',
                max_length=10,
                verbose_name='Presentación',
            ),
        ),
    ]
