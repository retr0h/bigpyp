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

import unittest2 as unittest

from bigpyp import utils


class TestUtils(unittest.TestCase):
    #def filter_on_public(vips_dict):
    #    vd = vips_dict['load_balancing'].iteritems()
    #    filtered = [(k, v) for k, v in vd
    #                if public_domain(v['dns'])]
    #    return dict(filtered)

    def test_filter_on_public(self):
        pass

    def test_public_domain(self):
        domain = 'foo.dpa1.attcompute.com'
        result = utils.public_domain(domain)
        self.assertEqual(True, result)

    def test_public_domain_returns_false_when_internal_domain(self):
        domain = 'foo.int.dpa1.attcompute.com'
        result = utils.public_domain(domain)
        self.assertEqual(False, result)

    def test_pool_name(self):
        domain = 'foo.dpa1.attcompute.com'
        port = '5000'
        result = utils.pool_name(domain, port)
        self.assertEqual('/Common/foo.dpa1.attcompute.com_5000_pl', result)

    def test_ssl_profile_name(self):
        domain = 'foo.dpa1.attcompute.com'
        result = utils.ssl_profile_name(domain)
        self.assertEqual('/Common/foo.dpa1.attcompute.com_pr', result)
