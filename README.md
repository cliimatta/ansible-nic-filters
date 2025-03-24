# ansible-nic-filters
## Motivation
The standard format of `ansible_facts` is sometimes difficult to work with when using Ansible templates, so I created a custom filter to parse the NIC information into a more useful dictionary format. 
This filter makes it easier to do things like creating iptables rules, or setting services to listen only on certain types of interfaces/IP addresses.

## Requirements
The Python module `netaddr` is required on the host you're running Ansible from.

Create a new directory in your ansible directory called `filter_plugins`, then copy `filters.py` into the directory.

## Example
1. Set a new variable either directly in your play `vars` or using `set_fact` using the `get_interfaces` filter:
```
---
- hosts: webservers
  vars:
    interfaces_1: "{{ ansible_facts | get_interfaces }}" # Example using play vars

  tasks:
    - ansible.builtin.set_fact:
        interfaces_2: "{{ ansible_facts | get_interfaces }}" # Example using set_fact
      
    - ansible.builtin.debug:
        msg: "{{ interfaces_1 }}"

    - ansible.builtin.debug:
        msg: "{{ interfaces_2 }}"
```
The filter sorts the interfaces into three interface types, `private`, `public`, and `loopback` along with the IP, NIC name, and network:
```
ok: [webserver1] => {
    "msg": {
        "loopback": [
            {
                "ip": "127.0.0.1",
                "name": "lo"
            }
        ],
        "private": [
            {
                "ip": "10.10.150.23",
                "name": "eno2np2",
                "network": "10.10.150.0/24"
            },
            {
                "ip": "10.45.10.10",
                "name": "eno2np1",
                "network": "10.45.10.0/24"
            }
        ],
        "public": [
            {
                "ip": "1.1.1.1",
                "name": "bond0"
            }
        ]
    }
}
```
NOTE: The `network` key only outputs for private interfaces.

2. Using the output in a template:
```Private Interfaces:
{% for interface in interfaces.private %}
  Interface name: {{ interface.name }}, IP: {{ interface.ip }}, Network: {{ interface.network }}
{% endfor %}

Public Interfaces:
{% for interface in interfaces.public %}
  Interface name: {{ interface.name }}, IP: {{ interface.ip }}
{% endfor %}

Loopback Interfaces:
{% for interface in interfaces.loopback %}
  Interface name: {{ interface.name }}, IP: {{ interface.ip }}
{% endfor %}
```
Output:
```
Private Interfaces:
  Interface name: eno2np1, IP: 10.45.10.10, Network: 10.45.10.0/24
  Interface name: eno2np2, IP: 10.10.150.23, Network: 10.10.150.0/24

Public Interfaces:
  Interface name: bond0, IP: 1.1.1.1

Loopback Interfaces:
  Interface name: lo, IP: 127.0.0.1
```

The filter has been tested only with the following versions:
```
ansible == 11.1.0
ansible-core == 2.18.1
netaddr == 1.3.0
Python 3.11
```

Feel free to create an issue if you face compatability problems or want a feature added.

If this filter was helpful to you, please consider buying me a coffee using the link below!

[!["Was this helpful for you? Buy Me A Coffee!"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cliimatta)
