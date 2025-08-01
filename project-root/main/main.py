import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import uuid
import bcrypt
import subprocess
import os
from datetime import datetime

def get_current_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def generate_uuid():
    return str(uuid.uuid4())

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def write_tenant_uuid_to_file(tenant_uuid):
    with open("current_tenant_uuid.txt", "w") as file:
        file.write(tenant_uuid)

def delete_tenant_uuid_file():
    if os.path.exists("current_tenant_uuid.txt"):
        os.remove("current_tenant_uuid.txt")

def send_email(recipient_email, tenant_uuid):
    sender_email = "prabhudatta.mishra.official@gmail.com"  
    sender_password = "frrq fgml zlou jxqn"  
    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to Our Linux Cloud Platform"
    message["From"] = sender_email
    message["To"] = recipient_email

    text = f"""Hi,
    Welcome to our Linux cloud platform. Your tenant UUID is: {tenant_uuid}.
    Please keep it safe as it will be used to manage your resources."""
    part1 = MIMEText(text, "plain")
    message.attach(part1)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def register_tenant():
    tenant_name = input("Enter tenant name: ")
    email = input("Enter email address: ")
    password = input("Enter password: ")
    tenant_uuid = generate_uuid()
    hashed_password = hash_password(password)
    current_timestamp = get_current_timestamp()
    
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO tenants (uuid, tenant_name, email, password, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (tenant_uuid, tenant_name, email, hashed_password, current_timestamp, current_timestamp))
        conn.commit()
        send_email(email, tenant_uuid)
        print("Tenant registered successfully.")
        write_tenant_uuid_to_file(tenant_uuid)
    except sqlite3.IntegrityError:
        print("A tenant with this email already exists.")
    finally:
        conn.close()

def verify_login(email, password):
    conn = sqlite3.connect('tenants.db')
    c = conn.cursor()
    c.execute("SELECT uuid, password FROM tenants WHERE email=?", (email,))
    record = c.fetchone()
    conn.close()

    if record and bcrypt.checkpw(password.encode(), record[1].encode()):
        write_tenant_uuid_to_file(record[0])
        return True
    return False

def login_tenant():
    email = input("Enter your email address: ")
    password = input("Enter your password: ")
    if verify_login(email, password):
        print("Login successful.")
        after_login_menu(email)
    else:
        print("Login unsuccessful. Please check your credentials.")

def after_login_menu(tenant_name):
    while True:
        print(f"\nWelcome, {tenant_name}. What would you like to manage?")
        print("1. VPCs")
        print("2. Subnets")
        print("3. VMs")
        print("4. Containers")
        print("5. Logout")
        choice = input("Select an option: ")
        if choice == '1':
            subprocess.run(["python3", "vpc.py"])
        elif choice == '2':
            subprocess.run(["python3", "subnet.py"])
        elif choice == '3':
            subprocess.run(["python3", "vm.py"])
        elif choice == '4':
            subprocess.run(["python3", "container.py"]) 
        elif choice == '5':
            delete_tenant_uuid_file()
            print("You have been logged out.")
            break
        else:
            print("Invalid option, please try again.")

def main_menu():
    while True:
        print("\nWelcome to the Cloud Platform")
        print("1. Register as a new tenant")
        print("2. Log in")
        print("3. Exit")
        choice = input("Select an option: ")
        if choice == '1':
            register_tenant()
        elif choice == '2':
            login_tenant()
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()
