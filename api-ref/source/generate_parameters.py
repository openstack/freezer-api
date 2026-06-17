# Copyright 2026, Cleura AB
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import yaml


def resolve(s, definitions):
    if isinstance(s, dict) and '$ref' in s:
        ref = s['$ref']
        if ref.startswith('#/definitions/'):
            def_name = ref.split('/')[-1]
            resolved = definitions.get(def_name)
            if resolved:
                return resolve(resolved, definitions)
    return s


def get_schema_type(s):
    t = s.get(
        'type',
        'object' if 'properties' in s
        else ('array' if 'items' in s else 'any')
    )
    if isinstance(t, list):
        t = next((x for x in t if x != 'null'), 'string')
    return str(t)


def get_nested_properties(schema, definitions, prefix="",
                          required_fields=None):
    props = {}
    schema = resolve(schema, definitions)
    if not isinstance(schema, dict) or 'properties' not in schema:
        return props

    req = required_fields or schema.get('required', [])
    for prop, prop_schema in schema['properties'].items():
        prop_name = f"{prefix}.{prop}" if prefix else prop
        is_req = prop in req
        ref_schema = resolve(prop_schema, definitions)
        prop_type = get_schema_type(ref_schema)

        nested_schema = None
        if prop_type == 'array':
            item_schema = resolve(ref_schema.get('items', {}), definitions)
            item_type = get_schema_type(item_schema)
            if item_type == 'object':
                meta_type = 'array'
                fallback_desc = f"A list of {prop} objects."
                nested_schema = item_schema
            else:
                meta_type = f"array of {item_type}s"
                fallback_desc = f"A list of {prop} values."
        elif prop_type == 'object':
            meta_type = 'dict'
            fallback_desc = f"The {prop} dictionary."
            nested_schema = ref_schema
        else:
            meta_type = prop_type
            fallback_desc = f"The {prop} property."

        enum_vals = ref_schema.get('enum')
        if prop_type == 'array':
            item_schema = resolve(ref_schema.get('items', {}), definitions)
            enum_vals = item_schema.get('enum')

        desc = ref_schema.get('description', fallback_desc)
        if enum_vals:
            valid_vals = [v for v in enum_vals if v not in (None, "")]
            if valid_vals:
                enum_str = ", ".join(f"``{val}``" for val in valid_vals)
                if "one of:" not in desc.lower():
                    if "e.g." not in desc.lower():
                        desc = f"{desc.rstrip('.')} (one of: {enum_str})."

        props[prop_name] = {
            'type': meta_type,
            'in': 'body',
            'required': is_req,
            'description': desc
        }
        if nested_schema:
            props.update(get_nested_properties(nested_schema,
                                               definitions,
                                               prop_name))
    return props


def generate_parameters_yaml():
    try:
        from freezer_api.common import json_schemas
    except ImportError:
        return

    schemas_to_doc = [
        ("jobs", json_schemas.job_schema),
        ("actions", json_schemas.action_schema),
        ("sessions", json_schemas.session_schema),
        ("clients", json_schemas.client_schema)
    ]

    generated_props = {}
    for name, schema in schemas_to_doc:
        definitions = schema.get('definitions', {})
        props = get_nested_properties(schema, definitions,
                                      required_fields=schema.get('required'))
        for prop_name, prop_meta in props.items():
            top_level_to_skip = {
                'client_id',
                'description',
                'session_id',
                'user_id',
                'project_id',
                'action_id'
            }
            if prop_name in top_level_to_skip:
                continue
            generated_props[prop_name] = prop_meta

    # Explicitly add freezer_action nested properties for Actions API
    freezer_action_props = get_nested_properties(
        {"properties": json_schemas.freezer_action_properties}, {},
        prefix="freezer_action"
    )
    for prop_name, prop_meta in freezer_action_props.items():
        generated_props[prop_name] = prop_meta

    script_dir = os.path.dirname(os.path.abspath(__file__))
    manual_path = os.path.join(script_dir, 'v2', 'parameters-manual.yaml')
    yaml_path = os.path.join(script_dir, 'v2', 'parameters.yaml')

    existing_yaml = {}
    if os.path.exists(manual_path):
        with open(manual_path, 'r') as f:
            try:
                existing_yaml = yaml.safe_load(f) or {}
            except Exception:
                existing_yaml = {}

    for prop_name, prop_meta in generated_props.items():
        existing_yaml[prop_name] = prop_meta

    order = {'path': 0, 'query': 1, 'header': 2, 'body': 3}
    sorted_yaml = dict(sorted(
        existing_yaml.items(),
        key=lambda item: (order.get(item[1].get('in', 'body'), 3), item[0])
    ))

    with open(yaml_path, 'w') as f:
        yaml.safe_dump(
            sorted_yaml, f, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    generate_parameters_yaml()
