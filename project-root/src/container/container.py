import subprocess

def read_tenant_uuid_from_file():
    """Reads the tenant UUID from a file to establish context for container operations."""
    try:
        with open("current_tenant_uuid.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print("Tenant UUID file not found. Please log in and try again.")
        return None

def container_menu():
    """Displays a menu for container management for a specific tenant."""
    tenant_uuid = read_tenant_uuid_from_file()
    if not tenant_uuid:
        print("Error: Tenant UUID not found. Please log in again.")
        return
    
    while True:
        print(f"\nContainer Management for Tenant UUID: {tenant_uuid}")
        print("1. Create Container")
        print("2. Retrieve all Containers")
        print("3. Delete Container")
        print("4. Return to the main menu")
        choice = input("Select an option: ")
        
        if choice == '1':
            # Assuming you have a script or command to create containers
            subprocess.run(["sudo", "python3", "create_container.py"])
        elif choice == '2':
            # Assuming you have a script or command to list containers
            subprocess.run(["sudo", "python3", "retrieve_container.py"])
        elif choice == '3':
            # Assuming you have a script or command to delete containers
            subprocess.run(["sudo", "python3", "delete_container.py"])
        elif choice == '4':
            break
        else:
            print("Invalid option, please try again.")

if __name__ == "__main__":
    container_menu()
