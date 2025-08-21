__test__ = False

try:
    import psycopg2
except ImportError:  # pragma: no cover - optional dependency
    psycopg2 = None

if psycopg2:
    try:
        conn = psycopg2.connect(
            dbname="igaming",
            user="postgres",
            password="Yhazzel1966!",
            host="localhost",
            port="5432"
        )
        print("✅ Conexión exitosa a la base de datos")

        cur = conn.cursor()
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print("Versión de PostgreSQL:", db_version)

        cur.close()
        conn.close()

    except Exception as e:
        print("❌ Error al conectar:", e)
