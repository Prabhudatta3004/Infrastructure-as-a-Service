import sqlite3
import json
import ipaddress
import hashlib
import subprocess
import time
import random

def read_tenant_uuid():
    """Reads the tenant UUID from a file. Adds more robust file handling."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            tenant_uuid = file.read().strip()
            if tenant_uuid:
                return tenant_uuid
            else:
                raise ValueError("Tenant UUID is empty.")
    except FileNotFoundError:
        print("Error: Tenant UUID file not found.")
        return None
    except ValueError as ve:
        print(ve)
        return None

def generate_unique_name(base, unique_string):
    hash_part = hashlib.sha256(unique_string.encode()).hexdigest()[:2]
    timestamp = int(time.time())
    return f"{base[:2]}{hash_part}{timestamp}"

def generate_subnet_id(vpc_name, cidr_block):
    timestamp = int(time.time())
    random_part = hashlib.sha256(str(random.random()).encode()).hexdigest()[:4]
    unique_string = f"{vpc_name}_{cidr_block}_{timestamp}_{random_part}"
    hash_part = hashlib.sha256(unique_string.encode()).hexdigest()[:8]
    return f"subnet_{hash_part}"

def get_container_and_namespace_names(vpc_name):
    conn = sqlite3.connect('tenants.db')
    try:
        c = conn.cursor()
        c.execute("SELECT container_name, namespace, tenant_uuid FROM vpcs WHERE vpc_name=?", (vpc_name,))
        result = c.fetchone()
        return result if result else (None, None, None)
    finally:
        conn.close()

def check_existing_subnet(cidr_block, vpc_name, tenant_uuid):
    conn = sqlite3.connect('tenants.db')
    try:
        c = conn.cursor()
        # Query also includes tenant_uuid to ensure uniqueness within a tenant's VPC
        c.execute("SELECT COUNT(*) FROM subnets WHERE subnet_used=? AND vpc_name=? AND tenant_uuid=?", (cidr_block, vpc_name, tenant_uuid))
        return c.fetchone()[0] > 0
    finally:
        conn.close()

def subnet_details(cidr_block):
    network = ipaddress.ip_network(cidr_block)
    gateway = str(network.network_address + 1)
    dhcp_start = str(network.network_address + 50)
    dhcp_end = str(network.network_address + 150)
    return gateway, dhcp_start, dhcp_end

def main():
    tenant_uuid = read_tenant_uuid()
    if not tenant_uuid:
        print("Tenant UUID is required to proceed.")
        return

    vpc_name = input("Enter VPC name: ")
    cidr_block = input("Enter the CIDR block (e.g., 192.168.6.0/24): ")

    if check_existing_subnet(cidr_block, vpc_name, tenant_uuid):
        print("Error: This subnet with the specified CIDR block already exists for this tenant in the specified VPC.")
        return

    container_name, namespace_name, _ = get_container_and_namespace_names(vpc_name)
    if not container_name or not namespace_name:
        print("Error: Container or Namespace not found for the provided VPC name.")
        return

    linux_bridge_name = generate_unique_name("li", container_name)
    ovs_bridge_name = generate_unique_name("ovs", container_name)
    subnet_gateway, dhcp_range_start, dhcp_range_end = subnet_details(cidr_block)
    subnet_id = generate_subnet_id(vpc_name, cidr_block)
    veth_host = generate_unique_name("v1", container_name)
    veth_ns = generate_unique_name("v2", container_name)

    vpc_details = {
        'net_namespace': namespace_name,
        'linux_bridge_name': linux_bridge_name,
        'bridge_name': ovs_bridge_name,
        'subnet_id': subnet_id,
        'subnet_block': cidr_block,
        'subnet_gateway': subnet_gateway,
        'dhcp_range_start': dhcp_range_start,
        'dhcp_range_end': dhcp_range_end,
        'dhcp_subnet_mask': "255.255.255.0",
        'dhcp_lease_time': "12h",
        'veth_host': veth_host,
        'veth_ns': veth_ns
    }

    json_content = json.dumps(vpc_details, indent=4)
    print("JSON content to be sent to Ansible:")
    print(json_content)

    with open('vpc_details.json', 'w') as json_file:
        json_file.write(json_content)

    process = subprocess.Popen(
        ["ansible-playbook", "create_subnet.yml", "-i", "localhost,", "-e", f"@vpc_details.json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print("Playbook executed successfully, updating database.")
        conn = sqlite3.connect('tenants.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO subnets (subnet_id, veth_pair_names, linux_bridge_name, ovs_bridge_name, subnet_used, vpc_name, tenant_uuid)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (subnet_id, veth_host + ',' + veth_ns, linux_bridge_name, ovs_bridge_name, cidr_block, vpc_name, tenant_uuid))
        conn.commit()
        conn.close()
    else:
        print("Failed to execute playbook:", stderr.decode())

if __name__ == "__main__":
    main()
