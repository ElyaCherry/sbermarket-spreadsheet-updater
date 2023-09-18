import ast

urls = {}

markets = ["metro", "auchan", "lenta", "pyaterochka", "magnit", "okey", "samokat", "perekrestok", "fixprice", "vernyy",
           "lenta fast", "vkusvill", "dixy", "vprok"]

# prompt user for market and product names
while True:
    market_name = input("Enter the name of the market (or 'quit' to finish): ")
    if market_name == 'quit':
        break
    col = markets.index(market_name) + 4

    urls[market_name] = {}
    while True:
        product_name = input("Enter the name of the product (or 'done' to finish): ")
        if product_name == 'done':
            break

        # prompt user for URL and cell coordinates
        url = input(f"Enter the URL for {product_name} on {market_name}: ")
        row = input(f"Enter the row number for {product_name} on {market_name}: ")

        # add URL and cell coordinates to dictionary
        urls[market_name][product_name] = {'url': url, 'row': int(row), 'col': int(col)}

# write dictionary to file
with open('maps.py', 'w') as f:
    f.write(f"urls = {ast.literal_eval(str(urls))}")
