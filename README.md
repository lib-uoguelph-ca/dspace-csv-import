# DSpace CSV import tools

DSpace allows for items to be imported in bulk using a format called DSpace
Simple Archive Format. The format boils down to a directory structure and a
metadata XML format.

Unfortunately, the DSpace Simple Archive Format is not ideal for passing on
to end users. The main reason for this is that end users are often not
comforable creating or editing XML documents.

At the University of Guelph we have developed a small script to facilitate
metadata generation in CSV format which can be created or edited in Excel, a
tool with which many users are comfortable.

## Generate a sample CSV file

A sample, empty CSV file can be printed to STDOUT

    ./dspace_csv.py -t

To save this to a file just use a standard redirect

    ./dspace_csv.py -t > sample.csv

This can be useful for sending to a user and requesting that they fill it in
with default metadata that will apply to the whole import. `dc.language.iso`
would be an excellent candidate to fill in at this time.

Anything that is set at this stage can be overridden on a per-item basis, so
if you have something like 500 English items an 12 French items it is still
worth doing.

## Generate an empty archive structure

A sample archive structure can be generated with something like

    ./dspace_csv.py -a [directory-name]

but you will probably want to include the `-n` and `-s` options too:

    ./dspace_csv.py -a [directory-name] -n [number-of-items] -s [sample-csv-file-from-above]

The `-n` option specifies the number of `item_` subdirectories to create. The
current maximum for this process is 1000 items per import, but this might
increase in the future.

The `-s` option provides the name of a CSV file to be used as a starting
point for each item. Typically you would want to use a file generated using
the `-t` option as shown above that has been modified by the end user.

By automating the directory creation and copying of the initial CSV file we
can save a lot of time. There will also be a file called `README.html` in the
directory root containing some basic instructions for the end user.

### Zip up the empty archive

Create a zip file containing the archive with something like

    zip -r archive.zip directory-name

and send it to the end user. Direct them to unzip the file and refer to the
`README.html` file.

## Clean up the returned archive

After the end user has updated the metadata files and copied the item files
they should have zipped it back up and sent it to you.

First, unzip the directory with

    unzip archive.zip

It is probably a good idea to eyeball the CSV data on some items at this
point. Once you are satisfied that the data is sound, run the cleanup script
on the directory.

    ./dspace_csv.py -c [directory-name]

This does two things:

It parses the CSV metadata files and generates matching XML metadata files
that DSpace can understand. The existing CSV files are not modified or deleted.

It generates `contents` files inside each item subdirectory listing the files
that should be imported, as required by DSpace. It assumes that any files
inside the item directory that aren't named `dublin_core.csv`,
`dublin_core.xml`, `metadata_[anything].csv`, `metadata_[anything].xml` or
`contents` should be included.

If you want more control over the XML metadata or the `contents` file itself
you can create them manually. It is safe to run the clean script on a
directory containing these files: if they exist they will not be overwritten.

## Import into DSpace

Once the clean script has been successfully run the archive directory should
be ready for DSpace to import it. Something like

    [dspace]/bin/import --add --eperson=[importer's email address] --collection=[collection handle] --source=[directory-name] --mapfile=[directory-name]/mapfile

will add the items in the directory to the requested collection. Please refer
to the
[DSpace documentation](http://www.dspace.org/1_6_0Documentation/ch08.html#N1584C)
for more information about the DSpace Simple Archive Format or the
import/export commands.

The `--mapfile` argument is particularly important, and the file that gets
generated should be kept along with the rest of the source directory. This
file is required for deleting or modifying the imported files using the
command-line tools.
