#!/bin/sh

ansible-playbook -vvvvvvvvvvvvvvv -i inventories/poc/hosts --vault-password-file ~/.ssh/.ansible_vault_pwd -e "{ 'net_admin_debug': False, 'net_admin_state': 'present' }" site.yml 
