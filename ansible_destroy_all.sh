#!/bin/sh

ansible-playbook -i inventories/poc/hosts --vault-password-file ~/.ssh/.ansible_vault_pwd --skip-tags "apply" \
    -e "{ 'net_admin_debug': False, 'state': 'absent' }" site.yml 
