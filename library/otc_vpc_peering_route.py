#!/usr/bin/python

# Copyright (c) 2020, T-Systems International
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'T-Systems'}

DOCUMENTATION = '''
---
module: otc_vpc_peering_route
short_description: Add/remove routes to other, peered VPC
extends_documentation_fragment: opentelekom-ansible
version_added: "1.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add/remove routes to other, peered VPC.
options:
   peering:
     description:
        - Name or id of the peering
     alias: peering_id, nexthop
     required: true
   destination:
     description:
        - CIDR block of the ips in the destination vpc
     required: true
   vpc:
     description:
        - optional name or id of the vpc to peer from (admin only) 
     alias: vpc_id
     required: false
   state:
     description:
        - Create or remove a route.
     choices: ['present', 'absent']
     default: present
     version_added: "2.8"
requirements:
     - "openstacksdk"
     - "python-opentelekom-sdk"
'''

EXAMPLES = '''
'''

RETURN = '''
peering:
    description: Dictionary describing the vpc peering.
    type: complex
    contains:
        id:
            description: VPC peering id.
            type: str
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: VPC peering name.
            type: str
            sample: "own-name-vpc"
        status:
            description: vpc peering status.
            type: str
            sample: "ACTIVE"
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module

from opentelekom.connection import connect_from_ansible 
from opentelekom.vpc import vpc_service
from openstack import exceptions 


def main():
    argument_spec = openstack_full_argument_spec(
        peering=dict(type='str', required=True, aliases=['peering_id', "nexthop"]),
        state=dict(default='accept', choices=['present', 'absent']),
        destination=dict(type='str', required=True),
        vpc=dict(type='str', required=True, aliases=['vpc_id']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    state = module.params['state']
    peering_name = module.params['peering']
    vpc_name = module.params['vpc']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( vpc_service.VpcService("vpc", aliases=['vpc1'] ))
        # need to use the artificial endpoint without project-id
        cloud.add_service( vpc_service.VpcService("peervpc") )

        peering = cloud.peervpc.find_peering(peering_name, ignore_missing=False)
        vpc = cloud.vpc.find_vpc(vpc_name, ignore_missing=False)

        routes = cloud.peervpc.routes(nexthop=peering.id,
            destination=module.params['destination'],
            vpc_id=vpc.id
        )

        if state == 'present':
            try:
                route = next(routes)
                changed = False
            except StopIteration:
                route = cloud.peervpc.create_route(nexthop=peering.id,
                    destination=module.params['destination'],
                    vpc_id=vpc.id)
                changed = True
            module.exit_json(changed=changed, route=route.copy(), id=route.id )

        elif state == 'absent':
            try:
                cloud.peervpc.delete_route(next(routes).id)
                module.exit_json(changed=True)
            except StopIteration:
                module.exit_json(changed=False)



    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
