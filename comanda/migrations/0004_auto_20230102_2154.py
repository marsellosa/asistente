# Generated by Django 3.2.14 on 2023-01-03 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prepagos', '0004_pago_usuario'),
        ('comanda', '0003_comanda_prepago'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comanda',
            name='prepago',
        ),
        migrations.AddField(
            model_name='comanda',
            name='prepago',
            field=models.ManyToManyField(blank=True, null=True, to='prepagos.Prepago'),
        ),
    ]