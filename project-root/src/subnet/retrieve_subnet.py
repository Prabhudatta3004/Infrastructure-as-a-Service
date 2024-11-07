import sqlite3
from prettytable import PrettyTable

def read_tenant_uuid():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found.")
        return None

def retrieve_subnets_for_tenant(tenant_uuid):
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()

    vpc_name = input("Enter VPC name to retrieve subnets: ")
    print(f"Retrieving for Tenant UUID: {tenant_uuid} and VPC Name: {vpc_name}")

    query = """
    SELECT subnet_id, subnet_used, linux_bridge_name, ovs_bridge_name
    FROM subnets
    WHERE tenant_uuid=? AND vpc_name=?
    """
    cursor.execute(query, (tenant_uuid, vpc_name))
    subnets = cursor.fetchall()

    # Use PrettyTable to format the output
    table = PrettyTable()
    table.field_names = ["Subnet ID", "CIDR Block", "Linux Bridge Name", "OVS Bridge Name"]
    if subnets:
        for subnet in subnets:
            table.add_row([subnet[0], subnet[1], subnet[2], subnet[3]])
        print(table)
    else:
        print(f"No subnets found for VPC '{vpc_name}' under tenant UUID '{tenant_uuid}'.")
    conn.close()

def main():
    tenant_uuid = read_tenant_uuid()
    if tenant_uuid:
        retrieve_subnets_for_tenant(tenant_uuid)
    else:
        print("Tenant UUID is required to retrieve subnets.")

if __name__ == "__main__":
    main()
