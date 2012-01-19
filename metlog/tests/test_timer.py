# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is metlog
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2011
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   Rob Miller (rmiller@mozilla.com)
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****
from metlog.client import _Timer, MetlogClient
from mock import Mock
from nose.tools import assert_raises, eq_, ok_

import threading
import time


def _make_em():
    mock_client = Mock(spec=MetlogClient)
    timer = _Timer(mock_client)
    return mock_client, timer


def test_enforce_name():
    mock_client, timer = _make_em()

    def no_name_timer():
        with timer:
            time.sleep(0.01)
    assert_raises(ValueError, no_name_timer)

    def timed():
        time.sleep(0.01)
    assert_raises(ValueError, timer, timed)


def test_contextmanager():
    mock_client, timer = _make_em()
    with timer('name') as result:
        time.sleep(0.01)

    eq_(mock_client.timing.call_count, 1)
    timing_args = mock_client.timing.call_args[0]
    eq_(timing_args[0], timer)
    ok_(timing_args[1] >= 10)
    eq_(timing_args[1], result.ms)


def test_decorator():
    mock_client, timer = _make_em()

    @timer('name')
    def timed():
        time.sleep(0.01)

    timed()
    eq_(mock_client.timing.call_count, 1)
    timing_args = mock_client.timing.call_args[0]
    eq_(timing_args[0], timer)
    ok_(timing_args[1] >= 10)


def test_attrs_threadsafe():
    mock_client, timer = _make_em()

    def reentrant(val):
        sentinel = object()
        if getattr(timer, 'value', sentinel) is not sentinel:
            ok_(False, "timer.value already exists in new thread")
        timer.value = val

    t0 = threading.Thread(target=reentrant, args=(10,))
    t1 = threading.Thread(target=reentrant, args=(100,))
    t0.start()
    time.sleep(0.01)  # give it enough time to be sure timer.value is set
    t1.start()  # this will raise assertion error if timer.value from other
                # thread leaks through