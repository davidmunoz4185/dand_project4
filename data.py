#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re
import csv
import codecs
import pprint
import schema
import cerberus
import xml.etree.cElementTree as ET


import audit as au


NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"
OSM_PATH = "bronxtoles.osm"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

"""
Make sure the fields order in the csvs matches
the column order in the sql table schema
"""
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid',
               'version', 'changeset', 'timestamp']
node_default = {
    'id': 0,
    'lat': 0.0,
    'lon': 0.0,
    'user': 'default',
    'uid': 0,
    'version': '0',
    'changeset': 0,
    'timestamp': '2000-01-01T00:00:00Z'
}
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS,
                  way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS,
                  default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == 'node':
        for n_field in NODE_FIELDS:
            if n_field not in element.attrib:
                    node_attribs[n_field] = node_default[n_field]
            else:
                node_attribs[n_field] = element.attrib[n_field]

        for tag in element.iter("tag"):
            d_tags = {}
            d_tags["id"] = element.attrib["id"]
            d_tags["key"] = tag.attrib["k"]
            d_tags["value"] = tag.attrib["v"]
            d_tags["type"] = "regular"

            if LOWER_COLON.search(tag.attrib['k']):
                d_tags["key"] = ':'.join(tag.attrib['k'].split(":")[1:])
                d_tags["type"] = tag.attrib['k'].split(":")[0]

            if d_tags["key"] == "tipo_via":
                d_tags["value"] = au.treat_tipo_via(d_tags["value"])

            if d_tags["key"] in ["postal_code", "postcode"]:
                d_tags["value"] = au.treat_postcode(d_tags["value"])

            tags.append(d_tags)
        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        for n_field in WAY_FIELDS:
            way_attribs[n_field] = element.attrib[n_field]
        position = 0
        for pos in element.iter("nd"):
            pos_d = {}
            pos_d["id"] = element.attrib["id"]
            pos_d["node_id"] = pos.attrib["ref"]
            pos_d["position"] = position
            position = position + 1
            way_nodes.append(pos_d)

        for tag in element.iter("tag"):
            tag_d = {}
            tag_d["id"] = element.attrib["id"]
            tag_d["key"] = tag.attrib["k"]
            tag_d["value"] = tag.attrib["v"]
            tag_d["type"] = "regular"

            if LOWER_COLON.search(tag.attrib['k']):
                tag_d["key"] = ':'.join(tag.attrib['k'].split(":")[1:])
                tag_d["type"] = tag.attrib['k'].split(":")[0]

            if tag_d["key"] == "tipo_via":
                tag_d["value"] = au.treat_tipo_via(tag_d["value"])

            if tag_d["key"] in ["postal_code", "postcode"]:
                tag_d["value"] = au.treat_postcode(tag_d["value"])

            tags.append(tag_d)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}'"
        message_string = message_string + "has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, 
                unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)
