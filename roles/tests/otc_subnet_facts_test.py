---  
  - name: Find subnet facts
    otc_subnet_facts:
      auth_type: password
      auth:
        "{{ otc_os_auth }}"
      cacert: "{{ otc_cert_file }}"
      validate_certs: "yes"
      name: "rbe-sn-profidata-worker" 
    register: subnet_facts

  - debug:
      var: subnet_facts 
