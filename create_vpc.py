import sqlite3
import uuid
import json
import subprocess
from datetime import datetime
import ipaddress
import hashlib
import os

def get_current_timestamp():
    """Returns the current timestamp in a formatted string."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def read_tenant_uuid():
    """Reads the tenant UUID from a file, returning None if the file doesn't exist."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Error: Tenant UUID file not found.")
        return None

def vpc_exists(tenant_uuid, vpc_name):
    """Checks if a VPC already exists in the database."""
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT * FROM vpcs WHERE tenant_uuid=? AND vpc_name=?", (tenant_uuid, vpc_name))
    result = c.fetchone()
    conn.close()
    return result is not None

def generate_compact_name(name):
    """Generates a compact name for container and namespace."""
    return hashlib.sha1(name.encode()).hexdigest()[:6]

def get_last_assigned_subnet():
    """Retrieves the last used /30 subnet and calculates the next available one."""
    try:
        with open("last_assigned_subnet.txt", "r") as file:
            last_subnet = ipaddress.ip_network(file.read().strip(), strict=False)
    except FileNotFoundError:
        last_subnet = ipaddress.ip_network('10.2.1.0/30', strict=False)  # Start from here if no file exists
    return last_subnet

def calculate_next_subnet(last_subnet):
    """Calculates the next /30 subnet by incrementing the third octet."""
    next_subnet = ipaddress.ip_network(f"{last_subnet.network_address + 256}/30", strict=False)
    return next_subnet

def update_last_assigned_subnet(next_subnet):
    """Updates the last assigned subnet in the file."""
    with open("last_assigned_subnet.txt", "w") as file:
        file.write(str(next_subnet))

def assign_veth_ips():
    """Assigns IPs for veth pairs from a reserved pool."""
    last_subnet = get_last_assigned_subnet()
    next_subnet = calculate_next_subnet(last_subnet)
    update_last_assigned_subnet(next_subnet)
    return str(next_subnet[1]) + "/30", str(next_subnet[2]) + "/30"

def generate_compact_veth_name(unique_string):
    """Generates a compact name for the veth pair using a hash of a unique string."""
    hash_part = hashlib.sha256(unique_string.encode()).hexdigest()[:4]
    return f"v{hash_part}"

def create_vpc():
    tenant_uuid = read_tenant_uuid()
    if not tenant_uuid:
        return

    vpc_name = input("Enter VPC name: ")
    zone = input("Enter Zone: ")

    if vpc_exists(tenant_uuid, vpc_name):
        print("A VPC with the given name already exists for this tenant.")
        return

    vpc_id = str(uuid.uuid4())
    created_at = get_current_timestamp()
    container_name = generate_compact_name(tenant_uuid + vpc_name)
    namespace_name = container_name  # Same as container name
    veth1_ip, veth2_ip = assign_veth_ips()
    gateway_ip = veth2_ip.split('/')[0]
    network = ipaddress.ip_network(veth1_ip.split('/')[0] + '/30', strict=False)
    nat_subnet = str(network.network_address) + '/30'
    veth_ns = generate_compact_veth_name(tenant_uuid + vpc_name + "ns")
    veth_prov = generate_compact_veth_name(tenant_uuid + vpc_name + "prov")
    

    vpc_details = {
        'vpc_id': vpc_id,
        'tenant_uuid': tenant_uuid,
        'vpc_name': vpc_name,
        'zone': zone,
        'container_name': container_name,
        'veth_ns': veth_ns,
        'veth_prov': veth_prov,
        'veth_ns_ip': veth1_ip,
        'veth_prov_ip': veth2_ip,
        'gateway_ip': gateway_ip,
        'nat_subnet': nat_subnet 
    }

    print("Generated JSON data:")
    print(json.dumps(vpc_details, indent=4))

    temp_file_path = "vpc_details.json"
    with open(temp_file_path, 'w') as temp_file:
        json.dump(vpc_details, temp_file)

    playbook_path = os.path.join(os.getcwd(), "create_vpc.yml")
    playbook_command = ["ansible-playbook", playbook_path, "-i", "localhost,", "-e", f"@{temp_file_path}"]
    result = subprocess.run(playbook_command, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"VPC '{vpc_name}' creation playbook executed successfully.")
        conn = sqlite3.connect('tenants.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO vpcs (vpc_id, tenant_uuid, vpc_name, zone, container_name, namespace, veth1_ip, veth2_ip, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (vpc_id, tenant_uuid, vpc_name, zone, container_name, namespace_name, veth1_ip, veth2_ip, created_at))
        conn.commit()
        conn.close()
        print(f"VPC '{vpc_name}' created successfully with ID {vpc_id}.")
        print(f"Veth pair IPs assigned: {veth1_ip}, {veth2_ip}")
    else:
        print("Failed to execute VPC creation playbook. Error:", result.stderr)

    os.remove(temp_file_path)

if __name__ == "__main__":
    create_vpc()
