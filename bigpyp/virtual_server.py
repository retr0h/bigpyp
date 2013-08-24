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

import utils

import profile


class VirtualServer(object):
    """
    A class to manage a local load balancer's virtual servers.
    """

    PROTOCOL_TYPE = 'PROTOCOL_TCP'
    RESOURCE_TYPE = 'RESOURCE_TYPE_POOL'
    WILDMASKS = '255.255.255.255'
    SNAT_POOL = '/Common/fake-backend-snat'

    def __init__(self, bigip, vips_dict):
        """
        Construct a VirtualServer with the supplied args.

        :param bigip: An instance of the BigIP object.
        :param vips_dict: A dict containing VIP configuration.
        :returns: None
        """
        self._virtual_server = bigip.pc.LocalLB.VirtualServer
        self._vips_dict = vips_dict

    def create(self):
        print 'VirtualServer'
        self._create_virtual_servers()

    def _create_virtual_servers(self):
        for vipname, vip_dict in self._vips_dict['load_balancing'].iteritems():
            name = '/Common/%(dns)s_%(front_port)s' % vip_dict
            if vip_dict['members']:  # skip unconfigured members
                self._create_virtual_server(name, vip_dict)
                self._set_snat_pool(name)

    def _create_virtual_server(self, name, vip_dict):
        virtual_servers = self._virtual_server.get_list()
        domain = vip_dict['dns']
        if name in virtual_servers:
            msg = '  - {0} already exists'.format(name)
            utils.print_yellow(msg)
        else:
            vss = self._get_virtual_server_definition(name,
                                                      vip_dict['ip'],
                                                      vip_dict['front_port'],
                                                      self.PROTOCOL_TYPE)
            pool = utils.pool_name(domain, vip_dict['back_port'])
            vsrs = self._get_virtual_server_resource(pool)
            vsps = self._get_virtual_server_profile(vip_dict['monitor'],
                                                    domain)

            self._virtual_server.create(definitions=vss,
                                        wildmasks=[self.WILDMASKS],
                                        resources=vsrs,
                                        profiles=[vsps])
            msg = '  - {0} created'.format(name)
            utils.print_green(msg)

    def _set_snat_pool(self, name):
        result = self._virtual_server.get_snat_pool(virtual_servers=[name])
        if result[0] == self.SNAT_POOL:
            msg = '  - snat pool already exists for {0}'.format(name)
            utils.print_yellow(msg)
        else:
            self._virtual_server.set_snat_pool(virtual_servers=[name],
                                               snatpools=[self.SNAT_POOL])
            msg = '  - added snat pool for {0}'.format(name)
            utils.print_green(msg)

    def _get_virtual_server_definition(self, name, address, port, protocol):
        struct = 'Common.VirtualServerDefinition'
        vsd = self._virtual_server.typefactory.create(struct)
        vsd.name = name
        vsd.address = address
        vsd.port = port
        vsd.protocol = protocol

        struct = 'Common.VirtualServerSequence'
        vss = self._virtual_server.typefactory.create(struct)
        vss.item = [vsd]

        return vss

    def _get_virtual_server_resource(self, pool):
        struct = 'LocalLB.VirtualServer.VirtualServerResource'
        vsr = self._virtual_server.typefactory.create(struct)
        vsr.type = self.RESOURCE_TYPE
        vsr.default_pool_name = pool

        struct = 'LocalLB.VirtualServer.VirtualServerResourceSequence'
        vsrs = self._virtual_server.typefactory.create(struct)
        vsrs.item = [vsr]
        return vsrs

    def _get_virtual_server_profile(self, monitor, domain):
        struct = 'LocalLB.VirtualServer.VirtualServerProfile'
        profiles = []
        if monitor == 'tcp_half_open':
            if 'messaging' in domain:
                vsp_tcp_ka = self._virtual_server.typefactory.create(struct)
                vsp_tcp_ka.profile_context = 'PROFILE_CONTEXT_TYPE_ALL'
                vsp_tcp_ka.profile_name = profile.TCPProfile.PROFILE_NAME
                profiles.append(vsp_tcp_ka)
        else:
            vsp_tcp = self._virtual_server.typefactory.create(struct)
            vsp_tcp.profile_context = 'PROFILE_CONTEXT_TYPE_ALL'
            vsp_tcp.profile_name = '/Common/tcp'
            profiles.append(vsp_tcp)
        if monitor == 'http':
            vsp_xff = self._virtual_server.typefactory.create(struct)
            vsp_xff.profile_context = 'PROFILE_CONTEXT_TYPE_ALL'
            vsp_xff.profile_name = profile.HTTPProfile.PROFILE_NAME
            profiles.append(vsp_xff)
            if utils.public_domain(domain):
                vsp_ssl = self._virtual_server.typefactory.create(struct)
                vsp_ssl.profile_context = 'PROFILE_CONTEXT_TYPE_CLIENT'
                vsp_ssl.profile_name = utils.ssl_profile_name(domain)
                profiles.append(vsp_ssl)
        struct = 'LocalLB.VirtualServer.VirtualServerProfileSequence'
        vsps = self._virtual_server.typefactory.create(struct)
        vsps.item = profiles
        return vsps
