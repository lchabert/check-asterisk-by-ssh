#!/usr/bin/env python

# Copyright (C) 2014:
# Chabert Loic, chabert.loic.74@gmail.com
# Gabes Jean, naparuba@gmail.com
# Pasche Sebastien, sebastien.pasche@leshop.ch
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import os
import sys
import optparse
import base64
import subprocess
try:
    import paramiko
except ImportError:
    print "ERROR : this plugin needs the python-paramiko module. Please install it"
    sys.exit(2)

# Ok try to load our directory to load the plugin utils.
my_dir = os.path.dirname(__file__)
sys.path.insert(0, my_dir)

try:
    import schecks
except ImportError:
    print "ERROR : this plugin needs the local schecks.py lib. Please install it"
    sys.exit(2)

VERSION = "0.1"
DEFAULT_WARNING = 10
DEFAULT_CRITICAL = 20

def get_channels(client):
    # We are looking for a line like
    #0.19 0.17 0.15 1/616 3634 4
    # l1 l5 l15 _ _ nb_cpus
    raw = r"""asterisk -rx 'core show channels' | grep 'active call'"""
    stdin, stdout, stderr = client.exec_command(raw)
    line = [l for l in stdout][0].strip()
    
    data = line.split(" ")
    active_calls = int(data[0])

    raw = r"""asterisk -rx 'core show channels' | grep 'active channel'"""
    stdin, stdout, stderr = client.exec_command(raw)
    line = [l for l in stdout][0].strip()
    data = line.split(" ")
    active_channels = int(data[0])
    client.close()
    return active_channels,active_calls


parser = optparse.OptionParser(
    "%prog [options]", version="%prog " + VERSION)
parser.add_option('-H', '--hostname',
                  dest="hostname", help='Hostname to connect to')
parser.add_option('-i', '--ssh-key',
                  dest="ssh_key_file", help='SSH key file to use. By default will take ~/.ssh/id_rsa.')
parser.add_option('-u', '--user',
                  dest="user", help='remote use to use. By default shinken.')
parser.add_option('-p', '--port',
                  dest="port", help='SSH remote TCP port. By default will use 22')
parser.add_option('-P', '--passphrase',
                  dest="passphrase", help='SSH key passphrase. By default will use void')

parser.add_option('-w', '--warning_calls',
                  dest="warning_calls", help='Warning value for active calls. Default : 10')
parser.add_option('-c', '--critical_calls',
                  dest="critical_calls", help='Critical value for active calls. Default : 20')
parser.add_option('-W', '--warning_chan',
                  dest="warning_channels", help='Warning value for active channels. Default : 10')
parser.add_option('-C', '--critical_chan',
                  dest="critical_channels", help='Critical value for active channels. Default : 20')

if __name__ == '__main__':
    # Ok first job : parse args
    opts, args = parser.parse_args()
    if args:
        parser.error("Does not accept any argument.")

    hostname = opts.hostname
    if not hostname:
        print "Error : hostname parameter (-H) is mandatory"
        sys.exit(2)

    ssh_key_file = opts.ssh_key_file or os.path.expanduser('~/.ssh/id_rsa')
    user = opts.user or 'shinken'
    passphrase = opts.passphrase or ''
    try:
        port = int(opts.port) or 22
    except:
        print "Error : port parameter (-p) must be an integer"

    # Try to get numeic warning/critical values
    s_warning_calls =  s_warning_channels = DEFAULT_WARNING
    s_critical_calls = s_critical_channels = DEFAULT_CRITICAL
    
    try:
        if opts.warning_calls: 
            s_warning_calls = int(opts.warning_calls)
        if opts.critical_calls:
            s_critical_calls = int(opts.warning_calls)
        if opts.warning_channels: 
            s_warning_channels = int(opts.warning_channels)
        if opts.critical_channels:
            s_critical_channels = int(opts.critical_channels)
    except:
        print "Error : warning and critical parameters (-c,-w) must be an integer"
        sys.exit(3)

    client = schecks.connect(hostname, ssh_key_file, passphrase, user, port)
    active_channels, active_calls = get_channels(client)

    #check if we value is not greater than warning and critical
    status = 0
    if active_channels >= s_warning_channels:
        status = 1
    if active_channels >= s_critical_channels:
        status = 2
    if active_calls >= s_warning_calls:
        status = 3
    if active_calls >= s_critical_calls:
        status = 4

    perfdata = ''
    perfdata += ' active_channels=%d;%d;%d;;' % (active_channels,s_warning_channels,s_critical_channels)
    perfdata += ' active_calls=%d;%d;%d;;' % (active_calls,s_warning_calls,s_critical_calls)

    if status == 1:
        print "Warning: number of channels is very high %s | %s" % (active_channels, perfdata)
        sys.exit(1)

    if status == 2:
        print "Critical: number channels is too high %s | %s" % (active_channels, perfdata)
        sys.exit(2)
    
    if status == 3:
        print "Warning: number of call is very high %s | %s" % (active_calls, perfdata)
        sys.exit(1)

    if status == 4:
        print "Warning: number of call is too high %s | %s" % (active_calls, perfdata)
        sys.exit(1)

    print "Ok: number of call is good %s and channels too %s| %s" % (active_calls, active_channels, perfdata)
    sys.exit(0)