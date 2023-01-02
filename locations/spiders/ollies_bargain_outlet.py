import scrapy

from locations.dict_parser import DictParser
from locations.hours import OpeningHours


class OlliesBargainOutletSpider(scrapy.Spider):
    name = "ollies_bargain_outlet"
    allowed_domains = ["ollies.us"]
    item_attributes = {"brand": "Ollie's Bargain Outlet", "brand_wikidata": "Q7088304"}
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def start_requests(self):
        url = "https://www.ollies.us/admin/locations/ajax.aspx"
        payload = "Page=0&PageSize=1&StartIndex=0&EndIndex=5&Longitude=-74.006065&Latitude=40.712792&City=&State=&F=GetNearestLocations&RangeInMiles=5000"
        headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}

        yield scrapy.Request(url=url, method="POST", headers=headers, body=payload, callback=self.get_all_locations)

    def get_all_locations(self, response):
        number_locations = response.json().get("LocationsCount")
        url = "https://www.ollies.us/admin/locations/ajax.aspx"
        payload = "Page=0&PageSize={}&StartIndex=0&EndIndex=5&Longitude=-74.006065&Latitude=40.712792&City=&State=&F=GetNearestLocations&RangeInMiles=5000"
        headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}

        yield scrapy.Request(
            url=url, method="POST", headers=headers, body=payload.format(number_locations), callback=self.parse
        )

    def parse(self, response):
        for data in response.json().get("Locations"):
            item = DictParser.parse(data)
            item["country"] = "US"
            item["website"] = f'https://www.{self.allowed_domains[0]}{data.get("CustomUrl")}'

            openHours = data.get("OpenHours").split("<br />")
            openHourFiltered = [row.replace(":", "") for row in openHours if "-" in row]
            oh = OpeningHours()
            oh.from_linked_data({"openingHours": openHourFiltered}, "%I%p")
            item["opening_hours"] = oh.as_opening_hours()

            yield item
