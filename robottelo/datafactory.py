# -*- encoding: utf-8 -*-
"""Data Factory for all entities"""
import random

from functools import wraps
from fauxfactory import gen_string, gen_integer

from robottelo.config import settings
from robottelo.decorators import bz_bug_is_open


class InvalidArgumentError(Exception):
    """Indicates an error when an invalid argument is received."""


def datacheck(func):
    """Overrides the data creator functions in this class to return 1 value

    If run_one_datapoint=false, return the entire data set. (default: False)
    If run_one_datapoint=true, return a random data.

    """
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        """Perform smoke test attribute check"""
        dataset = func(*args, **kwargs)
        if settings.run_one_datapoint:
            dataset = [random.choice(dataset)]
        return dataset
    return func_wrapper


@datacheck
def generate_strings_list(length=None, remove_str=None, bug_id=None):
    """Generates a list of different input strings.

    :param int length: Specifies the length of the strings to be
        be generated. If the len1 is None then the list is
        returned with string types of random length.
    :param str remove_str: Specify any specific data point that needs to be
        removed. Example: remove_str='numeric'.
    :param int bug_id: Specify any bug id that is associated to the datapoint
        specified in remove_str.  This will be used only when remove_str is
        populated.
    :returns: A list of various string types.

    """
    if length is None:
        length = gen_integer(3, 30)
    strings = {
        str_type: gen_string(str_type, length)
        for str_type
        in (u'alpha', u'numeric', u'alphanumeric',
            u'latin1', u'utf8', u'cjk', u'html')
    }
    # Handle No bug_id, If some entity doesn't support a str_type.
    # Remove str_type from dictionary only if bug is open.
    if remove_str and (bug_id is None or bz_bug_is_open(bug_id)):
        del strings[remove_str]
    return list(strings.values())


@datacheck
def invalid_emails_list():
    """Returns a list of invalid emails."""
    return [
        u'foreman@',
        u'@foreman',
        u'@',
        u'Abc.example.com',
        u'A@b@c@example.com',
        u'email@example..c',
        u'{0}@example.com'.format(gen_string('alpha', 49)),  # total length 61
        u'{0}@example.com'.format(gen_string('html')),
        u's p a c e s@example.com',
        u'dot..dot@example.com'
    ]


@datacheck
def invalid_id_list():
    """Generates a list of invalid IDs."""
    return [
        gen_string('alpha'),
        None,
        u'',
        -1,
    ]


@datacheck
def invalid_names_list():
    """Generates a list of invalid names."""
    return [
        gen_string('alphanumeric', 300),
        gen_string('alpha', 300),
        gen_string('cjk', 300),
        gen_string('latin1', 300),
        gen_string('numeric', 300),
        gen_string('utf8', 300),
        gen_string('html', 300),
    ]


@datacheck
def invalid_values_list(interface=None):
    """Generates a list of invalid input values.

    This returns invalid values from :meth:`invalid_names_list` and some
    interface (api/cli/ui) specific empty string values.

    :param str interface: Interface name (one of api/cli/ui).
    :return: Returns the invalid values list
    :raises: :meth:`InvalidArgumentError`: If an invalid interface is received.

    """
    if interface not in ['api', 'cli', 'ui', None]:
        raise InvalidArgumentError(
            'Valid interface values are {0}'.format('api, cli, ui only')
        )
    if interface == 'ui':
        return ['', ' '] + invalid_names_list()
    else:  # interface = api or cli or None
        return ['', ' ', '\t'] + invalid_names_list()


@datacheck
def valid_data_list():
    """Generates a list of valid input values.

    Note:
    Although this helper is widely used for different attributes for several
    entities, the following are known behaviors and are handled specifically in
    the corresponding test modules::

        Org - name max length is 242
        Loc - name max length is 246

    """
    return [
        gen_string('alphanumeric', random.randint(1, 255)),
        gen_string('alpha', random.randint(1, 255)),
        gen_string('cjk', random.randint(1, 85)),
        gen_string('latin1', random.randint(1, 255)),
        gen_string('numeric', random.randint(1, 255)),
        gen_string('utf8', random.randint(1, 85)),
        gen_string('html', random.randint(1, 85)),
    ]


