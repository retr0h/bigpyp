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


class Pool(object):
    """
    A class to manage a local load balancer's pools.
    """

    LB_METHOD = 'LB_METHOD_ROUND_ROBIN'
    MONITOR_RULE_TYPE = 'MONITOR_RULE_TYPE_SINGLE'
    MONITOR_RULE_QUORUM = 0

    def __init__(self, bigip, vips_dict):
        """
        Construct a Pool with the supplied args.

        :param bigip: An instance of the BigIP object.
        :param vips_dict: A dict containing VIP configuration.
        :returns: None
        """
        self._pool = bigip.pc.LocalLB.Pool
        self._vips_dict = vips_dict

    def create(self):
        print 'Pool'
        self._create_pools()

    def _create_pools(self):
        for vipname, vip_dict in self._vips_dict['load_balancing'].iteritems():
            domain = vip_dict['dns']
            port = vip_dict['back_port']
            pool = utils.pool_name(domain, port)
            monitor = vip_dict['monitor']
            members = vip_dict['members']
            monitor = '/Common/%(monitor)s' % vip_dict
            if members:  # skip unconfigured members
                self._create_pool(pool, members, port)
                self._set_monitor(pool, monitor)
                # Add new members if necesssary.  Probably will want to handle
                # the removal of old members at some point.
                self._add_missing_members(pool, members, port)

    def _create_pool(self, pool, hosts, port):
        pools = self._pool.get_list()
        if pool in pools:
            msg = '  - {0} already exists'.format(pool)
            utils.print_yellow(msg)
        else:
            # Odd, must create a sequence, even when the docs state othewise.
            # https://devcentral.f5.com/wiki/iControl.LocalLB__Pool__create_v2.ashx  # NOQA
            member_sequence = self._get_common_ip_port_definition_sequence()
            members = []
            for host in hosts:
                member = self._get_common_address_port(host, port)
                members.append(member)
            member_sequence.items = members
            self._pool.create_v2(pool_names=[pool],
                                 lb_methods=[self.LB_METHOD],
                                 members=[member_sequence])
            msg = '  - {0} created'.format(pool)
            utils.print_green(msg)

    def _set_monitor(self, pool, monitor):
        result = self._pool.get_monitor_association([pool])
        templates = result[0].monitor_rule.monitor_templates
        if monitor in templates:
            msg = '  - monitor {0} already exists for {1}'.format(monitor,
                                                                  pool)
            utils.print_yellow(msg)
        else:
            struct = 'LocalLB.MonitorRule'
            monitor_rule = self._pool.typefactory.create(struct)
            monitor_rule.type = self.MONITOR_RULE_TYPE
            monitor_rule.quorum = self.MONITOR_RULE_QUORUM
            monitor_rule.monitor_templates = [monitor]

            struct = 'LocalLB.Pool.MonitorAssociation'
            monitor_assoc = self._pool.typefactory.create(struct)
            monitor_assoc.pool_name = pool
            monitor_assoc.monitor_rule = monitor_rule

            args_dict = {'monitor_associations': [monitor_assoc]}
            self._pool.set_monitor_association(**args_dict)
            msg = '  - monitor {0} created for {1}'.format(monitor, pool)
            utils.print_green(msg)

    def _add_missing_members(self, pool, members, port):
        current_members = self._pool.get_member_v2(pool_names=[pool])
        members_list = [m.address.replace('/Common/', '')
                        for m in current_members[0]]
        for member in members:
            if member not in members_list:
                m = self._get_common_address_port(member, port)
                ms = self._get_common_ip_port_definition_sequence()
                ms.items = m
                self._pool.add_member_v2(pool_names=[pool],
                                         members=[ms])
                msg = '  - member {0} added to {1}'.format(member, pool)
                utils.print_green(msg)

    def _get_common_address_port(self, host, port):
        member = self._pool.typefactory.create('Common.AddressPort')
        member.address = host
        member.port = port
        return member

    def _get_common_ip_port_definition_sequence(self):
        struct = 'Common.IPPortDefinitionSequence'
        return self._pool.typefactory.create(struct)
