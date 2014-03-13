check-asterisk-by-ssh
=======================

Several plugins of monitoring tools based on io-shinken-checks-linux.
No plugin requiered, only ssh and RSA keys.
Use asterisk -rx '<command>' to make checks.

check-asterisk-peers
=======================
check-asterisk-peers.py -H localhost -p 22 -u shinken -w 20 -c 30

check-asterisk-channels
=======================
check-asterisk-channels.py -H localhost -p 22 -u shinken -w 20 -c 30 -W 20 -C 30

-w : warning calls trigger

-c : critical calls trigger

-W : warning channels trigger

-C : critical channels trigger