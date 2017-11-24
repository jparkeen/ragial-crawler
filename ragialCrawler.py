# -------------------- 1. IMPORT SECTION
from urllib.request import Request, urlopen # Necessary to communicate with Ragial
from termcolor import colored # For good terminal print aesthetics
from enum import Enum
import pandas
import time # Time, to put this daemon to sleep after a refresh
import re # Regular expressions, to find interesting information
from operator import itemgetter
# -------------------- END OF SECTION (1)

# -------------------- 2. CONFIGURATION SECTION
ragialServerLink = 'http://ragi.al/search/iRO-Odin/' 
query = 'costume'
myCustomHeader = {'User-Agent': 'Mozilla/5.0'}
ragialRefreshTime = 600 # This time should be in seconds
# -------------------- END OF SECTION (2)

# -------------------- 3. ENUMS
class RagialValueOrder(Enum):
	# 'Short' is a seven (7) days analysis
	MIN_SHORT_PERIOD = 0
	MAX_SHORT_PERIOD = 1
	AVG_SHORT_PERIOD = 2
	STDEV_SHORT = 3
	# 'Long' is a twenty eight (28) days analysis
	MIN_LONG_PERIOD = 4
	MAX_LONG_PERIOD = 5
	AVG_LONG_PERIOD = 6
	STDEV_LONG = 7
	# From here, comes the available players prices
	MINIMAL_PRICE = 8

class scriptInfoOrder(Enum):
	PROPORTION = 0
	ITEM_NAME = 1
	MIN_CURRENT_PRICE = 2
	MIN_SHORT = 3
	AVG_SHORT = 4
	MAX_SHORT = 5
	
# -------------------- END OF SECTION (3)

# -------------------- 4. REGULAR EXPRESSIONS
# Regex to search for the item links
RegexfindItemURL = re.compile(r'http://ragi\.al/item/iRO-Odin/([^"]+)')
RegexfindItemTitle = re.compile(r'<title>\s*Ragial\s*-\s*([^-]+)\s*-\s*iRO-Odin\s*</title>')
RegexfindItemPrice = re.compile(r'([0-9,]+)z')
# -------------------- END OF SECTION (4)

# -------------------- 5. SOURCE SECTION
# Outter loop to keep program running 'forever', daemon-like application (1)
while True:
	# Inner Loop here, while it has a 'next' page to search up to (2)
	rawPageSource = str()
	try:
		# Requesting Ragial Iro-Odin costume first page search
		request = Request(ragialServerLink + query, 
			headers = myCustomHeader)

		rawPageSource = str(urlopen(request).read())

	except BaseException as exc: 
		print(colored('Fatal: could not get the source page from Ragial. (error: ' + repr(exc) + ')', 'red'))

	gatheredInfo = [[-1] * 6]

	if rawPageSource:
		# Find the item links, removing the identical ones
		itemLinkID = set(RegexfindItemURL.findall(rawPageSource))

		try:
			for item in itemLinkID:
				itemRawPageSource = str()

				try:
					itemRequest = Request('http://ragi.al/item/iRO-Odin/' + item, 
						headers = myCustomHeader)

					# Get page HTML source code
					itemRawPageSource = str(urlopen(itemRequest).read())

					# Search for the item name on the page HTML source code
					itemTitle = RegexfindItemTitle.findall(itemRawPageSource)
					# Seach for all relevant (zeny-based) information on the page HTML source code 
					values = RegexfindItemPrice.findall(itemRawPageSource)

					# Append a new information pack about a item
					gatheredInfo.append([
						values[scriptInfoOrder.PROPORTION.value],
						values[scriptInfoOrder.ITEM_NAME.value],
						values[scriptInfoOrder.MINIMAL_PRICE.value],
						values[scriptInfoOrder.MIN_SHORT_PERIOD.value],
						values[scriptInfoOrder.AVG_SHORT_PERIOD.value],
						values[scriptInfoOrder.MAX_SHORT_PERIOD.value]
						])

				except BaseException as exc:
					print(colored('Error on getting', 
						'\'http://ragi.al/item/iRO-Odin/' + item + '\' (error: ' + repr(exc) + ')', 
						'data.', 'red'))

		except BaseException as exc:
			print(colored('Error: ' + repr(exc), 'red'))
			
		# Now sort the items gathered by its commercial relevance and print all gathered data
		gatheredInfo.sort(key = itemgetter(scriptInfoOrder.PROPORTION.value))

		# Move to the next page, and repeat inner loop (2)

	dataFrame = pandas.DataFrame(gatheredInfo)
	dataFrame.columns = ['P', 'Item Name', 'Best Price', 'Avg (7D)', 'Min (7D)', 'Max (7D)']
	print(dataFrame)

	# Make the program 'sleep' for some minutes, to wait Ragial update it's info
	time.sleep(ragialRefreshTime)
# -------------------- END OF SECTION (5)