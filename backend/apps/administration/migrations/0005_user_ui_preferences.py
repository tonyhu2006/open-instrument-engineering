from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("administration", "0004_remove_projectmembership"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="ui_preferences",
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text=(
                    "Persisted UI preferences (column widths, theme overrides, etc.). "
                    "Structure: { tableWidths: { <storageKey>: { <colKey>: <px> } }, ... }"
                ),
            ),
        ),
    ]
