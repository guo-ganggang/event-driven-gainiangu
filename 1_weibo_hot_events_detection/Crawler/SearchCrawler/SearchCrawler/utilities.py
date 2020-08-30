def mode_add_one(integer, base):
    """
    increase integer by 1 if it equals base then return 0.
    :param integer:
    :param base:
    :return:
    """
    return (integer + 1) % base


def reset_dict(dict):
    """
    Reset all the dict values to ''
    :param dict:
    :return:
    """
    for key in dict:
        dict[key] = ''

