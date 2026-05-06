import psycopg2
conn = psycopg2.connect(dbname='qldd_db', user='postgres', password='Nghia23042005az', host='localhost')
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'myapp_thuadat';")
for row in cur.fetchall():
    print(row)
