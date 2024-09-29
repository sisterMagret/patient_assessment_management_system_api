# coding=utf-8
import json
from glob import glob
from os.path import dirname, isfile, realpath


class Countries:
    """To access one of the country properties available

    Example:
        country = CountryInfo('singapore')
        pprint(country.info())
    """

    def __init__(self, country_name=None):
        """constructor method

        :param country_name: str
            pass country name
        """
        self.__country_name = country_name.lower() if country_name else ""
        # get the files path
        __file_dir_path = dirname(realpath(__file__))
        __country_files = __file_dir_path + "/data/"
        __files_path = [
            files for files in glob(__country_files + "*.json")
        ]
        self.__countries = {}
        for file_path in __files_path:
            if isfile(file_path):
                country_info = json.load(open(file_path, encoding="utf-8"))
                # pprint(country_info)
                if country_info.get("name", None):
                    self.__countries[country_info["name"].lower()] = (
                        country_info
                    )

    def info(self):
        """Returns all available information for a specified country.

        :return: dict
        """
        if self.__country_name:
            _all = self.__countries[self.__country_name]
            # pprint(_all)

            return _all

    def provinces(self):
        """return provinces list

        :return: list
        """
        if self.__country_name:
            _provinces = self.__countries[self.__country_name]["provinces"]
            # pprint(_provinces)

            return _provinces

    def iso(self, alpha=None):
        """Returns ISO codes for a specified country

        :param alpha: int

        :return: dict or str
            based on param
        """
        if self.__country_name:
            _iso = self.__countries[self.__country_name]["ISO"]
            # pprint(_iso)

            if alpha == 2:
                return _iso["alpha2"]
            elif alpha == 3:
                return _iso["alpha3"]

            return _iso

    def alt_spellings(self):
        """Returns alternate spellings for the name of a specified country

        :return: list
        """
        if self.__country_name:
            _alt_spellings = self.__countries[self.__country_name][
                "altSpellings"
            ]
            # pprint(_alt_spellings)

            return _alt_spellings

    def area(self):
        """Returns area (km²) for a specified country

        :return: int
        """
        if self.__country_name:
            _area = self.__countries[self.__country_name]["area"]
            # pprint(_area)

            return _area

    def borders(self):
        """Returns bordering countries (ISO3) for a specified country

        :return: list
        """
        if self.__country_name:
            _borders = self.__countries[self.__country_name]["borders"]
            # pprint(_borders)

            return _borders

    def calling_codes(self):
        """Returns international calling codes for a specified country

        :return: list
        """
        if self.__country_name:
            _calling_codes = self.__countries[self.__country_name][
                "callingCodes"
            ]
            # pprint(_calling_codes)

            return _calling_codes

    def capital(self):
        """Returns capital city for a specified country

        :return: str
        """
        if self.__country_name:
            _capital = self.__countries[self.__country_name]["capital"]
            # pprint(_capital)

            return _capital

    def currencies(self):
        """Returns official currencies for a specified country

        :return: list
        """
        if self.__country_name:
            _currencies = self.__countries[self.__country_name][
                "currencies"
            ]
            # pprint(_currencies)

            return _currencies

    def demonym(self):
        """Returns the demonyms for a specified country

        :return: str
        """
        if self.__country_name:
            _demonym = self.__countries[self.__country_name]["demonym"]
            # pprint(_demonym)

            return _demonym

    def flag(self):
        """Returns SVG link of the official flag for a specified country

        :return: str
            it will return an URL if available
        """
        if self.__country_name:
            _flag = self.__countries[self.__country_name]["flag"]
            # pprint(_flag)

            return _flag

    def geo_json(self):
        """Returns geoJSON for a specified country

        :return: dict
        """
        if self.__country_name:
            _geo_json = self.__countries[self.__country_name]["geoJSON"]
            # pprint(_geo_json)

            return _geo_json

    def languages(self):
        """Returns official languages for a specified country

        :return: list
        """
        if self.__country_name:
            _languages = self.__countries[self.__country_name]["languages"]
            # pprint(_languages)

            return _languages

    def latlng(self):
        """Returns approx latitude and longitude for a specified country

        :return: list
        """
        if self.__country_name:
            _latlng = self.__countries[self.__country_name]["latlng"]
            # pprint(_latlng)

            return _latlng

    def native_name(self):
        """Returns the name of the country in its native tongue

        :return: str
        """
        if self.__country_name:
            _native_name = self.__countries[self.__country_name][
                "nativeName"
            ]
            # pprint(_native_name)

            return _native_name

    def population(self):
        """Returns approximate population for a specified country

        :return: int
        """
        if self.__country_name:
            _population = self.__countries[self.__country_name][
                "population"
            ]
            # pprint(_population)

            return _population

    def region(self):
        """Returns general region for a specified country

        :return: str
        """
        if self.__country_name:
            _region = self.__countries[self.__country_name]["region"]
            # pprint(_region)

            return _region

    def subregion(self):
        """Returns a more specific region for a specified country

        :return: str
        """
        if self.__country_name:
            _subregion = self.__countries[self.__country_name]["subregion"]
            # pprint(_subregion)

            return _subregion

    def timezones(self):
        """Returns all timezones for a specified country

        :return: list
        """
        if self.__country_name:
            _timezones = self.__countries[self.__country_name]["timezones"]
            # pprint(_timezones)

            return _timezones

    def tld(self):
        """Returns official top level domains for a specified country

        :return: list
        """
        if self.__country_name:
            _tld = self.__countries[self.__country_name]["tld"]
            # pprint(_tld)

            return _tld

    def translations(self):
        """Returns translations for a specified country name in popular languages

        :return: dict
        """
        if self.__country_name:
            _translations = self.__countries[self.__country_name][
                "translations"
            ]
            # pprint(_translations)

            return _translations

    def wiki(self):
        """Returns link to wikipedia page for a specified country

        :return: str
            return wiki url if available
        """
        if self.__country_name:
            _wiki = self.__countries[self.__country_name]["wiki"]
            # pprint(_wiki)

            return _wiki

    def all(self):
        """return all of the countries information

        :return: dict
        """
        _all = self.__countries
        # pprint(_all)

        return _all


