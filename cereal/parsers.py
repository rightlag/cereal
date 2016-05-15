import json
import re

from collections import OrderedDict
from meta import ProtocolMeta


class Protobuf(ProtocolMeta):
    def __init__(self, filepath):
        super(Protobuf, self).__init__(filepath)

    def to_avro(self, indent=4):
        """Convert a Google Protocol Buffer file to an Apache Avro file."""
        schemas = []
        with open(self._filepath) as fp:
            lines = fp.readlines()
            prog = re.compile(r'^message\s(\w+)\s\{$')
            for i in range(len(lines)):
                line = lines[i].strip()
                match = prog.match(line)
                if match is None:
                    continue
                record = OrderedDict()
                record['type'] = 'record'
                # Google Protocol Buffer message name.
                record['name'] = match.group(1)
                record['fields'] = []
                j = i
                while True:
                    # Increment `j` by 1 to ignore the `message` line
                    # itself.
                    j += 1
                    line = lines[j].strip()
                    if line.endswith('}'):
                        break
                    if line == '':
                        continue
                    field = line.split()
                    t, identifier = field[:2]
                    try:
                        t = Avro.TYPES[t]
                    except KeyError:
                        continue
                    record['fields'].append({
                        'name': identifier,
                        'type': t,
                    })
                schemas.append(record)
        return json.dumps(schemas, indent=indent)


class Avro(ProtocolMeta):
    TYPES = {
        'double': 'double',
        'float': 'float',
        'int32': 'int',
        'int64': 'long',
        'uint32': 'int',
        'uint64': 'long',
        'sint32': 'int',
        'sint64': 'long',
        'fixed32': 'int',
        'fixed64': 'long',
        'sfixed32': 'int',
        'sfixed64': 'long',
        'bool': 'boolean',
        'string': 'String',
        'bytes': 'ByteString',
    }

    REVERSED = dict({(v, k) for (k, v) in TYPES.iteritems()})

    def __init__(self, filepath):
        super(Avro, self).__init__(filepath)

    def to_protobuf(self, indent=4):
        lines = ''
        with open(self._filepath) as fp:
            records = json.loads(fp.read())
            for i in range(len(records)):
                if i != 0:
                    lines += '\n'
                lines += 'message {}'.format(records[i]['name'])
                lines += ' {\n'
                fields = records[i]['fields']
                for i in range(len(fields)):
                    lines += ' ' * indent + '{} {} = {};\n'.format(
                        self.REVERSED[fields[i]['type']],
                        fields[i]['name'],
                        i + 1,
                    )
                lines += '}\n'
        return lines