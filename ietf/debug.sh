#! /usr/bin/env bash

export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

trap 'mysql.server stop; kill $pid; exit' INT

mysql.server start

python -m smtpd -n -c DebuggingServer localhost:1025 &
pid=$!

echo "*** Starting secure development server at https://127.0.0.1:8443/"
(stunnel -fd 0 << EOF
cert = /usr/local/etc/stunnel/stunnel.pem
pid =
output = /dev/stdout
foreground = yes
debug = 4
[stunnel]
accept = 8443
connect = 8000
TIMEOUTbusy=3600
TIMEOUTclose=3600
TIMEOUTconnect=3600
TIMEOUTidle=3600
EOF
) &

PYTHONWARNINGS="d" HTTPS=1 PYTHONPATH=. python manage.py runserver
kill $pid
