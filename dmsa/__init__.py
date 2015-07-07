import os

serial = os.environ.get('CIRCLE_BUILD_NUM')
sha = os.environ.get('CIRCLE_SHA1')
if sha:
    sha = sha[0:8]

__version_info__ = {
    'major': 0,
    'minor': 4,
    'micro': 0,
    'releaselevel': 'alpha',
    'serial': serial,
    'sha': sha
}


def get_version(short=False):
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ['%(major)i.%(minor)i.%(micro)i' % __version_info__, ]
    if __version_info__['releaselevel'] != 'final' and not short:
        vers.append('-%(releaselevel)s' % __version_info__)
        if __version_info__['serial'] or __version_info__['sha']:
            vers.append('+%(serial)s.%(sha)s' % __version_info__)
    return ''.join(vers)

__version__ = get_version()
