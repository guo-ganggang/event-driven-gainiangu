def loop_increase(integer, base):
    """
    increase integer by 1 if it exceeds base then reset integer
    :param integer:
    :param base:
    :return:
    """
    return (integer + 1) % base


def reset_dict(dict):

    for key in dict:
        dict[key] = ''


def test_exception(func):
    """
    Try to test exception on one certain function
    :param func:
    :return:
    """

    def _test_eception(*args, **keyargs):
        try:
            return func(*args, **keyargs)
        except Exception as e:
            print e
            print 'Error execute: %s' % func.__name__

    return _test_eception




