"""
CheckiOReferee is a base referee for checking you code.
    arguments:
        tests -- the dict contains tests in the specific structure.
            You can find an example in tests.py.
        cover_code -- is a wrapper for the user function and additional operations before give data
            in the user function. You can use some predefined codes from checkio.referee.cover_codes
        checker -- is replacement for the default checking of an user function result. If given, then
            instead simple "==" will be using the checker function which return tuple with result
            (false or true) and some additional info (some message).
            You can use some predefined codes from checkio.referee.checkers
        add_allowed_modules -- additional module which will be allowed for your task.
        add_close_builtins -- some closed builtin words, as example, if you want, you can close "eval"
        remove_allowed_modules -- close standard library modules, as example "math"

checkio.referee.checkers
    checkers.float_comparison -- Checking function fabric for check result with float numbers.
        Syntax: checkers.float_comparison(digits) -- where "digits" is a quantity of significant
            digits after coma.

checkio.referee.cover_codes
    cover_codes.unwrap_args -- Your "input" from test can be given as a list. if you want unwrap this
        before user function calling, then using this function. For example: if your test's input
        is [2, 2] and you use this cover_code, then user function will be called as checkio(2, 2)
    cover_codes.unwrap_kwargs -- the same as unwrap_kwargs, but unwrap dict.

"""

