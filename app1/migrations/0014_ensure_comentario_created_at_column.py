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


def ensure_created_at(apps, schema_editor):
    """
    Garante que a coluna created_at exista no banco (deploy e ambientes novos).
    Se criada agora, reaproveita o valor de criado_em quando estiver presente.
    """
    table_name = "app1_comentario"
    existing = _existing_columns(schema_editor, table_name)
    Comentario = apps.get_model("app1", "Comentario")
    qn = schema_editor.quote_name

    if "created_at" not in existing:
        field = Comentario._meta.get_field("created_at")
        schema_editor.add_field(Comentario, field)
        existing.add("created_at")

    if "criado_em" in existing:
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
        ("app1", "0013_alter_comentario_options"),
    ]

    operations = [
        migrations.RunPython(ensure_created_at, migrations.RunPython.noop),
    ]
