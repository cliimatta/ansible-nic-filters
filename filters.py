from ansible.plugins.filter.core import FilterModule
from ansible.errors import AnsibleFilterError
from netaddr import *

class FilterModule(FilterModule):
    def __init__(self):
        self.sorted_interfaces = {'private': [], 'public': [], 'loopback': []}
        self.all_vars = {}

    def filters(self):
        return {
            'get_interfaces': self.return_interfaces
        }

    def get_all_interfaces(self):
        facts_interfaces = self.all_vars.get('interfaces')
        all_interfaces = []

        for key in self.all_vars:
            if isinstance(self.all_vars.get(key), dict):
                if self.all_vars[key].get('device') in facts_interfaces:
                    interface = self.all_vars.get(key)
                    all_interfaces.append(interface)

        if len(all_interfaces) > 0:
            return all_interfaces
        else:
            raise ValueError("No interfaces found")    

    def get_interface_details(self, interface):
        iface_name = interface.get('device')

        # Ignore interfaces that are "active" but don't have an IP (bond members)
        if not interface.get("ipv4"):
            return

        # Build the IP object so we can figure out if it's public or private
        raw_ip = interface['ipv4'].get('address')
        ip = IPAddress(raw_ip)

        # Determine the local network
        raw_network = interface['ipv4'].get('network')
        raw_cidr = interface['ipv4'].get('prefix')
        network = str(raw_network + "/" + raw_cidr)

        # Ignore inactive devices
        if not interface.get('active'):
            return

        if ip.is_loopback():
            device_dict = {'name': iface_name, 'ip': raw_ip}
            self.sorted_interfaces['loopback'].append(device_dict)
            return

        if ip.is_ipv4_private_use():
            device_dict = {'name': iface_name, 'network': network, 'ip': raw_ip}
            self.sorted_interfaces['private'].append(device_dict)
            return

        if ip.is_global():
            device_dict = {'name': iface_name, 'ip': raw_ip}
            self.sorted_interfaces['public'].append(device_dict)
            return

        return

    def return_interfaces(self, value):
        self.all_vars = value

        try:
            interfaces = self.get_all_interfaces()
        except Exception as e:
            raise AnsibleFilterError("Failed to get interfaces: {}".format(e))

        try:
            for interface in interfaces:
                self.get_interface_details(interface)
        except Exception as e:
            raise AnsibleFilterError("Failed to get interface details {}".format(e))

        return self.sorted_interfaces
