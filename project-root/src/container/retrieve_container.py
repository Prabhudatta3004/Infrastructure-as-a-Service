import sqlite3
from prettytable import PrettyTable

def read_tenant_uuid():
    """Reads the tenant UUID from a file."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Tenant UUID file not found. Please log in and try again.")
        return None

def retrieve_containers(tenant_uuid, vpc_name, subnet_id):
    """Retrieves and displays container information for a given tenant, VPC, and subnet using PrettyTable."""
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()
    
    query = """
    SELECT container_name, veth_host, veth_container, ovs_bridge_name
    FROM containers
    WHERE tenant_uuid=? AND vpc_name=? AND subnet_id=?
    """
    try:
        cursor.execute(query, (tenant_uuid, vpc_name, subnet_id))
        containers = cursor.fetchall()

        if containers:
            table = PrettyTable()
            table.field_names = ["Container Name", "Veth Host", "Veth Container", "OVS Bridge"]
            for container in containers:
                table.add_row([container[0], container[1], container[2], container[3]])
            print(table)
        else:
            print("No containers found for the specified VPC and subnet under this tenant.")
    except sqlite3.Error as e:
        print(f"An error occurred while retrieving containers: {e}")
    finally:
        conn.close()

def main():
    tenant_uuid = read_tenant_uuid()
    if not tenant_uuid:
        print("Tenant UUID is required to proceed.")
        return

    vpc_name = input("Enter VPC name: ")
    subnet_id = input("Enter Subnet ID: ")

    retrieve_containers(tenant_uuid, vpc_name, subnet_id)

if __name__ == "__main__":
    main()
