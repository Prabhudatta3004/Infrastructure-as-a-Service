import subprocess
import sqlite3
import json

def get_container_input():
    """Collects user input for container creation."""
    print("Please enter the container details:")
    container_name = input("Container Name: ")
    bridge_name = input("Bridge Name (for networking): ")
    return container_name, bridge_name

def store_container_details(container_name, bridge_name):
    """Stores container details in the database."""
    conn = sqlite3.connect('tenants.db')
    with conn:
        c = conn.cursor()
        c.execute("""
            INSERT INTO containers (container_name, bridge_name)
            VALUES (?, ?)
            """, (container_name, bridge_name))
    print("Container details stored successfully in the database.")

def create_container(container_name, bridge_name):
    """Creates a container using an Ansible playbook."""
    container_details = {
        'container_config': {
            'container_name': container_name,
            'bridge_name': bridge_name
        }
    }
    with open('container_details.json', 'w') as json_file:
        json.dump(container_details, json_file, indent=4)
    
    print("JSON content to be sent to Ansible:")
    with open('container_details.json', 'r') as json_file:
        print(json_file.read())

    result = subprocess.run(
        ["ansible-playbook", "create_container.yml", "-i", "localhost,", "-e", "@container_details.json"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if result.returncode == 0:
        print("Container created successfully.")
        return True
    else:
        print("Failed to create container:", result.stderr)
        return False

def main():
    container_name, bridge_name = get_container_input()
    
    if create_container(container_name, bridge_name):
        store_container_details(container_name, bridge_name)

if __name__ == "__main__":
    main()
