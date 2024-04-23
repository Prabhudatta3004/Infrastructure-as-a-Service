import sqlite3
import subprocess

def check_subnet_exists(subnet_id):
    """Check if the subnet exists in the database."""
    conn = sqlite3.connect('tenants.db')
    try:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM subnets WHERE subnet_id=?", (subnet_id,))
        return c.fetchone()[0] > 0
    finally:
        conn.close()

def delete_subnet(subnet_id):
    """Delete the subnet details from the database."""
    conn = sqlite3.connect('tenants.db')
    try:
        c = conn.cursor()
        c.execute("DELETE FROM subnets WHERE subnet_id=?", (subnet_id,))
        conn.commit()
    finally:
        conn.close()

def main():
    subnet_id = input("Enter the subnet ID to delete: ")
    if check_subnet_exists(subnet_id):
        # Proceed with deletion
        delete_subnet(subnet_id)
        # Run the Ansible playbook to delete network components
        process = subprocess.Popen(
            ["ansible-playbook", "delete_subnet.yml", "-i", "localhost,", "-e", f"subnet_id={subnet_id}"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        if process.returncode == 0:
            print("Subnet deletion executed successfully.")
        else:
            print("Failed to execute subnet deletion:", stderr.decode())
    else:
        print("Error: Subnet ID does not exist.")

if __name__ == "__main__":
    main()
