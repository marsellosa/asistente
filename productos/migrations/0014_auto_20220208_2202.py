# Generated by Django 2.2.22 on 2022-02-09 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('productos', '0013_auto_20220129_2352'),
    ]

    operations = [
        migrations.RenameField(
            model_name='porcion',
            old_name='porciones_frasco',
            new_name='medida',
        ),
        migrations.RenameField(
            model_name='porcion',
            old_name='precio_medida',
            new_name='precio',
        ),
        migrations.RenameField(
            model_name='porcion',
            old_name='tipo_medida',
            new_name='unidad',
        ),
        migrations.RemoveField(
            model_name='porcion',
            name='medidas_porcion',
        ),
        migrations.AddField(
            model_name='categoria',
            name='detalle',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='categoria',
            name='tipo',
            field=models.CharField(choices=[('hmp', 'HMP'), ('nutricion', (('interna', 'INTERNA'), ('externa', 'EXTERNA'))), ('promocion', (('utensilios', 'UTENSILIOS'), ('literatura', 'LITERATURA')))], default='interna', max_length=32),
        ),
    ]