"""
COUNTRY CODES TUPLES
"""
country_codes: tuple = (
    ("93", " Afghanistan (93)"),
    ("355", "Albania (355)"),
    ("213", "Algeria (213)"),
    ("1-684", "American Samoa (1-684)"),
    ("376", "Andorra (376)"),
    ("244", "Angola (244)"),
    ("1-264", "Anguilla (1-264)"),
    # ('672', 'Antarctica (672)'),
    # ('1-268', 'Antigua (1-268)'),
    # ('1-268', 'Barbuda (1-268)'),
    ("54", "Argentina (54)"),
    ("374", "Armenia (374)"),
    ("297", "Aruba (297)"),
    ("61", "Australia (61)"),
    ("43", "Austria (43)"),
    ("994", "Azerbaijan (994)"),
    # ('1-242', 'Bahamas (1-242)'),
    ("973", "Bahrain (973)"),
    ("880", "Bangladesh (880)"),
    ("1-246", "Barbados (1-246)"),
    ("375", "Belarus (375)"),
    ("32", "Belgium (32)"),
    ("501", "Belize (501)"),
    ("229", "Benin (229)"),
    ("1-441", "Bermuda (1-441)"),
    ("975", "Bhutan (975)"),
    ("591", "Bolivia (591)"),
    ("387", "Bosnia (387)"),
    ("267", "Botswana (267)"),
    ("55", "Brazil (55)"),
    ("246", "British Indian Ocean Territory (246)"),
    ("1-284", "British Virgin Islands (1-284)"),
    ("673", "Brunei (673)"),
    ("359", "Bulgaria (359)"),
    ("226", "Burkina Faso (226)"),
    ("257", "Burundi (257)"),
    ("1-649", "Caicos Islands (1-649)"),
    ("855", "Cambodia (855)"),
    ("237", "Cameroon (237)"),
    ("1", "Canada (1)"),
    ("238", "Cape Verde (238)"),
    ("1-345", "Cayman Islands (1-345)"),
    ("236", "Central African Republic (236)"),
    ("235", "Chad (235)"),
    ("56", "Chile (56)"),
    ("86", "China (86)"),
    ("61", "Christmas Island (61)"),
    ("61", "Cocos Islands (61)"),
    ("57", "Colombia (57)"),
    ("269", "Comoros (269)"),
    ("682", "Cook Islands (682)"),
    ("506", "Costa Rica (506)"),
    ("385", "Croatia (385)"),
    ("53", "Cuba (53)"),
    ("599", "Curacao (599)"),
    ("357", "Cyprus (357)"),
    ("420", "Czech Republic (420)"),
    ("243", "Democratic Republic of the Congo (243)"),
    ("45", "Denmark (45)"),
    ("253", "Djibouti (253)"),
    ("1-767", "Dominica (1-767)"),
    ("1-809", "Dominican Republic (1-809)"),
    ("1-829", "Dominican Republic (1-829)"),
    ("1-849", "Dominican Republic (1-849)"),
    ("670", "East Timor (670)"),
    ("593", "Ecuador (593)"),
    ("20", "Egypt (20)"),
    ("503", "El Salvador (503)"),
    ("240", "Equatorial Guinea (240)"),
    ("291", "Eritrea (291)"),
    ("372", "Estonia (372)"),
    ("251", "Ethiopia (251)"),
    ("500", "Falkland Islands (500)"),
    ("298", "Faroe Islands (298)"),
    ("679", "Fiji (679)"),
    ("358", "Finland (358)"),
    ("681", "Futuna (681)"),
    ("33", "France (33)"),
    ("689", "French Polynesia (689)"),
    ("241", "Gabon (241)"),
    ("220", "Gambia (220)"),
    ("995", "Georgia (995)"),
    ("49", "Germany (49)"),
    ("233", "Ghana (233)"),
    ("350", "Gibraltar (350)"),
    ("30", "Greece (30)"),
    ("299", "Greenland (299)"),
    ("1-473", "Grenada (1-473)"),
    ("1-784", "Grenadines (1-784)"),
    ("1-671", "Guam (1-671)"),
    ("502", "Guatemala (502)"),
    ("44-1481", "Guernsey (44-1481)"),
    ("224", "Guinea (224)"),
    ("245", "Guinea-Bissau (245)"),
    ("592", "Guyana (592)"),
    ("509", "Haiti (509)"),
    ("387", "Herzegovina (387)"),
    ("504", "Honduras (504)"),
    ("852", "Hong Kong (852)"),
    ("36", "Hungary (36)"),
    ("354", "Iceland (354)"),
    ("91", "India (91)"),
    ("62", "Indonesia (62)"),
    ("98", "Iran (98)"),
    ("964", "Iraq (964)"),
    ("353", "Ireland (353)"),
    ("44-1624", "Isle of Man (44-1624)"),
    ("972", "Israel (972)"),
    ("39", "Italy (39)"),
    ("225", "Ivory Coast (225)"),
    ("1-876", "Jamaica (1-876)"),
    ("47", "Jan Mayen (47)"),
    ("81", "Japan (81)"),
    ("44-1534", "Jersey (44-1534)"),
    ("962", "Jordan (962)"),
    ("7", "Kazakhstan (7)"),
    ("254", "Kenya (254)"),
    ("686", "Kiribati (686)"),
    ("383", "Kosovo (383)"),
    ("965", "Kuwait (965)"),
    ("996", "Kyrgyzstan (996)"),
    ("856", "Laos (856)"),
    ("371", "Latvia (371)"),
    ("961", "Lebanon (961)"),
    ("266", "Lesotho (266)"),
    ("231", "Liberia (231)"),
    ("218", "Libya (218)"),
    ("423", "Liechtenstein (423)"),
    ("370", "Lithuania (370)"),
    ("352", "Luxembourg (352)"),
    ("853", "Macau (853)"),
    ("389", "Macedonia (389)"),
    ("261", "Madagascar (261)"),
    ("265", "Malawi (265)"),
    ("60", "Malaysia (60)"),
    ("960", "Maldives (960)"),
    ("223", "Mali (223)"),
    ("356", "Malta (356)"),
    ("692", "Marshall Islands (692)"),
    ("222", "Mauritania (222)"),
    ("230", "Mauritius (230)"),
    ("262", "Mayotte (262)"),
    ("52", "Mexico (52)"),
    ("691", "Micronesia (691)"),
    ("508", "Miquelon (508)"),
    ("373", "Moldova (373)"),
    ("377", "Monaco (377)"),
    ("976", "Mongolia (976)"),
    ("382", "Montenegro (382)"),
    ("1-664", "Montserrat (1-664)"),
    ("212", "Morocco (212)"),
    ("258", "Mozambique (258)"),
    ("95", "Myanmar (95)"),
    ("264", "Namibia (264)"),
    ("674", "Nauru (674)"),
    ("977", "Nepal (977)"),
    ("31", "Netherlands (31)"),
    ("599", "Netherlands Antilles (599)"),
    ("1-869", "Nevis (1-869)"),
    ("687", "New Caledonia (687)"),
    ("64", "New Zealand (64)"),
    ("505", "Nicaragua (505)"),
    ("227", "Niger (227)"),
    ("234", "Nigeria (234)"),
    ("683", "Niue (683)"),
    ("850", "North Korea (850)"),
    ("1-670", "Northern Mariana Islands (1-670)"),
    ("47", "Norway (47)"),
    ("968", "Oman (968)"),
    ("92", "Pakistan (92)"),
    ("680", "Palau (680)"),
    ("970", "Palestine (970)"),
    ("507", "Panama (507)"),
    ("675", "Papua New Guinea (675)"),
    ("595", "Paraguay (595)"),
    ("51", "Peru (51)"),
    ("63", "Philippines (63)"),
    # ('64', 'Pitcairn (64)'),
    ("48", "Poland (48)"),
    ("351", "Portugal (351)"),
    ("239", "Principe (239)"),
    ("1-787", "Puerto Rico (1-787)"),
    ("1-939", "Puerto Rico (1-939)"),
    ("974", "Qatar (974)"),
    ("242", "Republic of the Congo (242)"),
    ("262", "Reunion (262)"),
    ("40", "Romania (40)"),
    ("7", "Russia (7)"),
    ("250", "Rwanda (250)"),
    ("590", "Saint Barthelemy (590)"),
    ("290", "Saint Helena (290)"),
    ("1-869", "Saint Kitts (1-869)"),
    ("1-758", "Saint Lucia (1-758)"),
    ("590", "Saint Martin (590)"),
    ("508", "Saint Pierre (508)"),
    ("1-784", "Saint Vincent (1-784)"),
    ("685", "Samoa (685)"),
    ("378", "San Marino (378)"),
    ("239", "Sao Tome (239)"),
    ("966", "Saudi Arabia (966)"),
    ("221", "Senegal (221)"),
    ("381", "Serbia (381)"),
    ("248", "Seychelles (248)"),
    ("232", "Sierra Leone (232)"),
    ("65", "Singapore (65)"),
    ("1-721", "Sint Maarten (1-721)"),
    ("421", "Slovakia (421)"),
    ("386", "Slovenia (386)"),
    ("677", "Solomon Islands (677)"),
    ("252", "Somalia (252)"),
    ("27", "South Africa (27)"),
    ("82", "South Korea (82)"),
    ("211", "South Sudan (211)"),
    ("34", "Spain (34)"),
    ("94", "Sri Lanka (94)"),
    ("249", "Sudan (249)"),
    ("597", "Suriname (597)"),
    ("47", "Svalbard (47)"),
    ("268", "Swaziland (268)"),
    ("46", "Sweden (46)"),
    ("41", "Switzerland (41)"),
    ("963", "Syria (963)"),
    ("886", "Taiwan (886)"),
    ("992", "Tajikistan (992)"),
    ("255", "Tanzania (255)"),
    ("66", "Thailand (66)"),
    ("1-868", "Tobago (1-868)"),
    ("228", "Togo (228)"),
    ("690", "Tokelau (690)"),
    ("676", "Tonga (676)"),
    ("1-868", "Trinidad (1-868)"),
    ("216", "Tunisia (216)"),
    ("90", "Turkey (90)"),
    ("993", "Turkmenistan (993)"),
    ("1-649", "Turks (1-649)"),
    ("688", "Tuvalu (688)"),
    ("1-340", "U.S. Virgin Islands (1-340)"),
    ("256", "Uganda (256)"),
    ("380", "Ukraine (380)"),
    ("971", "United Arab Emirates (971)"),
    ("44", "United Kingdom (44)"),
    ("1", "United States (1)"),
    ("598", "Uruguay (598)"),
    ("998", "Uzbekistan (998)"),
    ("678", "Vanuatu (678)"),
    ("379", "Vatican (379)"),
    ("58", "Venezuela (58)"),
    ("84", "Vietnam (84)"),
    ("681", "Wallis (681)"),
    ("212", "Western Sahara (212)"),
    ("967", "Yemen (967)"),
    ("260", "Zambia (260)"),
    ("263", "Zimbabwe (263)"),
)


# Country name function: This function returns a given country name based on the inputted code.
def country_name(code="234"):
    return dict(country_codes).get(code)
