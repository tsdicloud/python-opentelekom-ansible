#!/bin/bash

# please install openstack-client first


# add Fedora epel repository
sudo yum -y install epel-release
#rpm -Uvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm

# patch CentOS to most frequent level
sudo yum -y update --skip-broken

# prepare to build a current version of ansible (>= 2.0) to support OpenStack
# psycopg2 for Postgres installation
sudo yum --enablerepo=epel -y install make rpm-build python36-psycopg2 python36-docutils asciidoc git expect libffi-devel openssl-devel --skip-broken

# install OpenStack+OTC extension+shade client lib
# to control the OpenStack by API
sudo /usr/bin/pip3 install --upgrade pip setuptools packaging

# thats new since 2018: shade is replaced by openstacksdk, which is now used by ansible
# and the public available pip version has a version problem, so we have to install from source
# sudo /usr/local/bin/pip3 install openstacksdk
pushd /tmp
git clone https://github.com/openstack/openstacksdk
pushd openstacksdk
sudo /usr/local/bin/pip3 install -r requirements.txt
sudo python3 setup.py install 
popd
rm -rf openstacksdk
popd
 
# checkout current version of ansible from git
# Ansible 2.x is not available as ready-made rpm package yet in repos
# generally, use /tmp as working directory
pushd /tmp
git clone git://github.com/ansible/ansible.git --branch stable-2.8
pushd ansible
sudo /usr/local/bin/pip3 install -r requirements.txt
sudo python3 setup.py install
popd
rm -rf /tmp/ansible
popd

# or installas rpm directly from ansible
#sudo yum install https://releases.ansible.com/ansible/rpm/release/epel-7-x86_64/ansible-2.7.9-1.el7.ans.noarch.rpm

# or, preferably, install ansible from python repo
# see also: http://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html
# or even better: directly install from pip3
sudo /usr/local/bin/pip3 install ansible


# install an optional proxy on the ansible server
# as internet access point for local VMs
# for cases where a NATTING gateway is not an option
#sudo yum install -y squid
#sudo firewall-cmd --permanent --add-port=3128/tcp
#
#sudo systemctl enable squid
#sudo systemctl start squid
