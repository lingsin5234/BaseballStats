# Generated by Django 3.0.4 on 2020-03-11 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseball', '0007_auto_20200311_1016'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobrequirements',
            name='form_type',
            field=models.CharField(choices=[('import_year', 'import_year'), ('process_team', 'process_team'), ('gen_stats', 'gen_stats')], default=None, max_length=20, null=True),
        ),
    ]
