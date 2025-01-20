# Generated by Django 5.1.5 on 2025-01-20 15:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_game_gamehistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamehistory',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='game.game'),
        ),
        migrations.AlterField(
            model_name='gamehistory',
            name='move',
            field=models.CharField(max_length=1),
        ),
        migrations.AlterField(
            model_name='gamehistory',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_moves', to=settings.AUTH_USER_MODEL),
        ),
    ]
