# Generated manually to align Comentario table with model.
from django.db import migrations


def _existing_columns(schema_editor, table_name):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        return {
            getattr(col, "name", col[0])
            for col in connection.introspection.get_table_description(
                cursor, table_name
            )
        }


def ensure_comentario_columns(apps, schema_editor):
    table_name = "app1_comentario"
    existing = _existing_columns(schema_editor, table_name)
    Comentario = apps.get_model("app1", "Comentario")

    if "avatar" not in existing:
        field = Comentario._meta.get_field("avatar")
        schema_editor.add_field(Comentario, field)
    if "criado_em" not in existing:
        field = Comentario._meta.get_field("criado_em")
        schema_editor.add_field(Comentario, field)


class Migration(migrations.Migration):

    dependencies = [
        ("app1", "0010_comentario"),
    ]

    operations = [
        migrations.RunPython(ensure_comentario_columns, migrations.RunPython.noop),
    ]
