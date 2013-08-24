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


class System(object):
    """
    A class to manage system-level services.
    """

    NTP_SERVERS_LIST = ['12.129.64.150',
                        '63.240.192.73',
                        '63.240.192.148']

    def __init__(self, bigip):
        """
        Construct a System with the supplied args.

        :param bigip: An instance of the BigIP object.
        :returns: None
        """
        self._pc = bigip.pc

    def create(self):
        print 'System'
        self._set_ntp_servers()
        self._set_time_zone()

    def _set_ntp_servers(self):
        inet = self._pc.System.Inet
        result = inet.get_ntp_server_address()
        if sorted(result) == sorted(self.NTP_SERVERS_LIST):
            msg = '  - already has ntp servers'
            utils.print_yellow(msg)
        else:
            inet \
                .set_ntp_server_address(ntp_addresses=self.NTP_SERVERS_LIST)
            msg = '  - added ntp servers'
            utils.print_green(msg)

    def _set_time_zone(self):
        """
        TODO(retr0h): How to set the time zone.  Cannot find API docs on how
        to do this.  The current timezone can be obtained via:
          ``self._pc.System.SystemInfo.get_time_zone().time_zone``
        """
        system_info = self._pc.System.SystemInfo
        result = system_info.get_time_zone()
        if result.time_zone == 'UTC':
            msg = '  - already has UTC time'
            utils.print_yellow(msg)
        else:
            msg = '  - need to set device to UTC time'
            utils.print_red(msg)
