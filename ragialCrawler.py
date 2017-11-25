# -------------------- 0. INFORMATION
"""
RagialCrawler is a small Python (3.5.2) script which automatically
access Ragial (default to iRO-Odin) and uses the Search System, mainly 
for Costumes queries, and gather useful economic information. 

The original purpose of this script is to summarize all pertinent information 
about iRO costume economics, bringing a extra facility to people who are actively
participating on the Ragnarok Costumes market.
"""
# -------------------- END OF SECTION (0)

# -------------------- 1. IMPORT SECTION
from urllib.request import Request, urlopen # Necessary to communicate with Ragial
from operator import itemgetter # To sort the information get
from termcolor import colored # For good terminal print aesthetics
from enum import Enum # To keep the code more organized
import pandas # To print the information get data.frame-like
import time # Time, to put this daemon to sleep after a refresh
import re # Regular expressions, to find interesting information
# -------------------- END OF SECTION (1)

# -------------------- 2. CONFIGURATION SECTION
# These values can be modified to adopt the script to another personal interest.
# Please note that this is a facilitie, but the script itself was not originally
# thinked to be this dynamic. This means that deeper modifications on this script 
# can be necessary, depending on the parameters set on this section. 
ragialServerLink = 'http://ragi.al/search/iRO-Odin/' # Link to Ragial search section, with server
query = 'costume' # Query to search for. Default is 'costume'
myCustomHeader = {'User-Agent': 'Mozilla/5.0'}
ragialRefreshTime = 600 # This time should be in seconds
requestDelay = 5.0 # Delay, in seconds, of a delay between each request on Ragial.
pandas.options.display.max_rows = 999 # Maximum rows while printing the gathered information
# Note: low values (< 5s) tend to NOT work, resulting on a (Too many requests) 429 error.
# -------------------- END OF SECTION (2)

# -------------------- 3. ENUMS
# 3.1 This enumerator reflects the sequence of the information gatehered by the
# 'RegexFindItemPrice' when used on the Ragial HTML Source Page of a specific item.
class RagialValueOrder(Enum):
	# 'Short' is a seven (7) days analysis
	MIN_SHORT_PERIOD = 0 # Minimum item price on a (7) days analysis
	MAX_SHORT_PERIOD = 1 # Maximum item price on a (7) days analysis
	AVG_SHORT_PERIOD = 2 # Average item price on a (7) days analysis
	STDEV_SHORT = 3	# Standard Devitation of the item price on a (7) days analysis
	# 'Long' is a twenty eight (28) days analysis
	MIN_LONG_PERIOD = 4 # Minimum item price on a (28) days analysis
	MAX_LONG_PERIOD = 5 # Maximum item price on a (28) days analysis
	AVG_LONG_PERIOD = 6 # Average item price on a (28) days analysis
	STDEV_LONG = 7 # Standard Devitation of the item price on a (28) days analysis
	# From here, comes the available players prices
	MINIMAL_PRICE = 8 # The best price found on Ragial

# 3.2 This enumerator, to be fair, is pure cosmetic at moment. This indicates the
# order of the columns used on Pandas's dataframe to print the colected relevant data.
# In other words, this is useful only for developers orientation.
class scriptInfoOrder(Enum):
	PROPORTION = 0 # Proportion calculus is (CurrentBestPrice/ShortAveragePrice - 1)
	ITEM_NAME = 1 # Self explanatory
	MIN_CURRENT_PRICE = 2 # Current item best price detected on Ragial
	AVG_SHORT = 4 # Average item price on a seven (7) days analysis
# -------------------- END OF SECTION (3)

# -------------------- 4. REGULAR EXPRESSIONS
# 4.1 Regex to search for the item links
RegexFindItemURL = re.compile(r'http://ragi\.al/item/iRO-Odin/([^"]+)')
# 4.2 Regex to search for item's title/name
RegexFindItemTitle = re.compile(r'<title>\s*Ragial\s*-\s*([^-]+)\s*-\s*iRO-Odin\s*</title>')
# 4.3 Regex to search for item prices/standard devitations/related values
RegexFindItemPrice = re.compile(r'([0-9,]+)z')
# 4.4 Regex to detect for Ragial's next page link on search HTML source code (capturing the exact
# link is unnecessary, because these follows a very simple predictable pattern).
RegexFindNextPage = re.compile(r'<a href="' + ragialServerLink + query + '/' + r'\w">Next</a>')
# -------------------- END OF SECTION (4)

# -------------------- 5. SOURCE SECTION
# Applies a Regex to find the item name on a given Raw HTML source code.
# It does return 'Unknown Item Name' if Regex fails.
def getItemName(itemRawPageSource):
	regMatch = RegexFindItemTitle.search(itemRawPageSource)
	return regMatch.group(1) if regMatch else 'Unknown Item Name'

