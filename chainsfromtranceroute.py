#!/usr/bin/env python3

"""Generates chains of network neighbour from the results of traceroute

From the current host, a set of hosts can be tried to be reached by using the
``traceroute`` facility. Then the chains of neighbour hosts are going to be
dumped into a pickle file to be further processed.

"""

import subprocess
import ipaddress
import socket
import sys
import pickle


from host import Host

#
# Querying hosts information
# --------------------------
#

def get_curr_host():

    """Returns the Host data structure for the host that the code running on"""

    hostname = subprocess.check_output(['hostname', '-f']).decode('utf-8')
    ip = subprocess.check_output(['hostname', '-i']).decode('utf-8')

    return Host(
        hostname=hostname.strip(),
        ip=ipaddress.ip_address(ip.strip())
        )

def get_dest_host(dest):

    """Gets the Host data structure for the destination
    
    The destination is given as a string for its hostname.

    """

    ip = socket.gethostbyname(dest)
    return Host(hostname=dest,
                ip=ipaddress.ip_address(ip))

def get_hosts_on_route(dest):

    """Returns a list of hosts by invoking traceroute on the destination

    Note that the origin and destination themselves are also included.

    """

    hosts = [get_curr_host(), ]

    waiting_time = 15
    max_hop = 30
    raw_out = subprocess.check_output(
        ['traceroute', '-w', str(waiting_time), '-m', str(max_hop), dest]
        ).decode('utf-8')

    for line in raw_out.split('\n')[1:-1]:
        fields = line.split()
        if fields[1] == '*':
            continue
        hostname = fields[1]
        ip = fields[2].strip('()')
        hosts.append(
            Host(hostname=hostname, ip=ipaddress.ip_address(ip))
            )
        continue

    hosts.append(get_dest_host(dest))

    print(" Host %s successfully reached." % dest)

    return hosts


#
# The main driver
# ---------------
#

def main():

    """The main driver function

    The list of destinations are going to be read from the file with name given
    as the first command line argument.

    """

    try:
        input_filename = sys.argv[1]
    except IndexError:
        print("Input file name not given!")
        raise

    with open(input_filename, 'r') as inp_f:
        dests = [i.strip() for i in inp_f]

    chains = [get_hosts_on_route(i) for i in dests]

    base_name = input_filename.split('.')[0]
    with open(base_name + '.pickle', 'w') as out_file:
        pickle.dump(chains, out_file)

    print("Chains dumped into the output file %s.pickel" % base_name)


if __name__ == '__main__':
    main()
