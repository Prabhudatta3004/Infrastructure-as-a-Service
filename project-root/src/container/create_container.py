import sqlite3
import subprocess
import json
import hashlib
import time
import random

def read_tenant_uuid():
    """Reads the tenant UUID from a file."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Tenant UUID file not found.")
        return None

def generate_unique_name(base, unique_string):
    """Generates a unique name using a base name and a unique string."""
    hash_part = hashlib.sha256(unique_string.encode()).hexdigest()[:4]
    timestamp = int(time.time())
    return f"{base}{hash_part}"

def get_ovs_bridge_name(subnet_id):
    """Fetches the OVS bridge name for a given subnet from the database."""
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()
    cursor.execute("SELECT ovs_bridge_name FROM subnets WHERE subnet_id=?", (subnet_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def store_container_info(tenant_uuid, vpc_name, subnet_id, container_name, veth_host, veth_container, ovs_bridge_name):
    """Stores container information in the database."""
    conn = sqlite3.connect('tenants.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO containers (tenant_uuid, vpc_name, subnet_id, container_name, veth_host, veth_container, ovs_bridge_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tenant_uuid, vpc_name, subnet_id, container_name, veth_host, veth_container, ovs_bridge_name))

def main():
    tenant_uuid = read_tenant_uuid()
    if not tenant_uuid:
        print("Tenant UUID is required to proceed.")
        return

    vpc_name = input("Enter VPC name: ")
    subnet_id = input("Enter Subnet ID: ")
    container_name = input("Enter Container Name: ")
    ovs_bridge_name = get_ovs_bridge_name(subnet_id)

    if not ovs_bridge_name:
        print("OVS Bridge not found for the specified subnet.")
        return

    veth_host = generate_unique_name("vh", container_name)
    veth_container = generate_unique_name("vc", container_name)

    # Running the playbook
    subprocess.run([
        "ansible-playbook", "create_container.yml",
        "-e", json.dumps({
            "container_name": container_name, 
            "ovs_bridge_name": ovs_bridge_name, 
            "veth_host": veth_host, 
            "veth_container": veth_container
        })
    ])

    # Store in DB
    store_container_info(tenant_uuid, vpc_name, subnet_id, container_name, veth_host, veth_container, ovs_bridge_name)
    print("Container created and data stored successfully.")

if __name__ == "__main__":
    main()
