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


class Rule(object):
    """
    A class to manage a local load balancer's rules.
    """

    RULE_NAME = '/Common/https-offloaded-header'
    IRULE = ('when HTTP_REQUEST {\n'
             '  HTTP::header remove "X-Forwarded-Protocol";\n'
             '  HTTP::header insert "X-Forwarded-Protocol" "https";\n'
             '}')

    def __init__(self, bigip):
        """
        Construct a Rule with the supplied args.

        :param bigip: An instance of the BigIP object.
        :returns: None
        """
        self._rule = bigip.pc.LocalLB.Rule

    def create(self):
        print 'Rule'
        self._create_rule_x_forwarded_protocol()

    def _create_rule_x_forwarded_protocol(self):
        rules = self._rule.get_list()
        if self.RULE_NAME in rules:
            msg = '  - already has x-forwarded-protocol rule'
            utils.print_yellow(msg)
        else:
            struct = 'LocalLB.Rule.RuleDefinition'
            ctx = self._rule.typefactory.create(struct)
            ctx.rule_name = self.RULE_NAME
            ctx.rule_definition = self.IRULE
            self._rule.create([ctx])
            msg = '  - created x-forwarded-protocol rule'
            utils.print_green(msg)
