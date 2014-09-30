#!/usr/bin/env python3

"""Generates network topology from the results of traceroute

From the current host, a set of hosts can be tried to be reached by using the
``traceroute`` facility. The hosts that has responded will be remembered. Then
all the topology of the hosts that has been reached is going to be generated.

"""

import subprocess
import ipaddress
import collections
import socket
import itertools
import sys


#
# The data type for an internet host
# ----------------------------------
#

Host = collections.namedtuple(
    'Host',
    ['hostname',
     'ip']
    )


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

    return hosts


#
# Network Topology
# ----------------
#

class Topology(object):

    """A simple data structure for network topology
    
    It is just consisted of a list of nodes and a list of pairs giving the
    neighbours as zero-based indices.

    """

    __slots__ = [
        'nodes',
        'neighbs'
        ]

    def __init__(self):
        """Initializes the topology into an empty one"""
        self.nodes = []
        self.neighbs = []

    def __contains__(self, key):
        """Queries the existence of a node in the topology"""
        return key in self.nodes

    def query_node(self, node):

        """Queries the index for a node in the topology

        The zero-based integral index will be returned it is exists in the
        topology, or ValueError is going to be raised if it is not there.

        """

        return self.nodes.index(node)

    def add_neighb(self, node1, node2):

        """Adds two new neighbouring nodes into the topology"""

        if node1 not in self:
            self.nodes.append(node1)
        if node2 not in self:
            self.nodes.append(node2)

        idx1 = self.query_node(node1)
        idx2 = self.query_node(node2)

        self.neighbs.append(
            (idx1, idx2) if idx1 < idx2 else (idx2, idx1)
            )

    def add_chain(self, chain):

        """Adds a chain of neighbours into the topology
        
        It removes the neighbours in the chain that is equal.

        """
        
        chain_uniq = [k for k, g in itertools.groupby(chain)]

        for i in range(0, len(chain_uniq) - 1):
            node1 = chain_uniq[i]
            node2 = chain_uniq[i + 1]
            self.add_neighb(node1, node2)
            continue

    def add_chains(self, chains, func):

        """Adds multiple chains into the topology
        
        An function can be given that will be called for each element of the
        chain before they are added.

        """

        for i in chains:
            self.add_chain(
                func(j) for j in i
                )
            continue

    def write_Pajek(self, file_name, str_fun):

        """Writes the topology into a file in Pajek format

        :param file_name: The file name to dump the information
        :param str_fun: The function to convert each node into a string

        """

        with open(file_name, 'w') as out_file:

            print(
                "*Vertices %d" % (len(self.nodes), ), file=out_file
                )
            for i, v in enumerate(self.nodes):
                print(" %d \"%s\" " % (i + 1, str_fun(v)), file=out_file)
                continue

            print("*Edges", file=out_file)
            for i in self.neighbs:
                print(" %d  %d " % (i[0] + 1, i[1] + 1), file=out_file)
                continue


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

    host_topology = Topology()
    host_topology.add_chains(chains, lambda x: x)

    network_topology = Topology()
    def get_network(host):
        ip_parts = str(host.ip).split('.')[0:3]
        return '.'.join(ip_parts)
    network_topology.add_chains(chains, get_network)

    base_name = input_filename.split('.')[0]
    host_topology.write_Pajek(
        base_name + '-host-topology.NET',
        lambda x: x.hostname
        )
    network_topology.write_Pajek(
        base_name + '-network-topology.NET',
        str
        )


if __name__ == '__main__':
    main()
