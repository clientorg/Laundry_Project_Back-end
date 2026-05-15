from django.db import migrations


def seed_msg91_settings(apps, schema_editor):
    AppSettings = apps.get_model('master', 'AppSettings')
    AppSettings.objects.get_or_create(
        key='msg91_auth_key',
        defaults={
            'value': '366581AeNc1jQyEhb6a03fa62P1',
            'description': 'MSG91 API auth key',
        }
    )
    AppSettings.objects.get_or_create(
        key='msg91_whatsapp_namespace',
        defaults={
            'value': 'a044e060_d204_415a_9ac4_6933a8706e28',
            'description': 'WhatsApp Business namespace from MSG91 dashboard',
        }
    )


def remove_msg91_settings(apps, schema_editor):
    AppSettings = apps.get_model('master', 'AppSettings')
    AppSettings.objects.filter(key__in=['msg91_auth_key', 'msg91_whatsapp_namespace']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0020_seed_whatsapp_number'),
    ]

    operations = [
        migrations.RunPython(seed_msg91_settings, remove_msg91_settings),
    ]
