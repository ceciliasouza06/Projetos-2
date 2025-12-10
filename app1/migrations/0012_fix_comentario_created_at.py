# Keep DB column created_at and drop state-only field criado_em.
from django.db import migrations, models


def _existing_columns(schema_editor, table_name):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        return {
            getattr(col, "name", col[0])
            for col in connection.introspection.get_table_description(
                cursor, table_name
            )
        }


def add_created_at_column(apps, schema_editor):
    table_name = "app1_comentario"
    columns = _existing_columns(schema_editor, table_name)
    Comentario = apps.get_model("app1", "Comentario")
    qn = schema_editor.quote_name

    if "created_at" not in columns:
        field = Comentario._meta.get_field("created_at")
        schema_editor.add_field(Comentario, field)
        columns.add("created_at")

    if "criado_em" in columns:
        schema_editor.execute(
            f"UPDATE {qn(table_name)} "
            f"SET {qn('created_at')} = COALESCE({qn('created_at')}, {qn('criado_em')}, CURRENT_TIMESTAMP)"
        )
    else:
        schema_editor.execute(
            f"UPDATE {qn(table_name)} "
            f"SET {qn('created_at')} = COALESCE({qn('created_at')}, CURRENT_TIMESTAMP)"
        )


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
                migrations.RunPython(
                    add_created_at_column, migrations.RunPython.noop
                ),
            ],
        ),
    ]
