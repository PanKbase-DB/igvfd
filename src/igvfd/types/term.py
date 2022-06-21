from snovault import (
    calculated_property,
    abstract_collection,
    collection,
    load_schema,
)

from .base import (
    Item,
)


@abstract_collection(
    name='terms',
    unique_key='term_id',
    properties={
        'title': 'Ontology term',
        'description': 'Ontology terms used by IGVF',
    })
class Term(Item):
    base_types = ['Term'] + Item.base_types
    schema = load_schema('igvfd:schemas/term.json')

    @staticmethod
    def _get_ontology_slims(registry, term_id, slim_key):
        if term_id not in registry['ontology']:
            return []
        key = registry['ontology'][term_id].get(slim_key, [])
        return list(set(
            slim for slim in key
        ))

    @calculated_property(condition='term_id', schema={
        'title': 'Synonyms',
        'type': 'array',
        'items': {
            'type': 'string',
        },
    })
    def synonyms(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'synonyms')


@collection(
    name='sample-terms',
    unique_key='term_id',
    properties={
        'title': 'Sample ontology term',
        'description': 'Ontology terms used by IGVF for samples',
    })
class SampleTerm(Term):
    item_type = 'sample_term'
    schema = load_schema('igvfd:schemas/sample_term.json')

    @calculated_property(condition='term_id', schema={
        'title': 'Organ',
        'type': 'array',
        'items': {
            'type': 'string',
        },
    })
    def organ_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'organs')

    @calculated_property(condition='term_id', schema={
        'title': 'Cell',
        'type': 'array',
        'items': {
            'type': 'string',
        },
    })
    def cell_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'cells')

    @calculated_property(condition='term_id', schema={
        'title': 'Developmental slims',
        'type': 'array',
        'items': {
            'type': 'string',
        },
    })
    def developmental_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'developmental')

    @calculated_property(condition='term_id', schema={
        'title': 'System slims',
        'type': 'array',
        'items': {
            'type': 'string',
        },
    })
    def system_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'systems')


@collection(
    name='assay-terms',
    unique_key='term_id',
    properties={
        'title': 'Assay ontology term',
        'description': 'Ontology terms used by IGVF for assays',
    })
class AssayTerm(Term):
    item_type = 'assay_term'
    schema = load_schema('igvfd:schemas/assay_term.json')

    @calculated_property(condition='term_id', schema={
        'title': 'Assay category',
        'type': 'array',
        'items': {
            'type': 'string',
        },
    })
    def category_slims(self, registry, term_id):
        return self._get_ontology_slims(registry, term_id, 'assay')


@collection(
    name='phenotype-terms',
    unique_key='term_id',
    properties={
        'title': 'Phenotype ontology term',
        'description': 'Ontology terms used by IGVF for phenotypes, such as traits or diseases.',
    })
class PhenotypeTerm(Term):
    item_type = 'phenotype_term'
    schema = load_schema('igvfd:schemas/phenotype_term.json')