from django.db import migrations


def backfill_level_map(apps, schema_editor):
    """
    Every existing ACCT_MAST row starts with parent=NULL (new field), so each is
    accurately its own single-level breadcrumb: totlev=1, lev1=<own id>.
    """
    ACCT_MAST = apps.get_model('purchase', 'ACCT_MAST')
    ACCT_MAST_MAP = apps.get_model('purchase', 'ACCT_MAST_MAP')

    last_map = ACCT_MAST_MAP.objects.order_by('-acmapno').first()
    next_acmapno = (last_map.acmapno + 1) if last_map else 10000

    for account in ACCT_MAST.objects.filter(level_map__isnull=True).order_by('id'):
        ACCT_MAST_MAP.objects.create(
            acct_mast=account,
            acmapno=next_acmapno,
            totlev=1,
            lev1=account.id,
            organization=account.organization,
        )
        next_acmapno += 1


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0020_acct_mast_parent_acct_mast_map_acct_mast'),
    ]

    operations = [
        migrations.RunPython(backfill_level_map, noop_reverse),
    ]
