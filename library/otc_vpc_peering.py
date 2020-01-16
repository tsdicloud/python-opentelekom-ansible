#!/usr/bin/python

# Copyright (c) 2019, T-Systems International
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'T-Systems'}

DOCUMENTATION = '''
---
module: otc_vpc_peering
short_description: Creates/removes a VPC peering from Open Telekom Cloud
extends_documentation_fragment: opentelekom-ansible
version_added: "1.0"
author: "B. Rederlechner (@brederle)"
description:
   - Add, modify or remove VPC peering connection from OpenTelekomCloud project.
options:
   name:
     description:
        - Name of the VPV peering connection
     required: true
   vpc:
     description:
        - name or id of the vpc to peer in the current project
     required: true
     alias: "vpc_id"
   peervpc:
     description:
        - name or id of the foreign vpc to peer with
     required: true
     alias: "peervpc_id"
   peerproject:
     description:
        - name or id if the foreign vpc is loated in another project or tenant
     required: false
     alias: "peerproject_id"
   state:
     description:
        - Indicate desired state of the resource.
     choices: ['present', 'absent']
     default: present
     version_added: "2.7"
requirements:
     - "openstacksdk"
     - "python-opentelekom-sdk"
'''

EXAMPLES = '''
'''

RETURN = '''
peering:
    description: Dictionary describing the VPC peering.
    returned: On success when I(state) is 'present'.
    type: complex
    contains:
        id:
            description: VPC peering id.
            type: str
            sample: "4bb4f9a5-3bd2-4562-bf6a-d17a6341bb56"
        name:
            description: VPC peering id/name.
            type: str
            sample: "own-name-vpc"
        status:
            description: VPC status.
            type: str
            sample: "OK"
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import openstack_full_argument_spec, openstack_module_kwargs, openstack_cloud_from_module

from opentelekom.connection import connect_from_ansible 
from opentelekom.vpc import vpc_service
from opentelekom.vpc.v2.peering import Peering, VpcInfoSpec
from opentelekom.vpc.v1.vpc import Vpc
from openstack import exceptions 


def _needs_update(module, cloud, res):
    if res.name != module.params['name']:
        return True

    if not res.description and module.params['description']:
        return True  
    if res.description and (res.description != module.params['description']):
        return True
    
    return False



def main():
    argument_spec = openstack_full_argument_spec(
        name=dict(type='str', required=True),
        vpc=dict(type='str', aliases=['vpc_id']),
        peervpc=dict(type='str', aliases=['peervpc_id']),
        peerproject_id=dict(type='str'),
        description=dict(type='str'),
        state=dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    state = module.params['state']
    name = module.params['name']
    description = module.params['description']

    cloud = connect_from_ansible(module)
    try:
        cloud.add_service( vpc_service.VpcService("vpc", aliases=['vpc1'] ))
        # need to use the artificial endpoint without project-id
        cloud.add_service( vpc_service.VpcService("peervpc"))



        peering = cloud.peervpc.find_peering(name)
        
        if state == 'present':
            if not peering:
                vpc = cloud.vpc.find_vpc(module.params['vpc'], ignore_missing=False)
                peerproject_id = module.params['peerproject_id']

                if not peerproject_id:
                    peervpc = cloud.vpc.find_vpc(module.params['peervpc'], ignore_missing=False)
                else:
                    # FIXME: remote peerings work only with ids at the moment
                    # so we build an empty resource to use the same followup code
                    peervpc = Vpc(id=module.params['peervpc'])

                new_peer = Peering(name=name,
                    request_vpc_info = VpcInfoSpec(
                        vpc_id=vpc.id,
                    ),
                    accept_vpc_info = VpcInfoSpec(
                        vpc_id=peervpc.id,
                    )
                )
                if peerproject_id:
                    new_peer.accept_vpc_info.tenant_id = peerproject_id 
                if description:
                    new_peer.description = description

                peering = cloud.peervpc.create_peering(**new_peer.to_dict(ignore_none=True))
                changed = True
            elif _needs_update(module, cloud, peering):
                if description:
                    peering.description=description
                peering = cloud.peervpc.update_peering(**peering.to_dict(ignore_none=True))
                changed = True
            else:
                changed = False
            module.exit_json(changed=changed, vpc=peering.copy(), id=peering.id )

        elif state == 'absent':
            if not peering:
                module.exit_json(changed=False)
            else:
                cloud.peervpc.delete_peering(peering)
                module.exit_json(changed=True)

    except exceptions.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


if __name__ == "__main__":
    main()
