import cPickle as pickle
import logging
import simpleflock

LOCK_FILE = 'dmsa.models.lockfile'
MODELS_FILE = 'dmsa.models'
RESOURCE_TEMPORARILY_UNAVAILABLE = 35  # An IOError errno


def _pickle_and_cache_models(models):
    try:
        with open(MODELS_FILE, mode='w') as f:
            try:
                pickle.dump(models, f)
            except pickle.PicklingError as e:
                logging.error('pickling data models: {}'.format(e))
                raise
    except IOError as e:
        logging.error('opening {} for writing: {}'.format(MODELS_FILE, e))
        raise


def set_cached_template_models(models):
    """Update the models from the data models service

    The models are cached on disk. A lock file is used to coordinate
    updates to this cache among threads and processes.

    If another process has the cache locked (only used for writing),
    then this function does nothing; i.e. it assumes that somebody
    else is taking care of the update ....

    Arguments:
        models object to write to the cache

    Return:
        none
    """
    try:
        with simpleflock.SimpleFlock(LOCK_FILE, timeout=0):
            _pickle_and_cache_models(models)
    except IOError as e:
        if e.errno != RESOURCE_TEMPORARILY_UNAVAILABLE:
            logging.error('creating lock file {}: {}'.format(LOCK_FILE, e))
            raise


def get_cached_template_models():
    """Fetch models from disk cache

    Arguments: none
    Return: list of models as if returned by get_template_models
    """
    try:
        with open(MODELS_FILE, mode='r') as f:
            try:
                models = pickle.load(f)
            except pickle.UnpicklingError as e:
                logging.error('unpickling data models: {}'.format(e))
                raise
    except IOError as e:
        logging.error('opening {} for reading: {}'.format(MODELS_FILE, e))
        raise

    return models
