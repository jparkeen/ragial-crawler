# -------------------- 1. IMPORT SECTION
from urllib.request import Request, urlopen # Necessary to communicate with Ragial
from termcolor import colored # For good terminal print aesthetics
from bs4 import BeautifulSoup # Because item page HTML is hell's scratch
import time # Time, to put this daemon to sleep after a refresh
import re # Regular expressions, to find interesting information
# -------------------- END OF SECTION (1)

# -------------------- 2. CONFIGURATION SECTION
ragialServerLink = 'http://ragi.al/search/iRO-Odin/' 
query = 'costume'
myCustomHeader = {'User-Agent': 'Mozilla/5.0'}
ragialRefreshTime = 600 # This time should be in seconds
# -------------------- END OF SECTION(2)

# -------------------- 3. REGULAR EXPRESSIONS
# Regex to search for the item links
RegexfindItemURL = re.compile(r'http://ragi\.al/item/iRO-Odin/([^"]+)')
# RegexfindItemTitle = re.compile(r'<title>\s*([^<]+)\s*</title>')
RegexfindItemTitle = re.compile(r'<title>\s*Ragial\s*-\s*([^-]+)\s*-\s*iRO-Odin\s*</title>')
# -------------------- END OF SECTION(3)

# -------------------- 4. SOURCE SECTION
# Outter loop here, to keep program running 'forever' daemon-like (1)
# Inner Loop here, while it has a 'next' page to search up to (2)
rawPageSource = str()
try:
	# Requesting Ragial Iro-Odin costume first page search
	request = Request(ragialServerLink + query, headers = myCustomHeader)
	rawPageSource = str(urlopen(request).read())
except BaseException as exc: 
	print(colored('Fatal: could not get the source page from Ragial. (error: ' + repr(exc) + ')', 'red'))

if rawPageSource:
	# Find the item links, removing the identical ones
	itemLinkID = set(RegexfindItemURL.findall(rawPageSource))

	# Get the best and average prices
	try:
		for item in itemLinkID:
			itemRawPageSource = str()
			try:
				itemRequest = Request('http://ragi.al/item/iRO-Odin/' + item, headers = myCustomHeader)
				itemRawPageSource = str(urlopen(itemRequest).read())
				print(RegexfindItemTitle.findall(itemRawPageSource))
			except BaseException as exc:
				print(colored('Error on getting', '\'http://ragi.al/item/iRO-Odin/' + item + '\' (error: ' + repr(exc) + ')', 'data.', 'red'))
	except BaseException as exc:
		print(colored('Error: ' + repr(exc), 'red'))

	# Now sort the itens gathered by its commercial relevance and print all gathered data

	# Move to the next page, and repeat inner loop (2)

# Make the program 'sleep' for some minutes, to wait Ragial update it's info
# time.sleep(ragialRefreshTime)
# -------------------- END OF SECTION(4)