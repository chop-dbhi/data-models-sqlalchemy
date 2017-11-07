""" A simple module for caching a single object on disk"""
import cPickle as pickle
import errno
import logging
import os
import simpleflock

__LOCK_FILE = 'dmsa.cache.lockfile'
__CACHE_FILE = 'dmsa.cache'
__DIR = None


def set_cache_dir(cache_dir):
    """Set the directory to use for holding cache and lock files

    If the directory is never set, the current directory is used (see below).
    """
    global __DIR
    __DIR = cache_dir


def _pathname(name):
    """Ensure directory `__DIR` exists and return path name

    If `__DIR` is falsy, simply return `name` as the pathname.

    Otherwise, create `__DIR` if necessary, and return the pathname.

    Return: the pathname resulting from path-joining `__DIR` and `name`
        (or just `name`).
    """
    if not __DIR:
        return name

    try:
        os.makedirs(__DIR)
    except OSError:
        pass

    return os.path.join(__DIR, name)


def _pickle_and_cache_models(obj):
    pathname = _pathname(__CACHE_FILE)
    try:
        with open(pathname, mode='w') as f:
            pickle.dump(obj, f)
    except pickle.PicklingError as e:
        logging.error('pickling object: {}'.format(e))
        raise
    except IOError as e:
        logging.error('opening {} for writing: {}'.format(pathname, e))
        raise


def set_cache(obj):
    """Update the cache with an object (dict, e.g.)

    The object is cached on disk. A lock file is used to coordinate
    updates to this cache among threads and processes.

    If another process has the cache locked (only used for writing),
    then this function does nothing; i.e. it assumes that somebody
    else is taking care of the update ....

    Arguments:
        obj - object to write to the cache

    Return:
        none
    """
    lock_path = _pathname(__LOCK_FILE)
    try:
        with simpleflock.SimpleFlock(lock_path, timeout=0):
            _pickle_and_cache_models(obj)
    except IOError as e:
        if e.errno != errno.EWOULDBLOCK:
            logging.error('creating lock file {}: {}'.format(lock_path, e))
            raise


def get_cache():
    """Fetch the object from disk cache

    Return: cached object as written by set_cache, or None if no cache file
    """
    pathname = _pathname(__CACHE_FILE)
    try:
        with open(pathname, mode='r') as f:
            try:
                obj = pickle.load(f)
            except pickle.UnpicklingError as e:
                logging.error('unpickling object: {}'.format(e))
                raise
    except IOError as e:
        if e.errno == errno.ENOENT:
            return None
        logging.error('opening {} for reading: {}'.format(pathname, e))
        raise

    return obj
