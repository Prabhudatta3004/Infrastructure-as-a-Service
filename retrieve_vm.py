import sqlite3
from prettytable import PrettyTable

def retrieve_vms():
    """Retrieve and display all VMs from the database."""
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()

    # Fetching all VM details
    cursor.execute("""
        SELECT tenant_uuid, subnet_id, vm_name, vm_memory, vm_vcpus, bridge_name
        FROM vms
    """)
    vms = cursor.fetchall()

    # Display results using PrettyTable
    table = PrettyTable()
    table.field_names = ["Tenant UUID", "Subnet ID", "VM Name", "Memory (MB)", "vCPUs", "Bridge Name"]
    for vm in vms:
        table.add_row([vm[0], vm[1], vm[2], vm[3], vm[4], vm[5]])

    print(table)

def main():
    print("Retrieving all VMs...")
    retrieve_vms()

if __name__ == "__main__":
    main()
