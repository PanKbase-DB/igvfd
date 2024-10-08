from datetime import datetime
from snovault.schema_validation import NO_DEFAULT
from pyramid.threadlocal import get_current_request
from string import (
    digits,
    ascii_uppercase,
)
import random
import uuid

from snovault.schema_utils import server_default


ACCESSION_FACTORY = __name__ + ':accession_factory'


def includeme(config):
    from pyramid.path import DottedNameResolver
    accession_factory = config.registry.settings.get('accession_factory')
    if accession_factory:
        factory = DottedNameResolver().resolve(accession_factory)
    else:
        factory = prod_accession
    config.registry[ACCESSION_FACTORY] = factory


@server_default
def userid(instance, subschema):
    request = get_current_request()
    principals = request.effective_principals
    for principal in principals:
        if principal.startswith('userid.'):
            return principal[7:]
    return NO_DEFAULT


@server_default
def now(instance, subschema):
    return datetime.utcnow().isoformat() + '+00:00'


@server_default
def uuid4(instance, subschema):
    return str(uuid.uuid4())


@server_default
def accession(instance, subschema):
    if 'external_accession' in instance:
        return NO_DEFAULT
    request = get_current_request()
    factory = request.registry[ACCESSION_FACTORY]
    # With 17 576 000 options
    ATTEMPTS = 10
    for attempt in range(ATTEMPTS):
        new_accession = factory(subschema['accessionType'])
        if new_accession in request.root:
            continue
        return new_accession
    raise AssertionError('Free accession not found in %d attempts' % ATTEMPTS)


PROD_ACCESSION_FORMAT = (
    digits, digits, digits, digits,
    ascii_uppercase, ascii_uppercase, ascii_uppercase, ascii_uppercase
)


def prod_accession(accession_type):
    random_part = ''.join(random.choice(s) for s in PROD_ACCESSION_FORMAT)
    return 'PKB' + accession_type + random_part


TEST_ACCESSION_FORMAT = (digits, ) * 8


def test_accession(accession_type):
    """ Test accessions are generated on test.encodedcc.org
    """
    random_part = ''.join(random.choice(s) for s in TEST_ACCESSION_FORMAT)
    return 'TST' + accession_type + random_part
