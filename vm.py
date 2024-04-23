import subprocess

def read_tenant_uuid_from_file():
    """Reads the tenant UUID from a file to establish context for VM operations."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()  # Ensure we return a clean UUID without newline
    except FileNotFoundError:
        print("Tenant UUID file not found. Please log in and try again.")
        return None

def vm_menu():
    """Displays a menu for VM management for a specific tenant."""
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        print("Error: Tenant UUID not found. Please log in again.")
        return
    
    while True:
        print(f"\nVM Management for Tenant UUID: {tenant_uuid}")
        print("1. Create VM")
        print("2. Retrieve all VMs")
        print("3. Delete VM")
        print("4. Return to the main menu")
        choice = input("Select an option: ")
        
        if choice == '1':
            subprocess.run(["sudo", "python3", "create_vm.py"])
        elif choice == '2':
            subprocess.run(["sudo", "python3", "retrieve_vm.py"])
        elif choice == '3':
            subprocess.run(["sudo", "python3", "delete_vm.py"])
        elif choice == '4':
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    vm_menu()
