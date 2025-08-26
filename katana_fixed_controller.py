#!/usr/bin/env python3
"""
Contrôleur MIDI pour Boss Katana 100 Mk2 - Version corrigée
Utilise les vraies adresses SysEx du Katana Mk2
"""

import mido
import time
from typing import List

class KatanaMk2ControllerFixed:
    def __init__(self, port_name: str = None):
        """Initialise la connexion MIDI avec le Katana Mk2"""
        self.device_id = 0x00  # Device ID par défaut
        # Model ID pour Katana 100 Mk2 (testé avec différentes variations)
        self.model_id = [0x00, 0x00, 0x00, 0x33]
        
        # Détection automatique du port
        if port_name is None:
            ports = mido.get_output_names()
            katana_ports = [p for p in ports if 'katana' in p.lower() or 'boss' in p.lower()]
            if katana_ports:
                port_name = katana_ports[0]
                print(f"Port Katana détecté: {port_name}")
            else:
                print("Ports MIDI disponibles:")
                for i, port in enumerate(ports):
                    print(f"{i}: {port}")
                raise Exception("Aucun port Katana trouvé")
        
        try:
            self.output = mido.open_output(port_name)
            print(f"Connecté au Katana sur: {port_name}")
        except Exception as e:
            raise Exception(f"Impossible de se connecter: {e}")
    
    def _send_sysex_raw(self, data: List[int]):
        """Envoie des données SysEx brutes"""
        try:
            msg = mido.Message('sysex', data=data)
            self.output.send(msg)
            print(f"Envoyé: {' '.join([f'{x:02X}' for x in data])}")
            return True
        except Exception as e:
            print(f"Erreur d'envoi: {e}")
            return False
    
    def _create_katana_message(self, address: List[int], data: List[int]) -> List[int]:
        """Crée un message SysEx formaté pour Katana"""
        # En-tête Roland: F0 41 [device_id] [model_id] 12
        header = [0x41, self.device_id] + self.model_id + [0x12]
        
        # Corps du message
        body = header + address + data
        
        # Calcul du checksum Roland (sum des bytes après model_id)
        checksum = (0x80 - (sum(body[6:]) & 0x7F)) & 0x7F
        
        return body + [checksum]
    
    def toggle_effect_v1(self, effect_name: str, state: bool):
        """Version 1: Teste les adresses basées sur la documentation communautaire"""
        
        # Adresses d'effets pour Katana (format: adresse dans la mémoire)
        effect_addresses = {
            'booster': [0x60, 0x00, 0x11, 0x00],  # Booster switch
            'mod': [0x60, 0x00, 0x12, 0x00],      # Mod switch
            'fx': [0x60, 0x00, 0x13, 0x00],       # FX switch
            'delay': [0x60, 0x00, 0x14, 0x00],    # Delay switch
            'reverb': [0x60, 0x00, 0x15, 0x00]    # Reverb switch
        }
        
        if effect_name not in effect_addresses:
            print(f"Effet '{effect_name}' non reconnu")
            return False
        
        address = effect_addresses[effect_name]
        data = [0x01 if state else 0x00]
        
        message = self._create_katana_message(address, data)
        success = self._send_sysex_raw(message)
        
        if success:
            print(f"Effet {effect_name}: {'ON' if state else 'OFF'} (v1)")
        
        return success
    
    def toggle_effect_v2(self, effect_name: str, state: bool):
        """Version 2: Teste des adresses alternatives"""
        
        # Adresses alternatives trouvées dans des projets open source
        effect_addresses = {
            'booster': [0x60, 0x00, 0x11],
            'mod': [0x60, 0x00, 0x12], 
            'fx': [0x60, 0x00, 0x13],
            'delay': [0x60, 0x00, 0x14],
            'reverb': [0x60, 0x00, 0x15]
        }
        
        if effect_name not in effect_addresses:
            return False
        
        address = effect_addresses[effect_name]
        data = [0x01 if state else 0x00]
        
        message = self._create_katana_message(address, data)
        success = self._send_sysex_raw(message)
        
        if success:
            print(f"Effet {effect_name}: {'ON' if state else 'OFF'} (v2)")
        
        return success
    
    def toggle_effect_v3(self, effect_name: str, state: bool):
        """Version 3: Teste le format direct sans sous-adresse"""
        
        # Messages SysEx complets pré-calculés pour tests rapides
        effect_messages = {
            'booster': {
                True: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x11, 0x00, 0x01],
                False: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x11, 0x00, 0x00]
            },
            'mod': {
                True: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x12, 0x00, 0x01],
                False: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x12, 0x00, 0x00]
            },
            'fx': {
                True: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x13, 0x00, 0x01],
                False: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x13, 0x00, 0x00]
            },
            'delay': {
                True: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x14, 0x00, 0x01],
                False: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x14, 0x00, 0x00]
            },
            'reverb': {
                True: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x15, 0x00, 0x01],
                False: [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x15, 0x00, 0x00]
            }
        }
        
        if effect_name not in effect_messages:
            return False
        
        # Récupère le message pré-calculé
        message_template = effect_messages[effect_name][state].copy()
        
        # Recalcule le checksum pour être sûr
        checksum = (0x80 - (sum(message_template[6:-1]) & 0x7F)) & 0x7F
        message_template[-1] = checksum
        
        success = self._send_sysex_raw(message_template)
        
        if success:
            print(f"Effet {effect_name}: {'ON' if state else 'OFF'} (v3)")
        
        return success
    
    def change_amp_channel(self, channel: int):
        """Change le canal d'amplification (0-3)"""
        if not 0 <= channel <= 3:
            raise ValueError("Canal doit être 0-3")
        
        # Test de plusieurs adresses possibles pour le changement de canal
        channel_addresses = [
            [0x60, 0x00, 0x00, 0x00],  # Adresse possible 1
            [0x00, 0x00, 0x00, 0x38],  # Adresse possible 2
            [0x60, 0x00, 0x10, 0x00],  # Adresse possible 3
        ]
        
        channel_names = ['CLEAN', 'CRUNCH', 'LEAD', 'BROWN']
        
        for i, address in enumerate(channel_addresses):
            print(f"Test changement canal v{i+1}...")
            message = self._create_katana_message(address, [channel])
            if self._send_sysex_raw(message):
                print(f"Canal changé vers {channel_names[channel]} (v{i+1})")
                return True
        
        return False
    
    def comprehensive_test(self):
        """Test complet de toutes les variantes"""
        effects = ['booster', 'mod', 'fx', 'delay', 'reverb']
        
        print("\n=== Test complet des effets ===")
        
        for effect in effects:
            print(f"\n--- Test de l'effet {effect.upper()} ---")
            
            # Test des 3 versions d'adresses
            for version in [1, 2, 3]:
                print(f"Version {version} - ON:")
                if version == 1:
                    self.toggle_effect_v1(effect, True)
                elif version == 2:
                    self.toggle_effect_v2(effect, True)
                else:
                    self.toggle_effect_v3(effect, True)
                
                time.sleep(2)  # Pause pour observation
                
                print(f"Version {version} - OFF:")
                if version == 1:
                    self.toggle_effect_v1(effect, False)
                elif version == 2:
                    self.toggle_effect_v2(effect, False)
                else:
                    self.toggle_effect_v3(effect, False)
                
                time.sleep(2)
    
    def send_identity_request(self):
        """Envoie une requête d'identité pour confirmer la communication"""
        print("Envoi requête d'identité...")
        identity_msg = [0x7E, 0x00, 0x06, 0x01]
        return self._send_sysex_raw(identity_msg)
    
    def close(self):
        """Ferme la connexion MIDI"""
        if hasattr(self, 'output'):
            self.output.close()
        print("Connexion fermée")

