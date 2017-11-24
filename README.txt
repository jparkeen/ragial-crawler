# RagialCrawler
RagialCrawler is a simple Python (Python 3.5.2) script which automatically search all Costumes-like itens on Ragial, more specifically on the iRO-Odin server, and get all relevant economic data from each found item. Then, at the end, it does print all the found items sorted by the proportion of Best Current Price Found and Short (7D) Average Item Price.

# Functionallity
- The program does not need any input. 
- It is supposed to run until the user stops it manually (Ctrl+C or killing the process). 
- It does update every 10 mins (600 seconds), in order to follow the Ragial update delay and to do not overcharge Ragial server with Requests.
- It does check all Ragial Pages.

# Output
The output is a Data Frame, which column order follows the specified order: