# Generated migration for adding association_code field to Lampi

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KTALDE_web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lampi',
            name='association_code',
            field=models.CharField(blank=True, db_index=True, max_length=6, null=True, unique=True),
        ),
    ]