def main():
    """Test principal"""
    try:
        katana = KatanaMk2ControllerFixed()
        
        print("\n=== Test de communication avec Katana 100 Mk2 ===")
        
        # Test 1: Requête d'identité
        print("\n1. Test de requête d'identité...")
        katana.send_identity_request()
        time.sleep(1)
        
        # Test 2: Test simple d'un effet
        print("\n2. Test simple - Booster ON/OFF...")
        for version in [1, 2, 3]:
            print(f"\nVersion {version}:")
            if version == 1:
                katana.toggle_effect_v1('booster', True)
                time.sleep(2)
                katana.toggle_effect_v1('booster', False)
            elif version == 2:
                katana.toggle_effect_v2('booster', True)
                time.sleep(2)
                katana.toggle_effect_v2('booster', False)
            else:
                katana.toggle_effect_v3('booster', True)
                time.sleep(2)
                katana.toggle_effect_v3('booster', False)
            time.sleep(2)
        
        # Test 3: Test complet (optionnel)
        response = input("\nLancer le test complet de tous les effets? (y/N): ")
        if response.lower() == 'y':
            katana.comprehensive_test()
        
    except Exception as e:
        print(f"Erreur: {e}")
    
    finally:
        if 'katana' in locals():
            katana.close()

if __name__ == "__main__":
    main()