# Get all economic relevant information on a raw HTML Item source page.
def parseNewItem(itemTitle, itemRawPageSource):
	# Seach for all relevant (zeny-based) information on the page HTML source code 
	values = RegexFindItemPrice.findall(itemRawPageSource)
	if values:
		# Remove ',' on the item value strings, and convert to integers (there's no decimal values on Ragnarok prices)
		for i in range(len(values)):
			values[i] = values[i].replace(',', '')
		values = list(map(int, values))
		
		# Proportion of the Item Best Price and the Average Price (7 days analysis). Lower values (< 0)
		# represent best opportunities, while higher (> 0) represent overpriced/price inflated items.
		proportion = values[RagialValueOrder.MINIMAL_PRICE.value]/values[RagialValueOrder.AVG_SHORT_PERIOD.value] - 1
 
		return [proportion, itemTitle, values[RagialValueOrder.MINIMAL_PRICE.value], values[RagialValueOrder.AVG_SHORT_PERIOD.value]]
	return []

# Produce a combination of Ragial Server's search link + query (costume, by default) + pageIndex
def _mountQueryLink(pageIndex):
	return ragialServerLink + query + '/' + str(pageIndex)

# Set Price Proportions (BestPrice/AveragePrice - 1) output readable fomart
def setProportionFormat(proportion):
	# Pertinent explanations:
	# '\033[92m' is GREEN COLOR (set if and only if proportion < 0)
	# '\033[91m' is RED COLOR (alternative color)
	# '\033[0m'  is FORMATING END
	# '{0:.2f}' means two decimal points

	# I'm having some trouble setting color at the output, because panda's dataFrame
	# get confused with the ANSI codes. Still to be fixed later.
	# return ('\033[92m' if proportion < 0 else '\033[91m') + '{0:.2f}\033[0m'.format(proportion)
	return '{0:.2f}%'.format(proportion * 100)
	
# Main method of the script.
def main():
	# Outter loop to keep program running 'forever', daemon-like application (1)
	while True:
		# -------------------- 5.1 VARIABLE SETUP
		pageIndex = 0
		hasNextPage = True
		# Start the information data structure. This is where all the information got goes before pandas data.frame
		gatheredInfo = []
		# -------------------- END OF SUBSECTION (5.1)

		# Inner Loop here, while it has a 'next' page to search up to (2)
		while hasNextPage:
			rawPageSource = str()
			pageIndex += 1
			
			# -------------------- 5.2 REQUEST RAGIAL HTML SOURCE
			try:
				# Requesting Ragial Iro-Odin costume first page search
				request = Request(_mountQueryLink(pageIndex), 
					headers = myCustomHeader)

				rawPageSource = str(urlopen(request).read())

			except BaseException as exc: 
				print(colored('Fatal: could not get the source page from Ragial. (error: ' + repr(exc) + ')', 'red'))
			# -------------------- END OF SUBSECTION (5.2)

			if rawPageSource:
				print(colored('New Ragial item page found (index: ' + str(pageIndex) + ').', 'yellow'))
				# Find the item links, removing the identical ones
				itemLinkID = set(RegexFindItemURL.findall(rawPageSource))

				# -------------------- 5.3 GET ITEM ECONOMIC DATA
				try:
					for item in itemLinkID:
						print(colored('Requesting \'' + item + '\' item data...', 'yellow'))
						time.sleep(requestDelay)
						itemRawPageSource = str()

						try:
							itemRequest = Request('http://ragi.al/item/iRO-Odin/' + item, 
								headers = myCustomHeader)

							# Get page HTML source code
							itemRawPageSource = str(urlopen(itemRequest).read())

							# Search for the item name on the page HTML source code
							itemTitle = getItemName(itemRawPageSource)

							# Append a new information pack about a item
							gatheredInfo.append(parseNewItem(itemTitle, itemRawPageSource))

						except BaseException as exc:
							print(colored('Error on getting', 
								'\'http://ragi.al/item/iRO-Odin/' + item + '\' (error: ' + repr(exc) + ')', 
								'data.', 'red'))

					# Move to the next page, and repeat inner loop (2)
					hasNextPage = RegexFindNextPage.search(rawPageSource) 
					
					# Delay to now overflow Ragial with requests
					time.sleep(requestDelay)

				except BaseException as exc:
					print(colored('Error: ' + repr(exc), 'red'))
					hasNextPage = None
				# -------------------- END OF SUBSECTION (5.3)

		# -------------------- 5.4 PRINT ALL GATHERED INFORMATION
		# Remove all null data from the gathered info (probably all empty lists)
		gatheredInfo = [item for item in gatheredInfo if item]
		# Check if there is at least a single valid information
		if gatheredInfo:
			# Now sort the items gathered by its commercial relevance and print all gathered data
			gatheredInfo.sort(key = itemgetter(scriptInfoOrder.PROPORTION.value), reverse = True)
			dataFrame = pandas.DataFrame(gatheredInfo)
			dataFrame.columns = ['P', 'Item Name', 'Best Price', 'Avg (7D)']
			dataFrame['P'] = dataFrame['P'].map(setProportionFormat)
			print(dataFrame)
		else:
			print(colored('Warning: no data gathered at all.', 'yellow'))
		# -------------------- END OF SUBSECTION (5.4)

		# Make the program 'sleep' for some minutes, to wait Ragial update it's info
		time.sleep(ragialRefreshTime)

# SCRIPT START
if __name__ == '__main__':
	main()
# -------------------- END OF SECTION (5)