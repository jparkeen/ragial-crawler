# RagialCrawler
RagialCrawler is a simple Python (version 3.5) script which automatically search all costumes-like items on Ragial default to on iRO-Odin server (but has easy support to all other Ragial supported servers), and get all relevant economic data from each found item. Then, at the end, it does print all the found items sorted by the proportion of Best Current Price Found and Short (7D) Average Item Price.

# Dependencies
- Python 3.5 or a greater version
- 'colorama' library
- Other libraries should not be a problem.

# Run
Just type on your terminal/console which follows:
```
$ python3 ragialCrawler.py
```
In case of missing colorama library type:
```
$ pip install colorama
```

# Functionallity
- The program does not need any input.
- It is supposed to run until the user stops it manually (Ctrl+C or killing the process).
- If the user ends the program, all memoized data will be lost, and must be regathered on the next session. This will not be 'fixed', as it prevents outdated memoized information.
- It does update every 5 mins (300 seconds), in order to follow the Ragial update delay and to do not overcharge Ragial server with requests.
- It does check all Ragial search pages, and get information only about items currently active on market.
- It has a delay of fours (4) seconds between each item data request, to avoid (Too Many Requests) 429 error. This delay occurs only on new items not memoized on the current section. If the item is already on the memoization table (i.e already found on previous iterations), it does not need a additional request, and the script only update it's best price and the proportion in relation of average price (7 days analysis), and proceed to the next item without delay.
- It has a four (4) seconds delay between each next page search request, in order to avoid (Too Many Requests) 429 error on the scenario when all items of the current page are already on the memoization structure.

# Output
The output is a Data Frame, which column order follows the specified order:
- Proportion: calculated by ((Best Ragial Price)/(Average Item Price (7 day analysis)) - 1.0) * 100.0
- Item name
- Best Ragial price at moment
- Average Price on a seven (7) days analysis
- Ragial item link

# For future Updates, if they ever happen
- Official script extern documentation
- And on-the-fly decided features.
- Or nothing, at all.