@datacheck
def valid_emails_list():
    """Returns a list of valid emails."""
    return [
        u'{0}@example.com'.format(gen_string('alpha')),
        u'{0}@example.com'.format(gen_string('alphanumeric')),
        u'{0}@example.com'.format(gen_string('numeric')),
        u'{0}@example.com'.format(gen_string('alphanumeric', 48)),
        u'{0}+{1}@example.com'.format(
            gen_string('alphanumeric'),
            gen_string('alphanumeric'),
        ),
        u'{0}.{1}@example.com'.format(
            gen_string('alphanumeric'),
            gen_string('alphanumeric'),
        ),
        u'"():;"@example.com',
        u'!#$%&*+-/=?^`{|}~@example.com',
    ]


@datacheck
def valid_environments_list():
    """Returns a list of valid environment names"""
    return[
        gen_string('alpha'),
        gen_string('numeric'),
        gen_string('alphanumeric'),
    ]


@datacheck
def valid_hosts_list(domain_length=10):
    """Generates a list of valid host names.

    Note::
    Host name format stored in db is 'fqdn=' + host_name + '.' + domain_name
    Host name max length is: 255 - 'fqdn=' - '.' - domain name length
    (default is 10) = 239 chars (by default).

    :param int domain_length: Domain name length (default is 10).
    :return: Returns the valid host names list
    """
    return [
        gen_string(
            'alphanumeric', random.randint(1, (255 - 6 - domain_length))),
        gen_string('alpha', random.randint(1, (255 - 6 - domain_length))),
        gen_string('numeric', random.randint(1, (255 - 6 - domain_length))),
    ]


@datacheck
def valid_hostgroups_list():
    """Generates a list of valid host group names.

    Note::
    Host group name max length is 245 chars.
    220 chars for html as the largest html tag in fauxfactory is 10 chars long,
    so 245 - (10 chars + 10 chars + '<></>' chars) = 220 chars.

    :return: Returns the valid host group names list
    """
    return [
        gen_string('alphanumeric', random.randint(1, 245)),
        gen_string('alpha', random.randint(1, 245)),
        gen_string('cjk', random.randint(1, 245)),
        gen_string('latin1', random.randint(1, 245)),
        gen_string('numeric', random.randint(1, 245)),
        gen_string('utf8', random.randint(1, 245)),
        gen_string('html', random.randint(1, 220)),
    ]


@datacheck
def valid_labels_list():
    """Generates a list of valid labels."""
    return [
        gen_string('alphanumeric', random.randint(1, 128)),
        gen_string('alpha', random.randint(1, 128)),
    ]


@datacheck
def valid_names_list():
    """Generates a list of valid names."""
    return [
        gen_string('utf8', 5),
        gen_string('utf8', 255),
        u"{0}-{1}".format(gen_string('utf8', 4), gen_string('utf8', 4)),
        u"{0}.{1}".format(gen_string('utf8', 4), gen_string('utf8', 4)),
        u"նոր օգտվող-{0}".format(gen_string('utf8', 2)),
        u"新用戶-{0}".format(gen_string('utf8', 2)),
        u"नए उपयोगकर्ता-{0}".format(gen_string('utf8', 2)),
        u"нового пользователя-{0}".format(gen_string('utf8', 2)),
        u"uusi käyttäjä-{0}".format(gen_string('utf8', 2)),
        u"νέος χρήστης-{0}".format(gen_string('utf8', 2)),
        u"foo@!#$^&*( ) {0}".format(gen_string('utf8')),
        u"<blink>{0}</blink>".format(gen_string('utf8')),
        u"bar+{{}}|\"?hi {0}".format(gen_string('utf8')),
        u' {0}'.format(gen_string('utf8')),
        u'{0} '.format(gen_string('utf8')),
    ]


@datacheck
def valid_org_names_list():
    """Generates a list of valid organization names.

    Note::
    Organization name max length is 242 chars.
    217 chars for html as the largest html tag in fauxfactory is 10 chars long,
    so 242 - (10 chars + 10 chars + '<></>' chars) = 217 chars.

    :return: Returns the valid organization names list
    """
    return [
        gen_string('alphanumeric', random.randint(1, 242)),
        gen_string('alpha', random.randint(1, 242)),
        gen_string('cjk', random.randint(1, 242)),
        gen_string('latin1', random.randint(1, 242)),
        gen_string('numeric', random.randint(1, 242)),
        gen_string('utf8', random.randint(1, 80)),
        gen_string('html', random.randint(1, 217)),
    ]


@datacheck
def valid_usernames_list():
    """Returns a list of valid user names.

    Note: utf8 data is being rejected by the satellite server so it is not
    included

    """
    return [
        gen_string("latin1"),
        gen_string("alpha"),
        gen_string("alphanumeric"),
        gen_string("numeric"),
    ]
