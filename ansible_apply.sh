#!/bin/sh

ansible-playbook -vvvv -i inventories/test/hosts --vault-password-file ~/.ssh/.ansible_vault_pwd --skip-tags "destroy"\
  --tags "test-peering" \
  -e "{ 'net_admin_debug': False, 'state': 'present' }" site.yml 
