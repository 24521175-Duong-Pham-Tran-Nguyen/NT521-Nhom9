"""Recursive JSON value searches with field-level access control."""

from policy import POLICY


def json_search(key, input_object, role=None):
    """Return all accessible values for key in depth-first encounter order.

    Fields absent from POLICY are public. Protected fields require an explicit
    allowed role; callers must supply a role from their authentication layer.
    Inaccessible fields and their subtrees are skipped, including within
    returned containers. Matches retain duplicates, falsey values, and container
    structure. The input is never modified. Input must be acyclic JSON data.
    """
    def can_read(field):
        return field not in POLICY or role in POLICY[field]

    def readable_copy(value):
        if isinstance(value, dict):
            return {
                field: readable_copy(child)
                for field, child in value.items()
                if can_read(field)
            }
        if isinstance(value, list):
            return [readable_copy(child) for child in value]
        return value

    results = []
    if not can_read(key):
        return results

    def search(value):
        if isinstance(value, dict):
            for field, child in value.items():
                if not can_read(field):
                    continue
                if field == key:
                    results.append(readable_copy(child))
                search(child)
        elif isinstance(value, list):
            for child in value:
                search(child)

    search(input_object)
    return results
