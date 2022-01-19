#!/bin/bash

########################################################################################################################

cat > /etc/systemd/system/rt.service << EOF
[Unit]
Description=Radio Telescope
After=network.target

[Service]
ExecStart=/home/rock/rt/bin/rt
WorkingDirectory=/home/rock/rt
StandardOutput=null
StandardError=inherit
Restart=always
User=root

[Install]
WantedBy=multi-user.target
EOF

########################################################################################################################

systemctl enable rt.service
systemctl restart rt.service
systemctl status rt.service

########################################################################################################################
