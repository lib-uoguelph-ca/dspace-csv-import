#!/usr/bin/env python

import csv
from optparse import OptionParser

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


# Dublin core tags to be put into generated templates
expected_tags = {
    'dc.contributor': None,
    'dc.contributor.affiliation': None,
    'dc.contributor.author': None,
    'dc.contributor.editor': None,
    'dc.contributor.other': None,
    'dc.coverage.spatial': None,
    'dc.date.copyright': None,
    'dc.date.created': None,
    'dc.date.issued': None,
    'dc.description.abstract': None,
    'dc.description.provenance': None,
    'dc.description.sponsorship': None,
    'dc.description.version': None,
    'dc.format.medium': None,
    'dc.identifier.citation': None,
    'dc.identifier.isbn': None,
    'dc.identifier.issn': None,
    'dc.language.iso': None,
    'dc.publisher': None,
    'dc.relation.ispartofseries': None,
    'dc.rights': None,
    'dc.rights.holder': None,
    'dc.subject': None,
    'dc.submitter.submitter': None,
    'dc.title': None,
    'dc.type': None
}


def generate_csv_template(tags):
    """Return a CSV metadata template based on the tags passed in.
    
    Arguments:
    - `tags`: A dictionary of tag names to tag comments.
    """
    output = StringIO.StringIO()
    writer = csv.writer(output, dialect='excel')

    writer.writerow(['Dublin core element', 'Metadata value', 'Comment'])
    [writer.writerow([tag, '', comment]) for tag, comment in tags.items()]
    output.seek(0)

    return output.read()


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-t', '--generate-template', action='store_true',
                      dest='generate_template', default=False,
                      help='Output a CSV template to STDOUT')
    (options, args) = parser.parse_args()


    if options.generate_template:
        print generate_csv_template(expected_tags)
