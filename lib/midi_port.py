import mido
from time import sleep
import logging
dbg = logging.getLogger("debug")

class KatanaPort:
    def __init__(self):
        self.has_device = False
        self.is_connected = False
        self.index = 0
        self.name = None

        #GLib.timeout_add_seconds(10, self.check_online)

    def check_online( self ):
        dbg.debug("KatanaPort.check_online")
        ports = mido.get_output_names()
        self.has_device = any("katana" in p.lower() for p in ports)
        return True

    def list(self):
        dbg.debug("KatanaPort.list")
        midi_ports = mido.get_output_names()
        self.ports = [p for p in midi_ports if 'katana' in p.lower() or 'boss' in p.lower()] or None
        if self.ports:
            print(f"Ports MIDI disponibles: {self.ports}")
            self.has_device = True
            for i, port in enumerate(self.ports):
                print(f"{i}: {port}")
 
    def select( self, port_index ):
        self.index= port_index
        print(f"Sélection du port : {self.ports[port_index]}")
        return self.ports[port_index]

    def connect( self, callback ):
        mido.set_backend('mido.backends.rtmidi')
        try:
            if not self.name:
                self.name = self.ports[self.index]
            self.output = mido.open_output(self.name)
            self.input = mido.open_input(self.name, callback=callback)
            self.output.reset()
            print(f"Connecté au Katana sur: {self.name}")
            self.is_connected = True
        except Exception as e:
            self.is_connected = False
            raise Exception(f"Impossible de se connecter au port {self.name}: {e}")

    def send( self, message):#, callback=None ):
        dbg.debug(f"send: {message.hex()}")
        #if callback:
        #    self.listener_callback = callback
        #cks = self.checksum( message )
        self.output.send( message )

    def close( self ):
        if hasattr(self, 'output'):
            self.output.close()
        if hasattr(self, 'input'):
            self.input.close()
        print("Connexions MIDI fermées")

