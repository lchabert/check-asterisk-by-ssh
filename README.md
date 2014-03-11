check-asterisk-by-ssh
=======================

Several plugins of monitoring tools based on io-shinken-checks-linux.
No plugin requiered, only ssh and RSA keys.
Use asterisk -rx '<command>' to make checks.

check-asterisk-peers
=======================
check_asterisk-peers.py -H localhost -p 22 -u shinken -w 20 -c 30