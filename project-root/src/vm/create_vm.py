import subprocess
import sqlite3
import json

def read_tenant_uuid_from_file():
    """Reads the tenant UUID from a file to establish context for VM operations."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()  # Ensure we return a clean UUID without newline
    except FileNotFoundError:
        print("Tenant UUID file not found. Please log in and try again.")
        return None

def get_vm_input():
    """Collects user input for VM creation."""
    print("Please enter the VM details:")
    subnet_id = input("Subnet ID: ")
    vm_name = input("VM Name: ")
    vm_memory = input("Memory (in MB, e.g., 2048): ")
    vm_vcpus = input("Number of vCPUs: ")
    return subnet_id, vm_name, vm_memory, vm_vcpus

def get_bridge_name(subnet_id):
    """Fetches the bridge name from the database based on the subnet ID."""
    conn = sqlite3.connect('tenants.db')
    try:
        c = conn.cursor()
        c.execute("SELECT ovs_bridge_name FROM subnets WHERE subnet_id=?", (subnet_id,))
        result = c.fetchone()
        return result[0] if result else None
    finally:
        conn.close()

def store_vm_details(tenant_uuid, subnet_id, vm_name, vm_memory, vm_vcpus, bridge_name):
    """Stores VM details in the database."""
    conn = sqlite3.connect('tenants.db')
    with conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO vms (tenant_uuid, subnet_id, vm_name, vm_memory, vm_vcpus, bridge_name)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (tenant_uuid, subnet_id, vm_name, vm_memory, vm_vcpus, bridge_name))
    print("VM details stored successfully in the database.")

def create_vm(vm_name, vm_memory, vm_vcpus, bridge_name):
    """Creates a VM using an Ansible playbook with improved runner output."""
    vm_details = {
        'base_config': {
            'root_password': 'rootpasswd',
            'ubuntu_password': 'ubuntupasswd',
            'base_image_path': "/var/lib/libvirt/images/jammy-server-cloudimg-amd64.img",
            'vm_disk_size': "12G",
            'vm_memory': vm_memory,
            'vm_vcpus': vm_vcpus
        },
        'topology': {
            'vms': [{
                'name': vm_name,
                'networks': [{
                    'bridge': bridge_name
                }]
            }]
        }
    }
    with open('vm_details.json', 'w') as json_file:
        json.dump(vm_details, json_file, indent=4)
    
    print("JSON content to be sent to Ansible:")
    with open('vm_details.json', 'r') as json_file:
        print(json_file.read())

    try:
        result = subprocess.run(
            ["ansible-playbook", "create_vm.yml", "-i", "localhost,", "-e", "@vm_details.json"],
            capture_output=True, text=True, check=True
        )
        print("STDOUT:", result.stdout)
        print("VM created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to create VM:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        return  # UUID must be present to proceed
    
    subnet_id, vm_name, vm_memory, vm_vcpus = get_vm_input()
    bridge_name = get_bridge_name(subnet_id)
    if not bridge_name:
        print("Error: No bridge found for the given subnet ID.")
        return

    if create_vm(vm_name, vm_memory, vm_vcpus, bridge_name):
        store_vm_details(tenant_uuid, subnet_id, vm_name, vm_memory, vm_vcpus, bridge_name)

if __name__ == "__main__":
    main()
