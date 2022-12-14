# Generated by Django 3.2.14 on 2022-08-16 03:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('operadores', '0001_initial'),
        ('persona', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Socio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('operador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='operadores.operador')),
                ('persona', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='persona.persona')),
                ('referidor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='socios.socio')),
            ],
        ),
    ]
