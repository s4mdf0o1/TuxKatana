# How

   * All hexa bytes are MIDI (base 128) : 0x7F +1 = 0x00 
   
   > see: [MIDIBytes](./lib/midi_bytes.py)
   * All messages are F0 ... F7 enclosed (added by mido)
   * Scan device request by sending  '7F 00 06 01'
   * Ask device name at '10 00 00 00'
   * the starting actual preset adress is '60 00 00 00'
   * Preset name is stored at '60 00 00 00', size MIDIBytes('10').int = 16
   * Each address corresponding to one (or more) bytes of each setting is stored as a variable in the YAML files named according to each effect.

## Naming convention
 Each effect must be named precisely, with its corresponding YAML file name determines its properties based on a prefix.  
 [ModFx](./widgets/mod_fx.py) Effects are added in the modfx folder

Example : ['Booster'](./widgets/booster.py)
 
   * py_file : 'widgets/booster.py'
   * yaml_file : 'params/booster.yaml'
   * class_name: 'Booster'
   * prefix : 'bo_'

ModFx Example : ['Touch Wah'](./widgets/modfx/touch_wah.py)

   * py_file : 'widgets/modfx/touch_wah.py'
   * yaml_file : 'params/modfx/touch_wah.yaml'
   * class_name: 'TouchWah'
   * prefix : 'tw_'

## Init order
Mido Message constructed with [SysEx](./lib/sysex.py)

    Katana ◀ SEND  |  RECV ▶ TuxKatana
Approximately interpreted:
   * ◀ F0 7E 00 06 01 F7        # Scan devices
   * ▶ F0 7E 00 06 02 41 33 03 00 00 06 00 00 00 F7
      * '41': Vendor (Boss) 
      * '33': Model (Katana Mk2)
      * '03': ???
      * '00 06 00 00': Firmware version ?
      * '00': checksum ?  (here unsure, sure and calculated for other next messages)
The following is Ok:
   * ◀ F0 41 00 00 00 00 33 11 10 00 00 00 00 00 00 10 60 F7    # Ask device name
      * '41 00 00 00 00 33': Header (for all following messages)
      * '11': Get
      * '10 00 00 00': [Address](./lib/midi_bytes.py)
      * '00 00 00 10': size - AKA: nb bytes
      * '60': checksum (idem for all following messages)
   * ▶ F0 41 00 00 00 00 33 12 10 00 00 00 4B 41 54 41 4E 41 20 4D 6B 32 20 20 20 20 20 20 76 F7
      * '12': Set
      * 4B 41 54 41 4E 41 20 4D 6B 32 ... 20': "KATANA Mk2"
```python  
>>> MIDIBytes('4B 41 54 41 4E 41 20 4D 6B 32 20').to_chars()
'KATANA Mk2 '
```
   * ◀ F0 41 00 00 00 00 33 11 10 01 00 00 00 00 00 10 5F F7    # Ask Preset name #1
   * ▶ F0 41 00 00 00 00 33 12 10 01 00 00 43 6C 65 61 6E 20 52 65 76 65 72 62 20 20 20 20 06 F7
   * ◀ F0 41 00 00 00 00 33 11 10 02 00 00 00 00 00 10 5E F7    # Ask Preset name #2
   * ▶ F0 41 00 00 00 00 33 12 10 02 00 00 43 6C 65 61 6E 20 54 6F 6E 65 20 20 20 20 20 20 15 F7
   * ... # to preset name 8, at '10 08 00 00'
   * ◀ F0 41 00 00 00 00 33 12 7F 00 00 01 01 7F F7                    # Set Edit Mode True ['00'|'01']
   * ◀ F0 41 00 00 00 00 33 11 60 00 00 00 00 00 0F 00 11 F7    # Ask dump Memory size '00 00 0F 00'
```python
>>> MIDIBytes('0F 00').int
1920
```
   * ▶ 5 Messages of data size of 241, with corresponding adresses  
```python  
>>> Address('60 00 00 00') + 241
Address('60 00 01 71')
>>> Address('60 00 01 71') + 241
Address('60 00 03 62')
...
```
   * ▶ a final message with a size of 139 bytes whose address is offset, I don't know why, I fill it with zeros for a consistent size of [Memory](./lib/memory.py)
## Special
### Edit Mode

    Toggled at '7F 00 00 01': ['00' | '01']
    

### Channel Change
    
 Send 3 MIDIBytes at Address('00 01 00 00'): see 'SWITCHER' in [config.yaml](./params/config.yaml)


