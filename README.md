# TuxKatana

  > Interface python de communication avec le Boss Katana via USB

## Installation

Python Requirements:

gtk4 mido bidict collections 

## Adding Interface

3 files to create

### params/you_interface.yaml

format :
```
SEND:
    variable: "XX XX XX XX"     # XX -> hex str expression of address 
RECV:
    "XX XX XX XX": 'variable'   # addresses to only be readen
Models:
    "Name": "XX"                # XX: hex code of model
```
### widgets/your_interface


addresses to send/receive NB: receive = receive | send.inverse
  - lib/ur_intrf.py
  - widgets/ur_intrf.py

