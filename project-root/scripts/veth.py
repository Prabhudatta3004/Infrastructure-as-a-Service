import ipaddress

def assign_veth_ips(tenant_id, base_ip_prefix='10.2.', mask='/30'):
    base_ip = f'{base_ip_prefix}{tenant_id}.0'
    
    base_network = ipaddress.ip_network(f'{base_ip}{mask}', strict=False)
    
   
    tenant_network = list(base_network.subnets(new_prefix=30))[0]
    
    
    ips = list(tenant_network.hosts())[:2]
    
    if len(ips) < 2:
        raise ValueError("Not enough IP addresses available in the subnet")
    
    return {
        'veth_ns_ip': str(ips[0]),  
        'veth_prov_ip': str(ips[1]), 
        'gateway_ip': str(ips[1]), 
        'subnet': str(tenant_network)
    }

# Test the function with multiple tenants
for tenant_id in range(1, 11):  # Testing for tenants 1 to 10
    ips = assign_veth_ips(tenant_id=tenant_id)
    print(f"Tenant {tenant_id} IP Configuration:", ips)
