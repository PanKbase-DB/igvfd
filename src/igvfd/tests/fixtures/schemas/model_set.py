import pytest


@pytest.fixture
def model_set_no_input(
    testapp,
    award,
    lab,
    software_version
):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'model_name': 'predictive model',
        'model_version': 'v0.0.1',
        'file_set_type': 'neural network',
        'prediction_objects': ['genes'],
        'software_version': software_version['@id']
    }
    return testapp.post_json('/model_set', item, status=201).json['@graph'][0]