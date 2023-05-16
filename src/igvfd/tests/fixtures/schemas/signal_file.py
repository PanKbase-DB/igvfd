import pytest


@pytest.fixture
def signal_file(testapp, lab, award, analysis_set_with_sample, reference_file):
    item = {
        'award': award['@id'],
        'lab': lab['@id'],
        'md5sum': '350e99db0738e1987d3d6b53c22c3937',
        'file_format': 'bigWig',
        'file_set': analysis_set_with_sample['@id'],
        'file_size': 4328491803,
        'content_type': 'signal of all reads',
        'reference_files': [
            reference_file['@id']
        ],
        'strand_specificity': 'plus',
        'normalized': False,
        'filtered': False
    }
    return testapp.post_json('/signal_file', item, status=201).json['@graph'][0]