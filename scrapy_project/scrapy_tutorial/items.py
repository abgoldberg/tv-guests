# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class EpisodeItem(Item):
    year = Field()
    date = Field()
    guest_innertexts = Field()
    guest_resources = Field()
    guest_linktexts = Field()
    promotion = Field()

