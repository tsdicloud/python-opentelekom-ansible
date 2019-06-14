#!/bin/sh

ansible-playbook -i inventories/poc/hosts --vault-password-file ~/.ssh/.ansible_vault_pwd --skip-tags "destroy" --tags "test-rds" \
    -e "{ 'net_admin_debug': False, 'state': 'present' }" site.yml 
