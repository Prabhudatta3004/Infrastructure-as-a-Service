import sqlite3
import subprocess
import os

def read_tenant_uuid():
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found.")
        return None

def get_vpc_details(tenant_uuid, vpc_name):
    """Retrieve VPC details from the database."""
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT vpc_id, container_name, veth1_ip, veth2_ip FROM vpcs WHERE tenant_uuid=? AND vpc_name=?", (tenant_uuid, vpc_name))
    details = c.fetchone()
    conn.close()
    return details

def delete_vpc():
    tenant_uuid = read_tenant_uuid()
    if not tenant_uuid:
        return

    vpc_name = input("Enter VPC name to delete: ")

    vpc_details = get_vpc_details(tenant_uuid, vpc_name)
    if not vpc_details:
        print("VPC not found.")
        return

    vpc_id, container_name, veth1_ip, veth2_ip = vpc_details
    playbook_path = os.path.join(os.getcwd(), "delete_vpc.yml")
    playbook_command = [
        "ansible-playbook", playbook_path,
        "-i", "localhost,",
        "-e", f"vpc_id={vpc_id} container_name={container_name} veth1_ip={veth1_ip} veth2_ip={veth2_ip}"
    ]

    result = subprocess.run(playbook_command, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"VPC '{vpc_name}' deletion executed successfully.")
        conn = sqlite3.connect('tenants.db')
        c = conn.cursor()
        c.execute("DELETE FROM vpcs WHERE vpc_id=?", (vpc_id,))
        conn.commit()
        conn.close()
    else:
        print("Failed to execute VPC deletion playbook. Error:", result.stderr)

if __name__ == "__main__":
    delete_vpc()
