import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy_tutorial.items import EpisodeItem

class TDSSpider(BaseSpider):
    name = "tds"
    allowed_domains = ["wikipedia.org"]
    start_urls = []
    for year in range(2003,2014):
        start_urls.append("http://en.wikipedia.org/wiki/List_of_The_Daily_Show_guests_(%s)" % year)

    def parse(self, response):
        year = re.search(r'\((.*)\)', response.url).group(1)
        items = []

        # Find all table rows
        hxs = HtmlXPathSelector(response)
        trs = hxs.select('//tr')
        for tr in trs:
            # If the row has 3 cells, extract the three values and strip html
            if len(tr.select('td')) == 3:
                item = EpisodeItem()
                item['year'] = year
                item['date'] = tr.select('td[1]/text()').extract()[0]
                item['guest_innertexts'] = filter(lambda x: len(x) > 0 and x != ' &amp; ', tr.select('td[2]').re(r'>(.*?)<'))
                item['guest_resources'] = tr.select('td[2]/a/@href').re('wiki/(.*)')
                item['guest_linktexts'] = tr.select('td[2]/a/text()').extract()
                item['promotion'] = ''.join(filter(lambda x: len(x) > 0, tr.select('td[3]').re(r'>(.*?)<')))
                items.append(item)

        return items

class ColbertSpider(BaseSpider):
    name = "colbert"
    allowed_domains = ["wikipedia.org"]
    start_urls = []
    for year in range(2005,2014):
        start_urls.append("http://en.wikipedia.org/wiki/List_of_The_Colbert_Report_episodes_(%s)" % year)

    def parse(self, response):
        year = re.search(r'\((.*)\)', response.url).group(1)
        items = []

        # Find all table rows
        hxs = HtmlXPathSelector(response)
        trs = hxs.select('//tr')
        for tr in trs:

            # Example
            # <th scope="row" id="ep1131" style="text-align: center;background:#F2F2F2;">1131</th>
            # <td class="summary" style="text-align: left;"></td>  # The Word (blank for some years)
            # <td><a href="/wiki/Jimmy_Wales" title="Jimmy Wales">Jimmy Wales</a></td>
            # <td>It's 2013. Suck it Mayans.</td>
            # <td>January 7</td>
            # <td id="pc9039">9039</td>

            # If the row has 5 tds, extract the three values and strip html
            if len(tr.select('td')) == 5:

                # If no episode #, skip
                try:
                    episode_number = tr.select('th[1]/text()').extract()[0].strip()
                except:
                    episode_number = ""

                if len(episode_number) == 0:
                    continue

                item = EpisodeItem()
                item['year'] = year
                item['date'] = tr.select('td[4]/text()').extract()[0]
                item['guest_innertexts'] = filter(lambda x: len(x) > 0 and x != ' &amp; ', [s.replace(', ', '') for s in tr.select('td[2]').re(r'>(.*?)<')])
                item['guest_resources'] = tr.select('td[2]/a/@href').re('wiki/(.*)')
                item['guest_linktexts'] = tr.select('td[2]/a/text()').extract()
                item['promotion'] = ''.join(filter(lambda x: len(x) > 0, tr.select('td[3]').re(r'>(.*?)<')))
                items.append(item)

        return items

class FallonSpider(BaseSpider):
    name = "fallon"
    allowed_domains = ["wikipedia.org"]
    start_urls = ["http://en.wikipedia.org/wiki/List_of_Late_Night_with_Jimmy_Fallon_episodes"]
    for year in range(2009,2012):
        start_urls.append("http://en.wikipedia.org/wiki/List_of_Late_Night_with_Jimmy_Fallon_episodes_(%s)" % year)

    def parse(self, response):
        m = re.search(r'\((.*)\)', response.url)
        if m:
            year = m.group(1)
        else:
            year = "2013"

        items = []

        # Find all table rows
        hxs = HtmlXPathSelector(response)
        trs = hxs.select('//tr')
        for tr in trs:

            # Example:
            #<td>759</td>
            #<td>January 4, 2013</td>
            #<td><a href="/wiki/Bill_Cosby" title="Bill Cosby">Bill Cosby</a>, <a href="/wiki/Tempestt_Bledsoe" title="Tempestt Bledsoe">Tempestt Bledsoe</a></td>
            #<td><a href="/wiki/Grace_Potter_and_the_Nocturnals" title="Grace Potter and the Nocturnals">Grace Potter and the Nocturnals</a></td>

            # If the row has 4 tds, extract the three values and strip html
            if len(tr.select('td')) == 4:
                item = EpisodeItem()
                item['year'] = year
                item['date'] = tr.select('td[2]/text()').extract()[0]
                item['guest_innertexts'] = filter(lambda x: len(x) > 0 and x != ' &amp; ', [s.replace(', ', '') for s in tr.select('td[3]').re(r'>(.*?)<')])
                item['guest_resources'] = tr.select('td[3]/a/@href').re('wiki/(.*)')
                item['guest_linktexts'] = tr.select('td[3]/a/text()').extract()
                item['promotion'] = '' # technically, there's a description in a separate tr spanning all columns, but we're skipping for now
                items.append(item)

        return items
