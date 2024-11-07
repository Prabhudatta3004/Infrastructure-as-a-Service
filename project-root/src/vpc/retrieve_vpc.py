import sqlite3
from prettytable import PrettyTable

def read_tenant_uuid():
    """Reads the tenant UUID from a file, returning None if the file doesn't exist."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found.")
        return None

def retrieve_vpcs(tenant_uuid):
    """Retrieves all VPCs for the given tenant UUID."""
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT vpc_name, created_at, zone FROM vpcs WHERE tenant_uuid=?", (tenant_uuid,))
    vpcs = c.fetchall()
    conn.close()
    return vpcs

def display_vpcs(vpcs):
    """Displays VPC information in a table format."""
    table = PrettyTable()
    table.field_names = ["VPC Name", "Created At", "Zone"]
    for vpc in vpcs:
        # Ensures data is displayed for each VPC
        table.add_row([vpc[0], vpc[1], vpc[2]])
    print(table)

def main():
    tenant_uuid = read_tenant_uuid()
    if not tenant_uuid:
        print("No tenant UUID available to query VPCs.")
        return
    
    vpcs = retrieve_vpcs(tenant_uuid)
    if vpcs:
        display_vpcs(vpcs)
    else:
        print("No VPCs found for this tenant.")

if __name__ == "__main__":
    main()
