#!/usr/bin/env python3
"""
Contrôleur MIDI pour Boss Katana 100 Mk2
Permet de contrôler les effets, canaux et paramètres via SysEx
"""

import mido
import time
from typing import List, Union

class KatanaMk2Controller:
    def __init__(self, port_name: str = None):
        """
        Initialise la connexion MIDI avec le Katana Mk2
        """
        self.device_id = 0x00  # ID par défaut du Katana
        self.model_id = [0x00, 0x00, 0x00, 0x33]  # Katana Mk2
        
        # Liste les ports MIDI disponibles
        if port_name is None:
            ports = mido.get_output_names()
            print("Ports MIDI disponibles:")
            for i, port in enumerate(ports):
                print(f"{i}: {port}")
            
            katana_ports = [p for p in ports if 'katana' in p.lower() or 'boss' in p.lower()]
            if katana_ports:
                port_name = katana_ports[0]
                print(f"Port Katana détecté automatiquement: {port_name}")
            else:
                raise Exception("Aucun port Katana trouvé. Spécifiez le port manuellement.")
        
        try:
            self.output = mido.open_output(port_name)
            self.input = mido.open_input(port_name)
            print(f"Connecté au Katana sur: {port_name}")
        except Exception as e:
            raise Exception(f"Impossible de se connecter au port {port_name}: {e}")
    
    def _create_sysex_message(self, address: List[int], data: List[int], 
                            command: int = 0x12) -> mido.Message:
        """
        Crée un message SysEx pour le Katana
        Format: F0 41 [device_id] 00 00 00 33 [command] [address] [data] [checksum] F7
        """
        # En-tête Roland
        header = [0x41, self.device_id] + self.model_id + [command]
        
        # Construction du message complet (sans F0 et F7)
        message_data = header + address + data
        
        # Calcul du checksum Roland
        checksum = (0x80 - (sum(message_data[5:]) & 0x7F)) & 0x7F
        
        # Message SysEx complet
        sysex_data = message_data + [checksum]
        
        return mido.Message('sysex', data=sysex_data)
    
    def send_sysex(self, address: List[int], data: List[int]):
        """Envoie un message SysEx au Katana"""
        msg = self._create_sysex_message(address, data)
        self.output.send(msg)
        print(f"Envoyé: {[hex(x) for x in msg.data]}")
    
    def change_channel(self, channel: int):
        """
        Change le canal de l'ampli (0-3 pour CLEAN, CRUNCH, LEAD, BROWN)
        """
        if not 0 <= channel <= 3:
            raise ValueError("Le canal doit être entre 0 et 3")
        
        address = [0x00, 0x00, 0x00, 0x38]  # Adresse pour le changement de canal
        data = [channel]
        self.send_sysex(address, data)
        print(f"Canal changé vers: {['CLEAN', 'CRUNCH', 'LEAD', 'BROWN'][channel]}")
    
    def set_master_volume(self, volume: int):
        """
        Règle le volume principal (0-100)
        """
        if not 0 <= volume <= 100:
            raise ValueError("Le volume doit être entre 0 et 100")
        
        address = [0x00, 0x00, 0x00, 0x58]  # Adresse volume principal
        data = [volume]
        self.send_sysex(address, data)
        print(f"Volume principal réglé à: {volume}")
    
    def toggle_effect(self, effect_type: str, on: bool = True):
        """
        Active/désactive un effet
        effect_type: 'overdrive', 'distortion', 'booster', 'mod', 'fx', 'delay', 'reverb'
        """
        effect_addresses = {
            'booster': [0x00, 0x00, 0x00, 0x3A],
            'mod': [0x00, 0x00, 0x00, 0x3B], 
            'fx': [0x00, 0x00, 0x00, 0x3C],
            'delay': [0x00, 0x00, 0x00, 0x3D],
            'reverb': [0x00, 0x00, 0x00, 0x3E]
        }
        
        if effect_type not in effect_addresses:
            raise ValueError(f"Effet non supporté. Effets disponibles: {list(effect_addresses.keys())}")
        
        address = effect_addresses[effect_type]
        data = [1 if on else 0]
        self.send_sysex(address, data)
        print(f"Effet {effect_type}: {'ON' if on else 'OFF'}")
    
    def set_gain(self, gain: int):
        """
        Règle le gain (0-100)
        """
        if not 0 <= gain <= 100:
            raise ValueError("Le gain doit être entre 0 et 100")
        
        address = [0x00, 0x00, 0x00, 0x35]  # Adresse gain
        data = [gain]
        self.send_sysex(address, data)
        print(f"Gain réglé à: {gain}")
    
    def set_eq(self, bass: int = None, mid: int = None, treble: int = None):
        """
        Règle l'égaliseur (0-100 pour chaque bande)
        """
        if bass is not None:
            if not 0 <= bass <= 100:
                raise ValueError("Bass doit être entre 0 et 100")
            address = [0x00, 0x00, 0x00, 0x36]
            self.send_sysex(address, [bass])
            print(f"Bass réglé à: {bass}")
        
        if mid is not None:
            if not 0 <= mid <= 100:
                raise ValueError("Mid doit être entre 0 et 100")
            address = [0x00, 0x00, 0x00, 0x37]
            self.send_sysex(address, [mid])
            print(f"Mid réglé à: {mid}")
        
        if treble is not None:
            if not 0 <= treble <= 100:
                raise ValueError("Treble doit être entre 0 et 100")
            address = [0x00, 0x00, 0x00, 0x39]
            self.send_sysex(address, [treble])
            print(f"Treble réglé à: {treble}")
    
    def preset_save(self, preset_number: int):
        """
        Sauvegarde les réglages actuels dans un preset (1-4)
        """
        if not 1 <= preset_number <= 4:
            raise ValueError("Le numéro de preset doit être entre 1 et 4")
        
        address = [0x00, 0x00, 0x00, 0x7F]  # Commande de sauvegarde
        data = [preset_number - 1]
        self.send_sysex(address, data)
        print(f"Réglages sauvegardés dans le preset {preset_number}")
    
    def preset_load(self, preset_number: int):
        """
        Charge un preset (1-4)
        """
        if not 1 <= preset_number <= 4:
            raise ValueError("Le numéro de preset doit être entre 1 et 4")
        
        address = [0x00, 0x00, 0x00, 0x38]  # Adresse de sélection preset
        data = [preset_number - 1 + 4]  # Les presets sont décalés de 4
        self.send_sysex(address, data)
        print(f"Preset {preset_number} chargé")
    
    def close(self):
        """Ferme les connexions MIDI"""
        if hasattr(self, 'output'):
            self.output.close()
        if hasattr(self, 'input'):
            self.input.close()
        print("Connexions MIDI fermées")

