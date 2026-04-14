from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_add_ifsc_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='can_transfer_enabled',
            field=models.BooleanField(
                default=False,
                help_text='Admin-controlled switch that allows this user to make wire transfers.'
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='transfer_block_message',
            field=models.TextField(
                blank=True,
                help_text='Custom message shown to the user when wire transfers are blocked.',
                null=True
            ),
        ),
    ]
