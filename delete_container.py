import subprocess
import sqlite3

def read_tenant_uuid():
    """Reads the tenant UUID from a file."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Tenant UUID file not found. Please log in and try again.")
        return None

def fetch_container_details(tenant_uuid, subnet_id, vpc_name, container_name):
    """ Fetches veth names from the database based on tenant UUID, subnet ID, VPC name, and container name. """
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT veth_container FROM containers
            WHERE tenant_uuid=? AND subnet_id=? AND vpc_name=? AND container_name=?
        """, (tenant_uuid, subnet_id, vpc_name, container_name))
        return cursor.fetchone()
    finally:
        conn.close()

def delete_container_entry(tenant_uuid, subnet_id, vpc_name, container_name):
    """ Deletes the container entry from the database. """
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            DELETE FROM containers
            WHERE tenant_uuid=? AND subnet_id=? AND vpc_name=? AND container_name=?
        """, (tenant_uuid, subnet_id, vpc_name, container_name))
        conn.commit()
        print("Container entry deleted from database.")
    finally:
        conn.close()

def delete_container(container_name, veth_container, tenant_uuid, subnet_id, vpc_name):
    """ Calls the Ansible playbook to delete the container using details fetched from the DB. """
    if veth_container:
        result = subprocess.run([
            "ansible-playbook", "delete_container.yml",
            "-e", f"container_name={container_name} veth_container={veth_container}"
        ])
        if result.returncode == 0:
            print(f"Deletion process successful for container: {container_name}")
            delete_container_entry(tenant_uuid, subnet_id, vpc_name, container_name)
        else:
            print("Failed to delete container via Ansible playbook.")
    else:
        print("No container found with the specified tenant, subnet ID, VPC name, and container name.")

def main():
    tenant_uuid = read_tenant_uuid()
    if not tenant_uuid:
        print("Tenant UUID is required to proceed.")
        return

    subnet_id = input("Enter the Subnet ID associated with the container: ")
    vpc_name = input("Enter VPC name: ")
    container_name = input("Enter the name of the container to delete: ")

    container_details = fetch_container_details(tenant_uuid, subnet_id, vpc_name, container_name)
    if container_details:
        delete_container(container_name, container_details[0], tenant_uuid, subnet_id, vpc_name)
    else:
        print("No veth details found for the specified parameters.")

if __name__ == "__main__":
    main()
