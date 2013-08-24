# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013, AT&T Services, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations

"""Load Balancer.

Usage:
  load_balancer.py zone <name>

Options:
  -h --help     Show this screen
  --version     Show version
"""

import logging
import os
import yaml

import pycontrol.pycontrol as pc

from docopt import docopt
from pbr import version

import cert
import monitor
import pool
import profile
import rule
import system
import virtual_server


class LoadBalancer(object):
    """
    A class representing a load balancer.  Handles the high-level
    configuration details.

    High-level is defined as:
      * On the network with proper interfaces, bonding, and vlans configured
      * Licensed (if applicable)
      * Firmware current (if applicable)
      * Established cluster
      * Outside/inside interfaces configured
    """
    def __init__(self, **kwargs):
        pass


class BigIP(LoadBalancer):
    """
    A class representing a BigIP load balancer.
    """

    DEFAULT_USER = "admin"
    DEFAULT_PASS = "admin"
    DEFAULT_HOST = "localhost"
    DEFAULT_LOGGING = False
    WSDL_LIST = ['LocalLB.Monitor',
                 'LocalLB.Pool',
                 'LocalLB.ProfileClientSSL',
                 'LocalLB.ProfileHttp',
                 'LocalLB.ProfileTCP',
                 'LocalLB.Rule',
                 'LocalLB.VirtualServer',
                 'Management.KeyCertificate',
                 'System.Inet',
                 'System.SystemInfo']

    def __init__(self, **kwargs):
        """
        Construct a BigIP with the supplied args.

        :param kwargs['username']: A string containing the username to use.
        :param kwargs['password']: A string containing the password to use.
        :param kwargs['host']: A string containing host to connect.
        :param kwargs['debug']: A boolean toggling suds client logging.
        :returns: None
        """
        if kwargs.get('debug', self.DEFAULT_LOGGING):
            logging.basicConfig(level=logging.INFO)
            logging.getLogger('suds.client').setLevel(logging.DEBUG)
        username = kwargs.get('username', self.DEFAULT_USER)
        password = kwargs.get('password', self.DEFAULT_PASS)
        host = kwargs.get('host', self.DEFAULT_HOST)
        self.pc = self._get_pc(username, password, host)

    def _get_pc(self, username, password, host, fromurl=True):
        """
        Create and return an instance of the BigIP object.

        :param username: A string containing the username to use.
        :param password: A string containing the password to use.
        :param host: A string containing host to connect.
        :param fromurl: A boolean to determine if the WSDL should
                        be fetched from the `host`.
        :returns: BigIP
        """
        return pc.BIGIP(username=username,
                        password=password,
                        hostname=host,
                        fromurl=fromurl,
                        wsdls=self.WSDL_LIST)


if __name__ == '__main__':
    version = 'Load Balancer {0}'.format(version.VersionInfo('bigpyp'))
    args = docopt(__doc__, version=version)

    f = '../conf/{0}_vips.yml'.format(args['<name>'])
    with open(f, 'r') as file:
        vips_dict = yaml.load(file)
        b = BigIP(host='192.168.112.62', password=os.environ['PASS'])

        cert.Cert(b, vips_dict).create()
        profile.Profile(b, vips_dict).create()
        system.System(b).create()
        rule.Rule(b).create()
        monitor.Monitor(b).create()
        pool.Pool(b, vips_dict).create()
        virtual_server.VirtualServer(b, vips_dict).create()
