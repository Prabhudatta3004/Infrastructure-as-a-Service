import subprocess
import sqlite3

def read_tenant_uuid_from_file():
    """Reads the tenant UUID from a file to establish context."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()  # Ensure we return a clean UUID without newline
    except FileNotFoundError:
        print("Tenant UUID file not found. Please log in and try again.")
        return None

def check_vm_exists(tenant_uuid, vm_name):
    """ Check if the VM exists for the given tenant in the database. """
    conn = sqlite3.connect('tenants.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vms WHERE vm_name=? AND tenant_uuid=?", (vm_name, tenant_uuid))
    vm = cursor.fetchone()
    conn.close()
    return vm is not None

def delete_vm_from_db(tenant_uuid, vm_name):
    """ Delete VM entry from the database for a specific tenant. """
    conn = sqlite3.connect('tenants.db')
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vms WHERE vm_name=? AND tenant_uuid=?", (vm_name, tenant_uuid))

def run_playbook(vm_name):
    """ Run the Ansible playbook to delete the VM. """
    try:
        result = subprocess.run(
            ["ansible-playbook", "delete_vm.yml", "-e", f"vm_name={vm_name}"],
            capture_output=True, text=True, check=True
        )
        print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("Failed to delete VM:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        print("Tenant UUID is required to proceed.")
        return

    vm_name = input("Enter the name of the VM to delete: ")
    if check_vm_exists(tenant_uuid, vm_name):
        if run_playbook(vm_name):
            delete_vm_from_db(tenant_uuid, vm_name)
            print("VM deleted successfully.")
        else:
            print("Failed to delete VM.")
    else:
        print("VM not found in the database for the specified tenant.")

if __name__ == "__main__":
    main()
