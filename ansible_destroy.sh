#!/bin/sh

ansible-playbook -vvv -i inventories/test/hosts --vault-password-file ~/.ssh/.ansible_vault_pwd --skip-tags "apply"\
  --tags "test-peering" \
  -e "{ 'net_admin_debug': False, 'state': 'absent' }" site.yml 
