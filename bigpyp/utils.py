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

import re

from termcolor import colored

RE_INTERNAL_DOMAIN = re.compile(r'\.int\..*\.com')


def print_green(msg):
    print colored(msg, 'green')


def print_yellow(msg):
    print colored(msg, 'yellow')


def print_red(msg):
    print colored(msg, 'red')


def filter_on_public(vips_dict):
    vd = vips_dict['load_balancing'].iteritems()
    filtered = [(k, v) for k, v in vd
                if public_domain(v['dns'])]
    return dict(filtered)


def public_domain(domain):
    if not RE_INTERNAL_DOMAIN.search(domain):
        return True
    return False


def pool_name(domain, port):
    return '/Common/%(domain)s_%(port)s_pl' % locals()


# TODO(retr0h): This needs to be handled bit cleaner.
def ssl_profile_name(domain):
    return '/Common/%(domain)s_pr' % locals()
