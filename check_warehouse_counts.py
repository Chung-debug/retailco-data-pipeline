import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="warehouse",
    user="postgres",
    password="6278"
)

cur = conn.cursor()

queries = [
    ("stores", "select count(*) from raw.stores"),
    ("employees", "select count(*) from raw.employees"),
    ("payment_methods", "select count(*) from raw.payment_methods"),
    ("customers", "select count(*) from raw.customers"),
    ("products", "select count(*) from raw.products"),
    ("orders", "select count(*) from raw.orders"),
    ("order_items", "select count(*) from raw.order_items"),
    ("payments", "select count(*) from raw.payments"),
    ("inventory_movements", "select count(*) from raw.inventory_movements"),
]

print("Warehouse row counts")
print("-" * 40)

for name, sql in queries:
    cur.execute(sql)
    count = cur.fetchone()[0]
    print(f"{name}: {count}")

conn.close()
