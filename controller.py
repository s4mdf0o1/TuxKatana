import mido
from time import sleep
from threading import Thread
import yaml
from ast import literal_eval

class KatanaPort:
    def __init__(self):
        self.ports = self.list()
        self.port_index = 0
        port_name = self.select(self.port_index)
        self.connect(port_name)

    def list(self):
        ports = mido.get_output_names()
        print("Ports MIDI disponibles:")
        ports = [p for p in ports if 'katana' in p.lower() or 'boss' in p.lower()]
        for i, port in enumerate(ports):
            print(f"{i}: {port}")
        return ports
 
    def select( self, port_index ):
        self.port_index= port_index
        print(f"Sélection du port : {self.ports[port_index]}")
        return self.ports[port_index]

    def connect( self, port_name ):
        mido.set_backend('mido.backends.rtmidi')
        try:
            self.output = mido.open_output(port_name)
            self.input = mido.open_input(port_name)
            print(f"Connecté au Katana sur: {port_name}")
            #print(mido.backend)
        except Exception as e:
            raise Exception(f"Impossible de se connecter au port {port_name}: {e}")

    def send( self, message ):
        self.output.send( message )

    def close( self ):
        if hasattr(self, 'output'):
            self.output.close()
        if hasattr(self, 'input'):
            self.input.close()
        print("Connexions MIDI fermées")
 
class SysEx(mido.Message):
    #header=[]
    def __init__( self, header ):
        super().__init__('sysex')
        print("DIR SYSEX")
        for d in dir(self):
            print(d)
        self.header = header

    def checksum( self, data ):
        checksum = 0
        for b in data:
            checksum += b & 0x7F
        checksum = (128 - (checksum & 0x7F)) & 0x7F
        return [checksum]
    
    def create( self, cmd, addr, val ):
        data=addr + val
        return mido.Message('sysex', self.header + cmd + data + self.checksum(data))

       
class KatanaController:
    def __init__(self, params=None):
        self.port = KatanaPort()
        self.port.input.callback = self.listener_callback
        sleep(1)
        if params == None:
            with open("params.yml", 'r') as f:
                self.params = yaml.safe_load(f)
        else:
            self.params = params
        self.vendor = self.params["Vendor"]
        self.device = self.params["Device"]
        self.model = self.params["Model"]
        header = self.vendor + self.device + self.model
        self.command=""
        self.cmd = [0x00]
        self.effect=""
        self.addr = [0x00, 0x00]
        self.value=""
        self.val = [0x00]
        self.sysex = mido.Message('sysex') #SysEx( header )

    def listener_callback(self, msg): #, dt):
        print(f"Reçu : {msg}") #" (delta {delta_time:.3f}s)")

    def set_command( self, command ):
        if command not in self.params["cmd"]:
            print(f"Bad command: {command}")
            self.command=""
            self.cmd = [0x00]
            return
        else:
            self.command = command
            self.cmd = self.params["cmd"][command]

    def set_effect( self, effect ):
        if effect not in self.params:
            print(f"Bad effect name: {effect}")
            self.effect = ""
            self.addr = [0x00]
            return
        else:
            self.effect = effect
            self.addr = self.params[effect]["addr"]

    def set_value( self, value ):
        if value not in self.params[effect]["val"]:
            print(f"Bad value: {value}")
            self.value = ""
            self.val = [0x00]
            return
        else:
            self.value = value
            self.val = self.params[effect]["val"][value]

    def send( self, command, effect, value ):
        self.port.send(self.sysex.create( self.cmd, self.addr, self.val))
        sleep(1)


if __name__ == "__main__":
    katana = KatanaController()
    try:
        katana.send("send", "Amp_type", "Lead")
    except KeyboardInterrupt:
        katana.port.close()


