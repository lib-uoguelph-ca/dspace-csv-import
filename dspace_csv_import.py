#!/usr/bin/env python

import csv, os, os.path, re
from optparse import OptionParser

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


class FileExistsError(Exception): pass


class DublinCoreDspaceMetadata:
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

        writer.writerow(['Dublin core element', 'Metadata value', 'Comment'])
        [writer.writerow([tag, '', comment]) for tag, comment in tags.items()]
        output.seek(0)

        return output.read()


def generate_sample_csv_archive(dir, item_count=3):
    """Generate a sample DSpace Simple Archive Format tree using CSV metadata.

    Arguments:
    - `dir`: The directory in which to store the archive.
    """
    if os.path.exists(dir):
        raise FileExistsError, dir

    # TODO: Should really try/except here
    os.mkdir(dir)

    for i in range(1, item_count+1):
        item_dir = os.path.join(dir, 'item_%03d' % i)
        os.mkdir(item_dir)
        metadata = open(os.path.join(item_dir, 'dublin_core.csv'), 'w')
        metadata.write(DublinCoreDspaceMetadata.generate_csv_template())


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


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-t', '--generate-template', action='store_true',
                      dest='generate_template', default=False,
                      help='Output a CSV template to STDOUT')
    parser.add_option('-a', '--generate-sample-archive', action='store',
                      dest='archive_name', metavar='DIR',
                      help='Generate a sample archive in DIR')
    parser.add_option('-c', '--clean-archive', action='store',
                      dest='clean_archive', metavar='DIR',
                      help='Convert CSV to XML and create contents files.')
    (options, args) = parser.parse_args()


    if options.clean_archive:
        clean_archive(options.clean_archive)
    elif options.archive_name:
        generate_sample_csv_archive(options.archive_name)
    elif options.generate_template:
        print DublinCoreDspaceMetadata.generate_csv_template()
