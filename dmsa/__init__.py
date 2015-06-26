import os

serial = os.environ.get('CIRCLE_BUILD_NUM') or 0
sha = os.environ.get('CIRCLE_SHA1') or 'untested'

__version_info__ = {
    'major': 0,
    'minor': 3,
    'micro': 1,
    'releaselevel': 'beta',
    'serial': serial,
    'sha': sha
}


def get_version(short=False):
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ["%(major)i.%(minor)i.%(micro)i" % __version_info__, ]
    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('%s%i+%s' % (__version_info__['releaselevel'][0],
                                 int(__version_info__['serial']),
                                 __version_info__['sha'].lower()[:8]))
    return ''.join(vers)


__version__ = get_version()
