tv-guests
=========

Code and data for experimenting with and analyzing tv guest appearances on late-night comedy shows.

Dependencies
------------
* scrapy python package
* rdflib python package
* wikipedia python package

Crawling
--------

Here's an example of how to crawl wikipedia for episode data.

Possible spider names are: tds, colbert, fallon

    cd scrapy_tutorial
    scrapy crawl name -o name_items.json -t json
