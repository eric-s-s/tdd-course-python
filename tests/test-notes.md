
# POS reader/display 

## problem scope

POSSystem:

- displayConnection
- productCatalog

- onBarcode(Barcode("str"))
  - getPrice() 
  - display()

barcodes:

- ""
- "23948234"
- "garbage"
- "23847239847(\r|\n|\t)" or any combination

ProductLookup.getPrice

- no price
- price
- multiple prices?  ugh! no!

display()

- response.OK
- response.FAIL

## test cases

no display:
1. empty barcode

error displays:
1. garbage barcode
2. no lookup found


Legit barcodes:
1. string
2. 10 digits
3. trailing and/or leading characters can be space, tab, and new line

retries on lookup?  out of scope!

displays:
1. single display
2. multiple requests only shows last one
3. multiple same request
4. multiple different request

retries on display?  maaaaaybe


## Scan multiple barcodes

3 things.
- displays total price as scan
- what if missing?
- need a total button
- total on products found?