def demo():
    """Démonstration d'utilisation du contrôleur"""
    try:
        # Connexion au Katana
        katana = KatanaMk2Controller()
        
        print("\n=== Démonstration du contrôleur Katana Mk2 ===")
        
        # Test changement de canal
        print("\n1. Test des canaux:")
        for i, channel_name in enumerate(['CLEAN', 'CRUNCH', 'LEAD', 'BROWN']):
            print(f"Passage au canal {channel_name}...")
            katana.change_channel(i)
            time.sleep(2)
        
        # Test volume
        print("\n2. Test du volume:")
        for vol in [50, 75, 25, 60]:
            print(f"Volume à {vol}%...")
            katana.set_master_volume(vol)
            time.sleep(1)
        
        # Test effets
        print("\n3. Test des effets:")
        effects = ['booster', 'mod', 'fx', 'delay', 'reverb']
        for effect in effects:
            print(f"Activation {effect}...")
            katana.toggle_effect(effect, True)
            time.sleep(1)
            print(f"Désactivation {effect}...")
            katana.toggle_effect(effect, False)
            time.sleep(1)
        
        # Test EQ
        print("\n4. Test de l'égaliseur:")
        katana.set_eq(bass=70, mid=60, treble=80)
        time.sleep(2)
        
        print("\nDémonstration terminée !")
        
    except Exception as e:
        print(f"Erreur: {e}")
    
    finally:
        if 'katana' in locals():
            katana.close()

if __name__ == "__main__":
    # Installation des dépendances requises
    print("Pour utiliser ce script, installez mido:")
    print("pip install mido python-rtmidi")
    print()
    
    # Lancement de la démo
    demo()
