#!/usr/bin/env python3
"""
Outil de diagnostic pour Katana 100 Mk2
Permet de capturer les messages MIDI réels et tester différentes adresses
"""

import mido
import time
import threading
from typing import List

class KatanaDebugger:
    def __init__(self, port_name: str = None):
        self.device_id = 0x00
        self.listening = False
        
        # Détection du port Katana
        if port_name is None:
            ports = mido.get_output_names()
            katana_ports = [p for p in ports if 'katana' in p.lower() or 'boss' in p.lower()]
            if katana_ports:
                port_name = katana_ports[0]
                print(f"Port Katana détecté: {port_name}")
            else:
                print("Ports disponibles:")
                for i, port in enumerate(ports):
                    print(f"{i}: {port}")
                return
        
        try:
            self.output = mido.open_output(port_name)
            self.input = mido.open_input(port_name)
            print(f"Connecté au Katana sur: {port_name}")
        except Exception as e:
            print(f"Erreur de connexion: {e}")
            return
    
    def listen_midi(self):
        """Écoute et affiche tous les messages MIDI reçus"""
        print("Démarrage de l'écoute MIDI...")
        print("Manipulez les contrôles de l'ampli pour voir les messages...")
        print("Appuyez sur Ctrl+C pour arrêter\n")
        
        self.listening = True
        try:
            while self.listening:
                for msg in self.input.iter_pending():
                    if msg.type == 'sysex':
                        print(f"SysEx reçu: {' '.join([f'{x:02X}' for x in msg.data])}")
                        self.decode_sysex(msg.data)
                    else:
                        print(f"MIDI: {msg}")
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.listening = False
            print("\nArrêt de l'écoute")
    
    def decode_sysex(self, data: List[int]):
        """Décode un message SysEx Roland"""
        if len(data) < 8:
            return
        
        if data[0] == 0x41:  # Roland
            device_id = data[1]
            model_id = data[2:6]
            command = data[6]
            
            print(f"  Roland - Device ID: {device_id:02X}, Model: {' '.join([f'{x:02X}' for x in model_id])}")
            print(f"  Commande: {command:02X}")
            
            if len(data) > 8:
                address = data[7:-1]  # Tout sauf le checksum
                print(f"  Adresse/Données: {' '.join([f'{x:02X}' for x in address])}")
    
    def send_test_sysex(self, data: List[int]):
        """Envoie un message SysEx de test"""
        try:
            msg = mido.Message('sysex', data=data)
            self.output.send(msg)
            print(f"Envoyé: {' '.join([f'{x:02X}' for x in data])}")
            time.sleep(0.1)
        except Exception as e:
            print(f"Erreur d'envoi: {e}")
    
    def test_known_addresses(self):
        """Test des adresses SysEx connues pour Katana"""
        print("Test des adresses connues pour Katana 100 Mk2...")
        
        # Différentes variations d'ID de modèle pour Katana Mk2
        model_variations = [
            [0x00, 0x00, 0x00, 0x33],  # Katana générique
            [0x00, 0x00, 0x00, 0x6A],  # Katana Mk2 100W
            [0x00, 0x00, 0x00, 0x6B],  # Autre variation
        ]
        
        # Test de requête d'identité
        print("\n1. Test de requête d'identité...")
        identity_request = [0x7E, 0x00, 0x06, 0x01]
        self.send_test_sysex(identity_request)
        time.sleep(0.5)
        
        for model_id in model_variations:
            print(f"\n2. Test avec Model ID: {' '.join([f'{x:02X}' for x in model_id])}")
            
            # Test d'activation/désactivation d'effets avec différentes adresses
            effect_tests = [
                # Format: (nom, adresse_possible)
                ("Booster ON", [0x60, 0x00, 0x11, 0x00]),
                ("Booster OFF", [0x60, 0x00, 0x11, 0x01]),
                ("Mod ON", [0x60, 0x00, 0x12, 0x00]),
                ("Mod OFF", [0x60, 0x00, 0x12, 0x01]),
                ("FX ON", [0x60, 0x00, 0x13, 0x00]),
                ("FX OFF", [0x60, 0x00, 0x13, 0x01]),
                ("Delay ON", [0x60, 0x00, 0x14, 0x00]),
                ("Delay OFF", [0x60, 0x00, 0x14, 0x01]),
                ("Reverb ON", [0x60, 0x00, 0x15, 0x00]),
                ("Reverb OFF", [0x60, 0x00, 0x15, 0x01]),
            ]
            
            for test_name, address in effect_tests:
                # Construction du message Roland complet
                header = [0x41, 0x00] + model_id + [0x12]
                message_body = header + address + [0x01]  # Valeur ON/OFF
                checksum = (0x80 - (sum(message_body[6:]) & 0x7F)) & 0x7F
                full_message = message_body + [checksum]
                
                print(f"  Test {test_name}...")
                self.send_test_sysex(full_message)
                time.sleep(1)  # Pause pour voir l'effet
        
        # Test d'adresses alternatives trouvées dans la communauté
        print("\n3. Test d'adresses alternatives...")
        alternative_tests = [
            # Adresses basées sur les découvertes communautaires
            ([0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x11, 0x00, 0x01], "Booster ON v2"),
            ([0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x11, 0x00, 0x00], "Booster OFF v2"),
            ([0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x12, 0x00, 0x01], "Mod ON v2"),
            ([0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x12, 0x60, 0x00, 0x15, 0x00, 0x01], "Reverb ON v2"),
        ]
        
        for test_data, test_name in alternative_tests:
            # Recalcul du checksum
            checksum = (0x80 - (sum(test_data[6:-1]) & 0x7F)) & 0x7F
            test_data[-1] = checksum
            
            print(f"  {test_name}...")
            self.send_test_sysex(test_data)
            time.sleep(1)
    
    def interactive_hex_sender(self):
        """Interface interactive pour envoyer des messages SysEx personnalisés"""
        print("\n=== Envoi de messages SysEx personnalisés ===")
        print("Entrez les données en hexadécimal (ex: 41 00 00 00 00 33 12 60 00 11 00 01)")
        print("Tapez 'quit' pour quitter, 'listen' pour écouter, 'test' pour les tests automatiques")
        
        while True:
            try:
                user_input = input("HEX> ").strip()
                
                if user_input.lower() == 'quit':
                    break
                elif user_input.lower() == 'listen':
                    self.listen_midi()
                elif user_input.lower() == 'test':
                    self.test_known_addresses()
                elif user_input:
                    # Conversion hex vers bytes
                    hex_values = user_input.replace(',', ' ').split()
                    data = [int(x, 16) for x in hex_values]
                    self.send_test_sysex(data)
                
            except ValueError:
                print("Format invalide. Utilisez des valeurs hexadécimales séparées par des espaces.")
            except KeyboardInterrupt:
                break
    
    def dump_current_settings(self):
        """Demande le dump des réglages actuels"""
        print("Demande de dump des réglages...")
        
        # Requête de dump Roland standard
        dump_requests = [
            [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x11, 0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20],
            [0x41, 0x00, 0x00, 0x00, 0x00, 0x33, 0x11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00],
        ]
        
        for i, request in enumerate(dump_requests):
            # Calcul du checksum
            checksum = (0x80 - (sum(request[6:]) & 0x7F)) & 0x7F
            full_request = request + [checksum]
            
            print(f"Envoi requête dump {i+1}...")
            self.send_test_sysex(full_request)
            time.sleep(2)
    
    def close(self):
        """Ferme les connexions"""
        self.listening = False
        if hasattr(self, 'output'):
            self.output.close()
        if hasattr(self, 'input'):
            self.input.close()

def main():
    debugger = KatanaDebugger()
    
    if not hasattr(debugger, 'output'):
        return
    
    try:
        print("\n=== Katana Debug Tool ===")
        print("1. Test automatique des adresses connues")
        print("2. Écoute des messages MIDI")
        print("3. Dump des réglages actuels")
        print("4. Mode interactif (envoi manuel)")
        
        choice = input("\nChoisissez une option (1-4): ").strip()
        
        if choice == '1':
            debugger.test_known_addresses()
        elif choice == '2':
            debugger.listen_midi()
        elif choice == '3':
            debugger.dump_current_settings()
            debugger.listen_midi()
        elif choice == '4':
            debugger.interactive_hex_sender()
        else:
            print("Option invalide")
    
    except KeyboardInterrupt:
        pass
    finally:
        debugger.close()

if __name__ == "__main__":
    main()
