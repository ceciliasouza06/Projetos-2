# Keep DB column created_at and drop state-only field criado_em.
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0011_fix_comentario_columns"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name="comentario",
                    name="criado_em",
                ),
                migrations.AddField(
                    model_name="comentario",
                    name="created_at",
                    field=models.DateTimeField(
                        auto_now_add=True,
                        db_column="created_at",
                    ),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    "ALTER TABLE app1_comentario ADD COLUMN created_at datetime DEFAULT CURRENT_TIMESTAMP",
                    migrations.RunSQL.noop,
                ),
                migrations.RunSQL(
                    "UPDATE app1_comentario SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP);",
                    migrations.RunSQL.noop,
                ),
            ],
        ),
    ]