SENDGRID_COVER = '''
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import sendgrid
from sendgrid.helpers.mail import *
try:
    import sendgrid.cio as cio
except ImportError:
    import cio
from datetime import datetime, timedelta
COUNTRIES = ['AM', 'AP', 'AR', 'AT', 'AU', 'AZ', 'BA', 'BD', 'BE', 'BF', 'BG', 'BO', 'BR', 'BY', 'CA', 'CH', 'CL', 'CN', 'CO', 'CR', 'CY', 'CZ', 'DE', 'DK', 'DO', 'DZ', 'EC', 'EE', 'EG', 'ES', 'EU', 'FI', 'FR', 'GB', 'GE', 'GR', 'GT', 'HK', 'HR', 'HU', 'ID', 'IE', 'IL', 'IN', 'IQ', 'IT', 'JM', 'JP', 'KE', 'KR', 'KW', 'KZ', 'LK', 'LT', 'LU', 'MA', 'MD', 'ME', 'MM', 'MO', 'MX', 'MY', 'NG', 'NL', 'NO', 'NZ', 'OM', 'PE', 'PH', 'PK', 'PL', 'PT', 'RO', 'RS', 'RU', 'SA', 'SD', 'SE', 'SG', 'SI', 'SK', 'TH', 'TN', 'TR', 'TW', 'UA', 'US', 'UZ', 'VE', 'VN', 'ZA']


try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

cio.set_testing_mode()

class MockStatsGet(cio.MockSimple):
    def __init__(self, start_date, stats):
        self.stats_dates = {}
        for data in stats:
            self.stats_dates[start_date] = data
            start_date += timedelta(days=1)

    def time_period_data(self, start_date, end_date):
        while start_date <= end_date:
            defined_data = self.stats_dates.get(start_date, {})
            yield self.generate_data(defined_data, start_date)
            start_date = start_date + timedelta(days=1)

    def generate_data(self, defined_data, cur_date):
        return {
            'date': cur_date.strftime('%Y-%m-%d'),
            'stats': list(self.generate_stats(defined_data))
        }

    def generate_stats(self, defined_data):
        for code in COUNTRIES:
            data = {'type': 'country', 'metrics': {'clicks': 0, 'opens': 0, 'unique_opens': 0, 'unique_clicks': 0}, 'name': code}
            data['metrics'].update(defined_data.get(code, {}))
            yield data

    def __call__(self, request):
        try:
            from urlparse import parse_qs
        except ImportError:
            from urllib.parse import parse_qs
        full_url = request.get_full_url()
        if '?' not in full_url:
            raise HTTPError(request.get_full_url(), 400, 'BAD REQUEST', '', StringIO())

        data = parse_qs(full_url.split('?')[1])

        start_date = end_date = limit = offset = None
        if 'start_date' in data:
            try:
                start_date = datetime.strptime(data['start_date'][0], '%Y-%m-%d')
            except ValueError:
                raise HTTPError(request.get_full_url(), 400, 'BAD REQUEST', '', StringIO())
        else:
            raise HTTPError(request.get_full_url(), 400, 'BAD REQUEST', '', StringIO())

        if 'end_date' in data:
            try:
                end_date = datetime.strptime(data['end_date'][0], '%Y-%m-%d')
            except ValueError:
                raise HTTPError(request.get_full_url(), 400, 'BAD REQUEST', '', StringIO())
        else:
            end_date = datetime.now()

        data = self.time_period_data(start_date, end_date)

        return sendgrid.Response(200, """Server: nginx
Date: Mon, 03 Apr 2017 14:43:27 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 0
Connection: close
X-Message-Id: wvYdP5GWR9aF5cneTovlHA
X-Frame-Options: DENY
Access-Control-Allow-Origin: https://sendgrid.api-docs.io
Access-Control-Allow-Methods: POST
Access-Control-Allow-Headers: Authorization, Content-Type, On-behalf-of, x-sg-elas-acl
Access-Control-Max-Age: 600
X-No-CORS-Reason: https://sendgrid.com/docs/Classroom/Basics/API/cors.html
""", json.dumps(list(data)).encode('utf-8'))

def cover(func, in_data):
    mock = MockStatsGet(datetime(2016, 1, 1), [
        {
            'IT': {'clicks': 12, 'opens': 30, 'unique_opens': 24, 'unique_clicks': 10},
            'FR': {'clicks': 7, 'opens': 12, 'unique_opens': 10, 'unique_clicks': 7},
            'SE': {'clicks': 10, 'opens': 15, 'unique_opens': 10, 'unique_clicks': 8}
        },
        {
            'IT': {'clicks': 88, 'opens': 120, 'unique_opens': 109, 'unique_clicks': 67},
            'FR': {'clicks': 6, 'opens': 12, 'unique_opens':10, 'unique_clicks': 5},
            'SE': {'clicks': 21, 'opens': 36, 'unique_opens': 25, 'unique_clicks': 19}

        },
        {
            'IT': {'clicks': 47, 'opens': 75, 'unique_opens': 56, 'unique_clicks': 33},
            'FR': {'clicks': 2, 'opens': 2, 'unique_opens': 2, 'unique_clicks': 2},
            'SE': {'clicks': 3, 'opens': 7, 'unique_opens': 4, 'unique_clicks': 2}

        },
        {
            'IT': {'clicks': 21, 'opens': 25, 'unique_opens': 22, 'unique_clicks': 20},
            'FR': {'clicks': 203, 'opens': 320, 'unique_opens': 223, 'unique_clicks': 156},
            'SE': {'clicks': 65, 'opens': 77, 'unique_opens': 70, 'unique_clicks': 44}

        },
        {
            'IT': {'clicks': 1, 'opens': 2, 'unique_opens': 1, 'unique_clicks': 1},
            'FR': {'clicks': 44, 'opens': 65, 'unique_opens': 58, 'unique_clicks': 34},
            'SE': {'clicks': 16, 'opens': 26, 'unique_opens': 21, 'unique_clicks': 12}

        },
        {
            'IT': {'clicks': 6, 'opens': 12, 'unique_opens': 8, 'unique_clicks': 4},
            'FR': {'clicks': 16, 'opens': 25, 'unique_opens': 21, 'unique_clicks': 12},
            'SE': {'clicks': 6, 'opens': 12, 'unique_opens': 9, 'unique_clicks': 4}

        },
        {
            'IT': {'clicks': 5, 'opens': 6, 'unique_opens': 5, 'unique_clicks': 3},
            'FR': {'clicks': 3, 'opens': 4, 'unique_opens': 3, 'unique_clicks': 3},
            'SE': {'clicks': 12, 'opens': 21, 'unique_opens': 18, 'unique_clicks': 8}

        },
        {
            'IT': {'clicks': 2, 'opens': 3, 'unique_opens': 2, 'unique_clicks': 1},
            'FR': {'clicks': 3, 'opens': 6, 'unique_opens': 5, 'unique_clicks': 3},
            'SE': {'clicks': 2, 'opens': 2, 'unique_opens': 2, 'unique_clicks': 1}

        },
        {
            'IT': {'clicks': 8, 'opens': 12, 'unique_opens': 12, 'unique_clicks': 6},
            'FR': {'clicks': 1, 'opens': 1, 'unique_opens': 1, 'unique_clicks': 1},
            'SE': {'clicks': 2, 'opens': 7, 'unique_opens': 5, 'unique_clicks': 2}

        }
    ])

    cio.set_mock('/geo/stats', mock)
    return func(*in_data)
    
'''

from checkio.signals import ON_CONNECT
from checkio import api
from checkio.referees.io import CheckiOReferee
from checkio.referees import cover_codes

from tests import TESTS

api.add_listener(
    ON_CONNECT,
    CheckiOReferee(
        tests=TESTS,
        function_name={
            "python": "best_country"
        },
        cover_code={
            'python-27': SENDGRID_COVER,
            'python-3': SENDGRID_COVER
        }
    ).on_ready)
