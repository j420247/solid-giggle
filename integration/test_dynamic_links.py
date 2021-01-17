# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for firebase_admin.auth module."""
import sys

import pytest

from firebase_admin import dynamic_links
from tests import testutils

dynamic_links_e2e_url = ''
try:
    dynamic_links_e2e_url = testutils.resource('dynamic_links_e2e_url.txt').strip()
except IOError:
    sys.stderr.write('\nEnd-to-end tests not set up, see CONTRIBUTING.md file.\n')

@pytest.mark.skipif(not dynamic_links_e2e_url,
                    reason='End-to-end tests not set up, see CONTRIBTING.md file.')
class TestEndToEnd(object):
    """Runs an end-to-end test, see comment string for setup."""

    def test_get_stats(self):
        link_stats = dynamic_links.get_link_stats(
            dynamic_links_e2e_url,
            dynamic_links.StatOptions(last_n_days=4000))
        assert isinstance(link_stats, dynamic_links.LinkStats)
        assert len(link_stats.event_stats) > 0

    def test_get_stats_nonexistant_link(self):
        link_stats = dynamic_links.get_link_stats(
            dynamic_links_e2e_url + 'some_arbitary_unlikely_string_ZXCzxcASDasdQWEqwe',
            dynamic_links.StatOptions(last_n_days=4000))
        assert isinstance(link_stats, dynamic_links.LinkStats)
        assert len(link_stats.event_stats) == 0

class TestServerErrors(object):
    def test_unauthorized(self):
        with pytest.raises(dynamic_links.ApiCallError) as excinfo:
            dynamic_links.get_link_stats(
                'https://fake1.app.goo.gl/uQWc',
                dynamic_links.StatOptions(last_n_days=4000))
        assert excinfo.value.code == 'authentication-error'

    @pytest.mark.skipif(not dynamic_links_e2e_url,
                        reason='End-to-end tests not set up, see CONTRIBTING.md file.')
    def test_bad_request(self):
        with pytest.raises(dynamic_links.ApiCallError) as excinfo:
            dynamic_links.get_link_stats(
                dynamic_links_e2e_url + '/too/many/slashes/in/shortlink',
                dynamic_links.StatOptions(last_n_days=4000))
        assert excinfo.value.code == 'invalid-argument'
        assert 'Request contains an invalid argument' in str(excinfo.value)
