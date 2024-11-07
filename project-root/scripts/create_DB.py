import sqlite3

def initialize_db():
    # Create a new database connection
    conn = sqlite3.connect('tenants.db')  # This creates a new database file called 'new_tenants.db'
    c = conn.cursor()

    # Create tables within the database
    c.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            uuid TEXT PRIMARY KEY,
            tenant_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS vpcs (
        vpc_id TEXT PRIMARY KEY,
        tenant_uuid TEXT,
        vpc_name TEXT,
        zone TEXT,
        container_name TEXT,
        namespace TEXT,
        veth1_ip TEXT,
        veth2_ip TEXT,
        created_at TEXT,
        FOREIGN KEY(tenant_uuid) REFERENCES tenants(uuid) ON DELETE CASCADE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS subnets (
            subnet_id TEXT PRIMARY KEY,
            tenant_uuid TEXT,
            vpc_name TEXT,
            veth_pair_names TEXT,
            linux_bridge_name TEXT,
            ovs_bridge_name TEXT,
            subnet_used TEXT,
            FOREIGN KEY(tenant_uuid) REFERENCES tenants(uuid) ON DELETE CASCADE,
            FOREIGN KEY(vpc_name) REFERENCES vpcs(vpc_name) ON DELETE CASCADE
        )
    ''')
    print("Subnets table created successfully with foreign key constraints.")


    # Commit changes and close the database connection
    conn.commit()
    conn.close()

    print("Database initialized successfully.")

if __name__ == "__main__":
    initialize_db()
