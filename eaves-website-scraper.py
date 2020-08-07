#!/usr/bin/python3
#
from selenium import webdriver
import bs4
import urllib
import time
from bs4 import BeautifulSoup
import re
import csv
from collections import namedtuple
import datetime
import sys
import os
##from urllib import request

Apartment = namedtuple("Apartment", "UnitNum, Beds, Baths, Sqft, Price, AvailStart, AvailEnd")

class eavesApartmentParser:
    def __init__(self, url: str):
        self._apartments = []
        self._readUrl(url)
        self._parse()

    def _readUrl(self, url: str):
        options = webdriver.ChromeOptions()
        options.headless = True
        with webdriver.Chrome(options=options) as browser:
            browser.get(url)
            time.sleep(2)
            self._html = browser.page_source

    def _parse(self):
        bs = BeautifulSoup(self._html, "lxml")
        apartmentsUL = bs.find_all("li", {"class": "apartment-card"})
        for aptUL in apartmentsUL:
            aptNumStr = aptUL.find(class_="title brand-main-text-color").string.strip()
            aptDescStr = aptUL.find(class_="details").string.strip()
            aptPriceStr = aptUL.find(class_="price").find(class_="brand-main-text-color").string.strip()
            aptAvailDateStr = aptUL.find(class_="availability").string.strip()

            ## Parse out the garbage
            aptNum = re.search("Apartment.*-(\d.+)", aptNumStr).group(1)
            _aptDescMatches = re.search("(\d) bedroom\D*(\d) \D*(\d+)\D*", aptDescStr)
            aptNumBedroom = _aptDescMatches.group(1)
            aptNumBath = _aptDescMatches.group(2)
            aptNumSqft = _aptDescMatches.group(3)
            aptPrice = aptPriceStr[1:].replace(",","")
            _aptAvailMatches = re.search("[A-Za-z]+\s([A-Za-z]+)\s(\d+)\s.\s([A-Za-z]+)\s(\d+)", aptAvailDateStr)
            aptAvailStart = _aptAvailMatches.group(1) + " "+ _aptAvailMatches.group(2)
            aptAvailEnd = _aptAvailMatches.group(3) + " " +_aptAvailMatches.group(4)

            apt = Apartment(aptNum, aptNumBedroom, aptNumBath, aptNumSqft, aptPrice, aptAvailStart, aptAvailEnd)
            self._apartments.append(apt)

    def saveCSV(self, filePath : str):
        thisdate = datetime.datetime.now().strftime('%b-%d-%I%M%p-%G')
        fileName = os.path.join(filePath, "{}-eavesAvailability.csv".format(thisdate))
        with open(fileName, "w") as f:
            f.write("#UnitNum, Beds, Baths, Sqft, Price, AvailStart, AvailEnd\n")
            csvWriter = csv.writer(f, delimiter=",")
            for apt in self._apartments:
                csvWriter.writerow([apt.UnitNum, apt.Beds, apt.Baths, apt.Sqft, apt.Price, apt.AvailStart, apt.AvailEnd])


URL="https://www.avaloncommunities.com/california/san-diego-apartments/eaves-rancho-penasquitos/apartments?bedroom=1BD"
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("missing path argument")
        sys.exit(0)
    pathArg = sys.argv[1]
    dl = eavesApartmentParser(URL)    
    dl.saveCSV(pathArg)
