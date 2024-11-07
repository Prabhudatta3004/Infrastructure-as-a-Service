import sqlite3

def show_all_tenants():
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    try:
        c.execute("SELECT uuid, tenant_name, email, created_at FROM tenants")
        tenants = c.fetchall()
        if tenants:
            print("\nList of all tenants:")
            for tenant in tenants:
                print(f"UUID: {tenant[0]}, Name: {tenant[1]}, Email: {tenant[2]}, Created At: {tenant[3]}")
        else:
            print("No tenants found.")
    finally:
        conn.close()
