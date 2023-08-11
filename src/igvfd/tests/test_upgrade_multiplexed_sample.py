import pytest


def test_multiplexed_sample_upgrade_1_2(upgrader, multiplexed_sample_v1):
    value = upgrader.upgrade('multiplexed_sample', multiplexed_sample_v1, current_version='1', target_version='2')
    assert 'source' not in value
    assert 'product_id' not in value
    assert 'lot_id' not in value
    assert value['notes'] == 'Source /sources/sigma/ was removed via upgrade. Product ID ab272168 was removed via upgrade. Lot ID 0000001 was removed via upgrade.'
    assert value['schema_version'] == '2'


def test_multiplexed_sample_upgrade_2_3(upgrader, multiplexed_sample_v2):
    value = upgrader.upgrade('multiplexed_sample', multiplexed_sample_v2, current_version='2', target_version='3')
    assert value['schema_version'] == '3'