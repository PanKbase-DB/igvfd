from snovault.auditor import (
    audit_checker,
    AuditFailure,
)
from .formatter import (
    audit_link,
    path_to_text,
    get_audit_description
)

@audit_checker('HumanDonor', frame='object')
def audit_desired_fields(value, system):
    """
    {
        "audit_description": "Checks if desired fields are present and issues a warning if any are missing.",
        "audit_category": "missing desired field",
        "audit_level": "WARNING"
    }
    """
    description = get_audit_description(audit_desired_fields)
    desired_fields = [
        "center_donor_id",
        "ethnicities",
        "hba1c",
        "diabetes_status_hba1c",
        "glucose_loweing_theraphy",
        "hospital_stay",
        "donation_type",
        "cause_of_death"
    ]
    missing_fields = [field for field in desired_fields if field not in value]

    if missing_fields:
        for field in missing_fields:
            detail = (
                f'Human donor {audit_link(path_to_text(value["@id"]), value["@id"])} is missing the desired field `{field}`.'
            )
            yield AuditFailure('missing desired field', f'{detail} {description}', level='WARNING')
@audit_checker('AnalysisSet', frame='object')
def audit_related_donors(value, system):
    '''
    [
        {
            "audit_description": "The human donors indicated in the list of related donors are expected to be unique.",
            "audit_category": "inconsistent related donors",
            "audit_level": "WARNING"
        },
        {
            "audit_description": "The human donors indicated in the list of related donors are expected to include a mutual link to the corresponding donor.",
            "audit_category": "inconsistent related donors",
            "audit_level": "ERROR"
        }
    ]
    '''
    description_unique = get_audit_description(audit_related_donors)
    description_mutual = get_audit_description(audit_related_donors, index=1)
    if 'related_donors' in value:
        for unique_related_donor in set([related_donor['donor'] for related_donor in value['related_donors']]):
            if [related_donor['donor'] for related_donor in value['related_donors']].count(unique_related_donor) > 1:
                detail = (
                    f'Human donor {audit_link(path_to_text(value["@id"]), value["@id"])} '
                    f'has a duplicated related donor {audit_link(path_to_text(unique_related_donor), unique_related_donor)} in `related_donors`.'
                )
                yield AuditFailure('inconsistent related donors', f'{detail} {description_unique}', level='WARNING')
            related_donor_object = system.get('request').embed(unique_related_donor, '@@object?skip_calculated=true')
            if 'related_donors' not in related_donor_object or value['@id'] not in [related_donor['donor'] for related_donor in related_donor_object['related_donors']]:
                detail = (
                    f'Human donor {audit_link(path_to_text(value["@id"]), value["@id"])} '
                    f'has {audit_link(path_to_text(unique_related_donor), unique_related_donor)} '
                    f'as a related donor, but {audit_link(path_to_text(unique_related_donor), unique_related_donor)} '
                    f'does not mutually specify {audit_link(path_to_text(value["@id"]), value["@id"])} as a related donor in `related_donors`.'
                )
                yield AuditFailure('inconsistent related donors', f'{detail} {description_mutual}', level='ERROR')
