import psycopg2
import sys

def run_migration():
    # Use standard Supabase postgres string with sslmode=require
    url = "postgresql://postgres:K5H92z-LN9Z.dy-@db.ramenghkpvipxijhfptp.supabase.co:5432/postgres?sslmode=require"
    
    with open("manual_migration.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    print("Connecting to Supabase...")
    try:
        conn = psycopg2.connect(url)
        conn.autocommit = True
        with conn.cursor() as cur:
            print("Connected! Running migration...")
            cur.execute(sql)
            print("Migration complete.")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
