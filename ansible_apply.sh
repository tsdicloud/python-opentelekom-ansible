#!/bin/sh

ansible-playbook -i inventories/poc/hosts --vault-password-file ~/.ssh/.ansible_vault_pwd -e "{ 'net_admin_debug': False, 'state': 'present' }" --tags "test-vpc" site.yml 
