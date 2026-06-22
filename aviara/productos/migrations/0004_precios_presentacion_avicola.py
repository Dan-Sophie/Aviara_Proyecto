from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0003_unidad_medida_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalle_avicola',
            name='precio_x6',
            field=models.DecimalField(
                blank=True, null=True, max_digits=10, decimal_places=2,
                verbose_name='Precio media docena (x6)',
            ),
        ),
        migrations.AddField(
            model_name='detalle_avicola',
            name='precio_x15',
            field=models.DecimalField(
                blank=True, null=True, max_digits=10, decimal_places=2,
                verbose_name='Precio media cubeta (x15)',
            ),
        ),
        migrations.AddField(
            model_name='detalle_avicola',
            name='precio_x30',
            field=models.DecimalField(
                blank=True, null=True, max_digits=10, decimal_places=2,
                verbose_name='Precio cubeta (x30)',
            ),
        ),
    ]
