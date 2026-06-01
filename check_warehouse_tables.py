import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="warehouse",
    user="postgres",
    password="6278"
)

cur = conn.cursor()

# Check current database and schema
cur.execute("select current_database(), current_schema();")
print("DB/Schema:", cur.fetchone())

# List all user tables
cur.execute("""
    select schemaname, tablename
    from pg_tables
    where schemaname not in ('pg_catalog', 'information_schema')
    order by schemaname, tablename
""")
rows = cur.fetchall()

print("Tables found:", len(rows))
for row in rows[:100]:
    print(row)

conn.close()