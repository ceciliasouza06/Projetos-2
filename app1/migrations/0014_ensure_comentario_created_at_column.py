from django.db import migrations


def ensure_created_at(apps, schema_editor):
    """
    Garante que a coluna created_at exista no banco (deploy e ambientes novos).
    Se criada agora, reaproveita o valor de criado_em quando estiver presente.
    """
    conn = schema_editor.connection
    cursor = conn.cursor()
    existing = {
        row[1]
        for row in cursor.execute("PRAGMA table_info(app1_comentario);").fetchall()
    }

    if "created_at" not in existing:
        cursor.execute(
            "ALTER TABLE app1_comentario ADD COLUMN created_at datetime DEFAULT CURRENT_TIMESTAMP"
        )
        if "criado_em" in existing:
            cursor.execute(
                "UPDATE app1_comentario SET created_at = COALESCE(criado_em, CURRENT_TIMESTAMP)"
            )
    else:
        cursor.execute(
            "UPDATE app1_comentario SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP)"
        )


class Migration(migrations.Migration):
    dependencies = [
        ("app1", "0013_alter_comentario_options"),
    ]

    operations = [
        migrations.RunPython(ensure_created_at, migrations.RunPython.noop),
    ]
