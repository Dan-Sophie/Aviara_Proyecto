from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0002_campos_nuevos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='unidad_medida',
            field=models.CharField(
                max_length=10,
                choices=[
                    ('lb', 'Libra (lb)'),
                    ('kg', 'Kilogramo (kg)'),
                    ('und', 'Unidad (und)'),
                    ('atado', 'Atado'),
                    ('500g', '500 gramos'),
                    ('250g', '250 gramos'),
                ],
                default='lb',
                verbose_name='Unidad de medida',
            ),
        ),
    ]
