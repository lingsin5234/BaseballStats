# Generated by Django 3.0.4 on 2020-03-18 21:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseball', '0009_auto_20200317_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobrequirements',
            name='form_type',
            field=models.CharField(choices=[('import_year', 'import_year'), ('process_team', 'process_team'), ('generate_stats', 'generate_stats')], default=None, max_length=20, null=True),
        ),
    ]
