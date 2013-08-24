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


class Monitor(object):
    """
    A class to manage monitor templates and instances.
    """

    MONITOR_NAME = '/Common/mysql_monitor'

    def __init__(self, bigip):
        """
        Construct Monitor with the supplied args.

        :param bigip: An instance of the BigIP object.
        :returns: None
        """
        self._monitor = bigip.pc.LocalLB.Monitor

    def create(self):
        print 'Monitor'
        self._create_mysql_monitor()

    def _create_mysql_monitor(self):
        monitors = self._monitor.get_template_list()
        filtered = [monitor for monitor in monitors
                    if monitor.template_name == self.MONITOR_NAME]
        if filtered:
            msg = '  - mysql_monitor already exists'
            utils.print_yellow(msg)
        else:
            # TODO(retr0h): How to upload a custom monitor.  Once uploaded
            # can configure an external template.
            msg = '  - need to upload and configure mysql_monitor'
            utils.print_red(msg)
