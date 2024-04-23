import sqlite3
def delete_tenant_by_name():
    tenant_name = input("Enter the tenant name to delete: ")
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    try:
        c.execute("SELECT uuid FROM tenants WHERE tenant_name=?", (tenant_name,))
        tenant = c.fetchone()
        if tenant:
            c.execute("DELETE FROM tenants WHERE tenant_name=?", (tenant_name,))
            conn.commit()
            print(f"Tenant '{tenant_name}' has been deleted.")
        else:
            print("Tenant not found.")
    finally:
        conn.close()
