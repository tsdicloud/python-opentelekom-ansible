#!/bin/bash

# please install openstack-client first


# add Fedora epel repository
sudo yum -y install epel-release
#rpm -Uvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm

# patch CentOS to most frequent level
sudo yum -y update --skip-broken

# enable auto secuirty updating
sudo yum -y install yum-cron
sudo systemctl start yum-cron
sudo systemctl enable yum-cron

# TODO: Configure /etc/yum/yum-cron.conf
# update_cmd = security
# update_messages = yes
# download_updates = yes
# apply_updates = yes


# prepare to build a current version of ansible (>= 2.0) to support OpenStack
# psycopg2 for Postgres installation
sudo yum --enablerepo=epel -y install make rpm-build python3 asciidoc git expect libffi-devel openssl-devel --skip-broken
sudo python3 -m ensurepip
sudo ln -s /usr/local/bin/pip3 /usr/bin/pip3

# install OpenStack+OTC extension+shade client lib
# to control the OpenStack by API
sudo /usr/local/bin/pip3 install --upgrade pip setuptools packaging

# thats new since 2018: shade is replaced by openstacksdk, which is now used by ansible
# and we also want to have opentelekomsdk extensions which automatically pulls
# a proper openstacksdk version as dependency
pushd /tmp
# make script more stable by preventive cleanup before clone
sudo rm -rf python-opentelekom-sdk
git clone https://github.com/tsdicloud/python-opentelekom-sdk
pushd python-opentelekom-sdk
sudo /usr/local/bin/pip3 install -r requirements.txt
sudo python3 setup.py install 
popd
sudo rm -rf python-opentelekom-sdk
popd
 
# checkout current version of ansible from git
# Ansible 2.x is not available as ready-made rpm package yet in repos
# generally, use /tmp as working directory
pushd /tmp
# make script more stable and do preventive cleanup
sudo rm -rf ansible
git clone git://github.com/ansible/ansible.git --branch v2.9.1
pushd ansible
sudo /usr/local/bin/pip3 install -r requirements.txt
sudo python3 setup.py install
popd
sudo rm -rf ansible
popd

# or installas rpm directly from ansible
#sudo yum install https://releases.ansible.com/ansible/rpm/release/epel-7-x86_64/ansible-2.7.9-1.el7.ans.noarch.rpm

# or, preferably, install ansible from python repo
# see also: http://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
# or even better: directly install from pip3
#sudo /usr/bin/pip3 install ansible

# enable TCP forwarding e.g. for VSCode Remote Development
sudo sed -i 's/^.*AllowTcpForwarding.*/AllowTcpForwarding yes/' /etc/ssh/sshd_config
sudo systemctl restart sshd
sudo -- bash -c "grep -q  'fs.inotify.max_user_watches' /etc/sysctl.conf && 
       sed -i 's/.*fs.inotify.max_user_watches.*/fs.inotify.max_user_watches=524288/' /etc/sysctl.conf || 
       echo 'fs.inotify.max_user_watches=524288' >> /etc/sysctl.conf"
sudo sysctl -p

# install an optional proxy on the ansible server
# as internet access point for local VMs
# for cases where a NATTING gateway is not an option
#sudo yum install -y squid
#sudo firewall-cmd --permanent --add-port=3128/tcp
#
#sudo systemctl enable squid
#sudo systemctl start squid
