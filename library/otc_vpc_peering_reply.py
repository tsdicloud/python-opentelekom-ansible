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
module: otc_vpc_peering_reply
short_description: Reply to a peering request from a different project
extends_documentation_fragment: opentelekom-ansible
version_added: "1.0"
author: "B. Rederlechner (@brederle)"
description:
   - Reply to a peering request from a different project or tenant.
options:
   name:
     description:
        - Name or id of the peering to reply to
     alias: id
     required: true
   state:
     description:
        - Accept or reject a peering request.
     choices: ['accept', 'reject']
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


def _needs_update(module, cloud, res):
    if res.cidr != module.params['cidr']:
        return True
    
    if not hasattr(res, 'enable_shared_snat') and module.params['enable_shared_snat']:
        return True
    
    if hasattr(res, 'enable_shared_snat') and (res.enable_shared_snat != module.params['enable_shared_snat']):
        return True
    
    return False



def main():
    argument_spec = openstack_full_argument_spec(
        peering=dict(type='str', required=True, aliases=['peering_id']),
        state=dict(default='accept', choices=['accept', 'reject']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    state = module.params['state']
    peering_name = module.params['peering']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( vpc_service.VpcService("vpc", aliases=['vpc1'] ))
        # need to use the artificial endpoint without project-id
        cloud.add_service( vpc_service.VpcService("peervpc") )

        v = cloud.peervpc.find_peering(peering_name, ignore_missing=False)
        if state == 'accept':
            if v.status == "PENDING_ACCEPTANCE":
                cloud.peervpc.accept_peering(v)
                if module.params['wait']:
                    v = cloud.peervpc.wait_for_status(v, "ACTIVE")
                changed = True
            elif v.status == "ACTIVE":
                changed = False
            else:
                module.fail_json(msg="Peering in wrong state " + v.status )
        elif state == 'reject':
            if v.status == "PENDING_ACCEPTANCE":
                cloud.peervpc.reject_peering(v)
                if module.params['wait']:
                    v = cloud.peervpc.wait_for_status(v, "REJECTED")
                changed = True
            elif v.status == "REJECTED":
                changed = False
            else:
                module.fail_json(msg="Peering in wrong state " + v.status )
        else:
            changed = False
        module.exit_json(changed=changed, peering=v.copy(), id=v.id )

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
