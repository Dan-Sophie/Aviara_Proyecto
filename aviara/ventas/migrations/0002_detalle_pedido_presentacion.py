from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalle_pedido',
            name='presentacion',
            field=models.CharField(blank=True, default='', max_length=10,
                                   verbose_name='Presentación (x6/x15/x30)'),
        ),
    ]
