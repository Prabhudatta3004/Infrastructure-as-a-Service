# Infrastructure as a Service (IaaS) Project

## Overview
This project provides a scalable, modular Infrastructure as a Service (IaaS) system designed to manage and provision virtualized resources such as virtual machines (VMs), virtual private clouds (VPCs), subnets, and containers. The project is structured to offer seamless northbound and southbound communication, providing efficient and modularized resource management capabilities.

## Project Structure
The project is organized as follows:

```
project-root/
  ├── config/
  │   ├── dnsmasq_conf                 # Configuration file for DNS/DHCP service
  │   └── topology.yml                 # Network topology configuration
  ├── data/
  │   └── last_assigned_subnet.txt     # Tracks the last assigned subnet ID
  ├── main/
  │   └── main.py                      # Main entry point for the application
  ├── scripts/
  │   ├── create_DB.py                 # Script to initialize the database
  │   └── veth.py                      # Utility script for virtual Ethernet (veth) management
  ├── src/
  │   ├── container/
  │   │   ├── container.py             # Core logic for container management
  │   │   ├── container2ns.sh          # Script to map containers to network namespaces
  │   │   ├── create_container.py      # Create container functionality
  │   │   ├── create_container.yml     # Ansible playbook for container creation
  │   │   ├── delete_container.py      # Delete container functionality
  │   │   ├── delete_container.yml     # Ansible playbook for container deletion
  │   │   └── retrieve_container.py    # Retrieve container details
  │   ├── vpc/
  │   │   ├── create_vpc.py            # Create VPC functionality
  │   │   ├── create_vpc.yml           # Ansible playbook for VPC creation
  │   │   ├── delete_vpc.py            # Delete VPC functionality
  │   │   ├── delete_vpc.yml           # Ansible playbook for VPC deletion
  │   │   ├── retrieve_vpc.py          # Retrieve VPC details
  │   │   ├── vpc.py                   # Core logic for VPC management
  │   │   └── vpc_details.json         # JSON file storing VPC details
  │   ├── vm/
  │   │   ├── create_vm.py             # Create VM functionality
  │   │   ├── create_vm.yml            # Ansible playbook for VM creation
  │   │   ├── delete_vm.py             # Delete VM functionality
  │   │   ├── delete_vm.yml            # Ansible playbook for VM deletion
  │   │   ├── retrieve_vm.py           # Retrieve VM details
  │   │   ├── vm.py                    # Core logic for VM management
  │   │   └── vm_details.json          # JSON file storing VM details
  │   ├── subnet/
  │   │   ├── create_subnet.py         # Create subnet functionality
  │   │   ├── create_subnet.yml        # Ansible playbook for subnet creation
  │   │   ├── delete_subnet.py         # Delete subnet functionality
  │   │   ├── delete_subnet.yml        # Ansible playbook for subnet deletion
  │   │   ├── retrieve_subnet.py       # Retrieve subnet details
  │   │   └── subnet.py                # Core logic for subnet management
  │   └── tenant/
  │       ├── current_tenant_uuid.txt  # Tracks current tenant UUID
  │       ├── tenant_delete.py         # Tenant deletion functionality
  │       ├── tenant_retrieve.py       # Retrieve tenant details
  │       └── tenants.db               # Database storing tenant information
```

## Features
- **Container Management**: Create, retrieve, delete, and manage containers.
- **VPC Management**: Provision and manage Virtual Private Clouds with support for creation, retrieval, and deletion.
- **VM Management**: Manage Virtual Machines, including creation, retrieval, and deletion capabilities.
- **Subnet Management**: Provision subnets and handle related operations.
- **Tenant Management**: Support for multi-tenancy with operations for tenant creation, deletion, and retrieval.

## Prerequisites
- Python 3.8 or later
- Ansible
- Virtualization software (e.g., Docker)
- `pip` for Python package management

## Installation
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd project-root
   ```
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Setup database (if applicable)**:
   ```bash
   python scripts/create_DB.py
   ```

## Usage
### Running the Main Application
```bash
python main/main.py
```

### Creating a VPC
```bash
python src/vpc/create_vpc.py --name <vpc-name> --cidr <CIDR-block>
```

### Creating a VM
```bash
python src/vm/create_vm.py --name <vm-name> --vpc <vpc-id>
```

### Additional Commands
Refer to each module's documentation for more detailed usage instructions.

## Configuration
Configuration files are located in the `config/` directory:
- `dnsmasq_conf`: For configuring DNS/DHCP services.
- `topology.yml`: Define network topology configurations.

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## License
This project is licensed under the [MIT License](LICENSE).

---

This README provides a high-level overview, installation instructions, examples of how to use your IaaS project, and guidance on contributing. You can further tailor it to match specific requirements or features in your project.
