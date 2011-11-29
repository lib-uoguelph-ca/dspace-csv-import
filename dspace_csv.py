#!/usr/bin/env python

import cgi, csv, os, os.path, re, shutil
from optparse import OptionParser

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


class FileExistsError(Exception): pass


class DCMetadataElement:
    """A DSpace-compatible Dublin Core metadata element.
    """

    def __init__(self, name, value, language=None):
        """Create a new DC element.

        Arguments:
        - `name`: The DC element name, in dotted notation.
        - `value`: The value for the DC element.
        - `language`: An optional two-character ISO language code.
        """
        self.name = name
        self.value = value
        self.language = language

    def _name_components(self):
        """Return a list of name components split on the dots.
        """
        return self.name.split('.')

    def schema(self):
        """Return the item's schema.
        """
        return self._name_components()[0]

    def element(self):
        """Return the item's element.
        """
        return self._name_components()[1]

    def qualifier(self):
        """Return the item's qualifier or None if it does not have one.
        """
        if len(self._name_components()) > 2:
            return self._name_components()[2]

        return None


class DCMetadata:
    """A class representing DSpace-compatible Dublin Core metadata.
    """

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

    @classmethod
    def generate_csv_template(cls, tags=expected_tags):
        """Return a CSV metadata template based on the tags passed in.

        Arguments:
        - `tags`: A dictionary of tag names to tag comments.
        """
        output = StringIO.StringIO()
        writer = csv.writer(output, dialect='excel')

        writer.writerow(['Dublin core element', 'Metadata value', 'Language code', 'Comment'])
        [writer.writerow([tag, '', '', comment]) for tag, comment in sorted(tags.items())]
        output.seek(0)

        return output.read()

    def __init__(self):
        """Create a new Dublin Core object.
        """
        self.data = []

    def __getitem__(self, key):
        """Get a metadata value.

        Arguments:
        - `key`: The metadata key in dotted notation
        """
        return self.data[key]

    def __setitem__(self, key, value):
        """Set a metadata value.

        Arguments:
        - `key`: The metadata key in dotted notation
        - `value`: The new value for the metadata value
        """
        self.data[key] = value

    def append(self, value):
        """Append a new metadata element to this DC object.

        Arguments:
        - `value`: The new value to append.
        """
        self.data.append(value)

    def load_from_csv(self, csv_file):
        """Populate this Dublin Core object from CSV data.

        Arguments:
        - `csv_data`: CSV file representing a Dublin Core object
        """
        reader = csv.reader(open(csv_file, 'r'), dialect='excel')
        reader.next() # Skip the header row
        for record in reader:
            key = record[0]
            value = record[1]
            language = record[2]

            if language == '':
                language = None

            if value != '':
                self.append(DCMetadataElement(key, value, language))

    def to_xml(self):
        """Serialize this Dublin Core object to XML.

        There doesn't appear to be an XML writer built into Python (xml.sax
        is a parser) and I don't want to rely on external libraries like lxml
        so just build the XML with string operations.
        """
        output = ''
        indent = '  '

        for item in self.data:
            attributes = 'element="%s"' % cgi.escape(item.element(), quote=True)

            if item.qualifier():
                attributes += ' qualifier="%s"' % cgi.escape(item.qualifier(), quote=True)

            if item.language:
                attributes += ' language="%s"' % cgi.escape(item.language, quote=True)

            output += '''
%s<dcvalue %s>%s</dcvalue>''' % (indent, attributes, cgi.escape(item.value, quote=True))

        # Wrap our metadata tags in a root tag
        output = '''<dublin_core>%s
</dublin_core>''' % output

        return output


def generate_sample_csv_archive(dir, src=None, item_count=3):
    """Generate a sample DSpace Simple Archive Format tree using CSV metadata.

    Arguments:
    - `dir`: The directory in which to store the archive.
    - `src`: A preformatted CSV metadata sample to be used for each item.
    - `item_count`: The number of item subdirectories to create.
    """
    if os.path.exists(dir):
        raise FileExistsError, dir

    # TODO: Should really try/except here
    os.mkdir(dir)

    for i in range(1, item_count+1):
        item_dir = os.path.join(dir, 'item_%03d' % i)
        os.mkdir(item_dir)
        metadata_file_name = os.path.join(item_dir, 'dublin_core.csv')

        if src is not None:
            shutil.copy(src, metadata_file_name)
        else:
            metadata = open(metadata_file_name, 'w')
            metadata.write(DCMetadata.generate_csv_template())


def clean_archive(dir):
    """Create new XML metadata from existing CSV and create contents manifests.

    Arguments:
    - `dir`: The DSpace Simple Archive Format archive directory
    """
    if not os.path.exists(dir) or not os.path.isdir(dir):
        # TODO: Specify exception
        raise Exception

    item_pattern = re.compile('(:?%s)?item_\d{3}$' % os.sep)

    # Exclude 'contents', 'dublin_core.xml', 'metadata_[prefix].xml', or
    # either metadata name format with a csv extension.
    excluded_files_pattern = re.compile(
        '^(:?(:?dublin_core|metadata_[^.]+)\.(:?csv|xml)|contents)$'
    )

    # Don't need to walk the tree--there should only be the archive directory
    # itself and one level of item subdirectories.
    for f in os.listdir(dir):
        item_dir = os.path.join(dir, f)
        if os.path.isdir(item_dir) and item_pattern.search(item_dir):

            # Generate the contents files
            contents_file_name = os.path.join(item_dir, 'contents')
            if not os.path.exists(contents_file_name):
                contents_file = open(contents_file_name, 'w')

                for f in os.listdir(item_dir):
                    if not excluded_files_pattern.match(f):
                        contents_file.write(f + "\n")

                contents_file.close()

            # Generate XML Dublin Core files from CSV
            csv_file_name = os.path.join(item_dir, 'dublin_core.csv')
            xml_file_name = os.path.join(item_dir, 'dublin_core.xml')
            if os.path.exists(csv_file_name) and not os.path.exists(xml_file_name):
                metadata = DCMetadata()
                metadata.load_from_csv(csv_file_name)

                xml_file = open(xml_file_name, 'w')
                xml_file.write(metadata.to_xml())
                xml_file.close()


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-t', '--generate-template', action='store_true',
                      dest='generate_template', default=False,
                      help='Output a CSV template to STDOUT')
    parser.add_option('-a', '--generate-sample-archive', action='store',
                      dest='archive_name', metavar='DIR',
                      help='Generate a sample archive in DIR')
    parser.add_option('-s', '--source', action='store', default=None,
                      dest='metadata_src', metavar='FILE',
                      help='Use FILE as sample metadata for each item')
    parser.add_option('-c', '--clean-archive', action='store',
                      dest='clean_archive', metavar='DIR',
                      help='Convert CSV to XML and create contents files.')
    parser.add_option('-n', '--number-of-items', action='store', default=3,
                      dest='number_of_items', metavar='NUM', type='int',
                      help='Generate NUM item directories (use with -a).')
    (options, args) = parser.parse_args()


    if options.clean_archive:
        clean_archive(options.clean_archive)
    elif options.archive_name:
        generate_sample_csv_archive(options.archive_name,
                                    src=options.metadata_src,
                                    item_count=options.number_of_items)
    elif options.generate_template:
        print DCMetadata.generate_csv_template()
