import cPickle as pickle
import logging
import os
import simpleflock

__LOCK_FILE = 'dmsa.models.lockfile'
__MODELS_FILE = 'dmsa.models'
__RESOURCE_TEMPORARILY_UNAVAILABLE = 35  # An IOError errno
__DIR = None


def set_cache_dir(cache_dir):
    """Set the directory to use for holding models and lock files

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


def _pickle_and_cache_models(models):
    pathname = _pathname(__MODELS_FILE)
    try:
        with open(pathname, mode='w') as f:
            pickle.dump(models, f)
    except pickle.PicklingError as e:
        logging.error('pickling data models: {}'.format(e))
        raise
    except IOError as e:
        logging.error('opening {} for writing: {}'.format(pathname, e))
        raise


def set_cached_template_models(models):
    """Update the models from the data models service

    The models are cached on disk. A lock file is used to coordinate
    updates to this cache among threads and processes.

    If another process has the cache locked (only used for writing),
    then this function does nothing; i.e. it assumes that somebody
    else is taking care of the update ....

    Arguments:
        models - object to write to the cache

    Return:
        none
    """
    lock_path = _pathname(__LOCK_FILE)
    try:
        with simpleflock.SimpleFlock(lock_path, timeout=0):
            _pickle_and_cache_models(models)
    except IOError as e:
        if e.errno != __RESOURCE_TEMPORARILY_UNAVAILABLE:
            logging.error('creating lock file {}: {}'.format(lock_path, e))
            raise


def get_cached_template_models():
    """Fetch models from disk cache

    Return: list of models as if returned by get_template_models
    """
    pathname = _pathname(__MODELS_FILE)
    try:
        with open(pathname, mode='r') as f:
            try:
                models = pickle.load(f)
            except pickle.UnpicklingError as e:
                logging.error('unpickling data models: {}'.format(e))
                raise
    except IOError as e:
        logging.error('opening {} for reading: {}'.format(pathname, e))
        raise

    return models
