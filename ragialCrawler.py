# -------------------- 1. IMPORT SECTION
from urllib.request import Request, urlopen
from termcolor import colored
# from bs4 import BeautifulSoup
import time
import re
# -------------------- END OF SECTION (1)

# -------------------- 2. CONFIGURATION SECTION
ragialServerLink = 'http://ragi.al/search/iRO-Odin/' 
query = 'costume'
myCustomHeader = {'User-Agent': 'Mozilla/5.0'}
ragialRefreshTime = 600 # This time is in seconds
# -------------------- END OF SECTION(2)

# -------------------- 3. REGULAR EXPRESSIONS
# Regex to search for the item links
findItemURLRegex = re.compile(r'http://ragi\.al/item/iRO-Odin/([^"]+)')
findItemTitleRegex = re.compile(r'<title>\s*([^<]+)\s*</title>')
# -------------------- END OF SECTION(3)

# -------------------- 4. SOURCE SECTION
# A greater loop here, to keep program running 'forever' 
# Another Loop here, while it has a 'next' page to search up to
rawPageSource = None
try:
	# Requesting Ragial Iro-Odin costume first page search
	request = Request(ragialServerLink + query, headers = myCustomHeader)
	rawPageSource = urlopen(request)
except: 
	print(colored('Fatal: could not get the source page from Ragial.', 'red'))

if rawPageSource:
	# Using Beautiful soup for simplicity (not sure if it only make things slower)
	# soupPageSource = BeautifulSoup(rawPageSource, 'html.parser').prettify()

	# Find the item links, removing the identical ones
	itemLinkID = list(set(findItemURLRegex.findall(str(rawPageSource.read()))))

	# Get the best and average prices
	for item in itemLinkID:
		itemRawPageSource = None
		try:
			itemRequest = Request('http://ragi.al/item/iRO-Odin/' + item, headers = myCustomHeader)
			itemRawPageSource = urlopen(itemRequest)
			print(findItemTitleRegex.findall(itemRawPageSource.read()))
		except:
			print(colored('Error on getting', '\'http://ragi.al/item/iRO-Odin/' + item + '\'', 'data.', 'red'))

	# Move to the next page, and repeat inner loop
# Make a program 'sleep' for some minutes, to wait ragial update it's info
# time.sleep(ragialRefreshTime)
# -------------------- END OF SECTION(4)