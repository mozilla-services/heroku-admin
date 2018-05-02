#!/usr/bin/env python3

# This script identifies org users who do not have 2FA enabled,
# along with which apps their account can access. For example:
#
#   $ ./heroku-2fa.py
#   The following mozillacorporation users do not have 2FA enabled!
#
#   ~ 1 members:
#   some-user1@mozilla.com
#
#   ~ 3 collaborators:
#   some-user2@mozilla.com
#   some-user3@mozilla.com
#
#   3 apps are affected:
#
#   app-one (some-user3@mozilla.com)
#   app-two (some-user2@mozilla.com, some-user4@mozilla.com)
#   app-three (some-user1@mozilla.com)

import sys
from collections import defaultdict

import requests
from requests.utils import get_netrc_auth


ORG_NAME = 'mozillacorporation'
# https://devcenter.heroku.com/articles/platform-api-reference#organization-member
ORG_USERS_URL = 'https://api.heroku.com/organizations/{}/members'.format(ORG_NAME)
# https://devcenter.heroku.com/articles/platform-api-reference#clients
REQUEST_HEADERS = {
    'Accept': 'application/vnd.heroku+json; version=3',
    'User-Agent': 'build-stats',
}

session = requests.session()


def find_users_missing_2fa():
    org_users = fetch_api_json(ORG_USERS_URL)
    users_missing_2fa = defaultdict(set)
    for user in org_users:
        if not user['two_factor_authentication']:
            users_missing_2fa[user['role']].add(user['email'])
    return users_missing_2fa


def apps_accessible_by_user(email, role):
    if role == 'admin':
        return ['ALL']
    users_apps_url = '{}/{}/apps'.format(ORG_USERS_URL, email)
    return [app['name'] for app in fetch_api_json(users_apps_url)]


def fetch_api_json(url):
    # The requests library will automatically use credentials found in netrc.
    response = session.get(url, headers=REQUEST_HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    if not get_netrc_auth(ORG_USERS_URL):
        print('Heroku API credentials not found in `~/.netrc` or `~/_netrc`.\n'
              'Log in using the Heroku CLI to generate them.')
        sys.exit(1)

    users_missing_2fa = find_users_missing_2fa()

    if not users_missing_2fa:
        print('All {} users have 2FA enabled :)'.format(ORG_NAME))
        sys.exit(0)

    print('The following {} users do not have 2FA enabled!'.format(ORG_NAME))
    affected_apps = defaultdict(set)
    for role, users in users_missing_2fa.items():
        print('\n~ {} {}s:'.format(len(users), role))
        for email in sorted(users):
            for app in apps_accessible_by_user(email, role):
                affected_apps[app].add(email)
            print(email)

    if affected_apps:
        print('\n{} apps are affected:\n'.format(len(affected_apps)))
        for app, emails in sorted(affected_apps.items()):
            print('{} ({})'.format(app, ', '.join(sorted(emails))))


if __name__ == "__main__":
    main()
