from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import text


"""
==========================================
CONFIG
==========================================
"""

POSTGRES_URL = (
    "postgresql://postgres:1212@localhost/dentista_db"
)

SQLITE_URL = (
    "sqlite:///./dentista.db"
)


"""
==========================================
ENGINES
==========================================
"""

postgres_engine = create_engine(
    POSTGRES_URL
)

sqlite_engine = create_engine(
    SQLITE_URL,
    connect_args={
        "check_same_thread": False
    }
)


"""
==========================================
TABLE ORDER
==========================================
Importante:
El orden respeta relaciones básicas.
==========================================
"""

TABLES_ORDER = [

    "users",

    "servicios_catalogo",

    "clientes",

    "direcciones",

    "historiales",

    "odontogramas",

    "tratamientos",

    "citas",

    "ingresos",

    "servicios",

    "egresos",

    "actividad_sistema"

]


"""
==========================================
DELETE ORDER
==========================================
Para limpiar SQLite antes de migrar.
Se borra en orden inverso.
==========================================
"""

DELETE_ORDER = list(
    reversed(TABLES_ORDER)
)


def reflect_metadata():

    postgres_meta = MetaData()

    sqlite_meta = MetaData()

    postgres_meta.reflect(
        bind=postgres_engine
    )

    sqlite_meta.reflect(
        bind=sqlite_engine
    )

    return (
        postgres_meta,
        sqlite_meta
    )


def clear_sqlite_data(
    sqlite_conn,
    sqlite_meta
):

    print("")
    print("==========================================")
    print("LIMPIANDO SQLITE")
    print("==========================================")

    sqlite_conn.execute(
        text("PRAGMA foreign_keys=OFF")
    )

    for table_name in DELETE_ORDER:

        if table_name not in sqlite_meta.tables:

            print(
                f"SQLite no tiene tabla: {table_name}"
            )

            continue

        print(
            f"Borrando {table_name}..."
        )

        sqlite_conn.execute(
            text(f'DELETE FROM "{table_name}"')
        )

    try:

        sqlite_conn.execute(
            text("DELETE FROM sqlite_sequence")
        )

    except Exception:

        pass

    sqlite_conn.execute(
        text("PRAGMA foreign_keys=ON")
    )


def migrate_table(
    table_name,
    postgres_conn,
    sqlite_conn,
    postgres_meta,
    sqlite_meta
):

    if table_name not in postgres_meta.tables:

        print(
            f"PostgreSQL no tiene tabla: {table_name}"
        )

        return

    if table_name not in sqlite_meta.tables:

        print(
            f"SQLite no tiene tabla: {table_name}"
        )

        return

    pg_table = postgres_meta.tables[
        table_name
    ]

    sqlite_table = sqlite_meta.tables[
        table_name
    ]

    rows = postgres_conn.execute(
        pg_table.select()
    ).mappings().all()

    if not rows:

        print(
            f"{table_name}: 0 registros"
        )

        return

    rows_as_dicts = [
        dict(row)
        for row in rows
    ]

    sqlite_conn.execute(
        sqlite_table.insert(),
        rows_as_dicts
    )

    print(
        f"{table_name}: {len(rows_as_dicts)} registros migrados"
    )


def main():

    print("")
    print("==========================================")
    print("MIGRANDO POSTGRESQL → SQLITE")
    print("==========================================")

    (
        postgres_meta,
        sqlite_meta
    ) = reflect_metadata()

    with postgres_engine.connect() as postgres_conn:

        with sqlite_engine.begin() as sqlite_conn:

            clear_sqlite_data(
                sqlite_conn,
                sqlite_meta
            )

            print("")
            print("==========================================")
            print("COPIANDO DATOS")
            print("==========================================")

            for table_name in TABLES_ORDER:

                migrate_table(
                    table_name,
                    postgres_conn,
                    sqlite_conn,
                    postgres_meta,
                    sqlite_meta
                )

    print("")
    print("==========================================")
    print("MIGRACIÓN COMPLETADA ✅")
    print("==========================================")
    print("")
    print("Ahora puedes probar el backend con SQLite.")
    print("")


if __name__ == "__main__":

    main()