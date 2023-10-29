import argparse
import yaml


def handle_properties(properties, spec):
    for prop, kids in properties.items():
        if prop in ['optional', 'type', 'description', 'required']:
            continue

        if prop == 'fileSDConfigs':
            import pudb
            pu.db

        if 'properties' in kids:
            if isinstance(spec, list):
                spec.append(handle_properties(kids['properties'], {}))
            else:
                spec[prop] = handle_properties(kids['properties'], {})
        elif 'items' in kids:
            if isinstance(spec, list):
                if 'properties' in kids['items']:
                    spec.append(handle_properties(kids['items']['properties'], []))
                else:
                    spec.append(handle_properties(kids['items'], {}))
            else:
                spec[prop] = []
                if 'properties' in kids['items']:
                    spec[prop].append(handle_properties(kids['items']['properties'], {}))
                else:
                    spec[prop].append(handle_properties(kids['items'], {}))
        else:
            if isinstance(kids, dict):
                for key, value in kids.items():
                    example = None
                    if key == 'type':
                        if value == 'string':
                            example = f'example_{prop}'
                        elif value == 'integer':
                            example = 1
                        elif value == 'boolean':
                            example = True
                        elif value == 'array':
                            example = []
                        elif value == 'object':
                            continue
                        if len(spec) > 0 and isinstance(next(iter(spec.values())), list):
                            next(iter(spec.values()))[0][prop] = example
                        else:
                            if isinstance(spec, list):
                                if prop not in spec[0]:
                                    spec[0][prop] = example
                            else:
                              spec[prop] = example
            elif isinstance(kids, list):
                spec.append(kids)
            else:
                spec[prop] = kids

    return spec

parser = argparse.ArgumentParser(description='Generate CustomResource with all options from CRD')
parser.add_argument('--crd', dest='crd', required=True, help='Path to CRD file')
args = parser.parse_args()

with open(args.crd, 'r') as f:
    crd = yaml.safe_load(f)

cr = {
    'apiVersion': crd['spec']['group'] + '/' + crd['spec']['versions'][0]['name'],
    'kind': crd['spec']['names']['kind'],
    'metadata': {
        'name': 'example'
    },
    'spec': {}
}

spec = cr['spec']
spec = handle_properties(crd['spec']['versions'][0]['schema']['openAPIV3Schema']['properties']['spec']['properties'], spec)

print(yaml.dump(cr))
