# Generated by Django 5.0.4 on 2024-09-16 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fighters', '0003_challongetournament'),
    ]

    operations = [
        migrations.AddField(
            model_name='challongetournament',
            name='flayer_img',
            field=models.ImageField(blank=True, upload_to='flayers/'),
        ),
    ]
