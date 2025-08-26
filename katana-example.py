#!/usr/bin/env python3
"""
Exemple simple d'utilisation du contrôleur Katana Mk2
"""

from katana_controller import KatanaMk2Controller
import time

def simple_example():
    """Exemple basique d'utilisation"""
    
    # Connexion au Katana (détection automatique du port)
    katana = KatanaMk2Controller()
    
    try:
        # Passage au canal LEAD
        katana.change_channel(2)  # 0=CLEAN, 1=CRUNCH, 2=LEAD, 3=BROWN
        
        # Réglage du volume à 70%
        katana.set_master_volume(70)
        
        # Réglage du gain
        katana.set_gain(85)
        
        # Configuration de l'EQ
        katana.set_eq(bass=60, mid=75, treble=80)
        
        # Activation de quelques effets
        katana.toggle_effect('delay', True)
        katana.toggle_effect('reverb', True)
        katana.toggle_effect('booster', True)
        
        print("Configuration appliquée avec succès !")
        
        # Optionnel: sauvegarder dans un preset
        # katana.preset_save(1)
        
    except Exception as e:
        print(f"Erreur: {e}")
    
    finally:
        katana.close()

def preset_manager():
    """Gestionnaire de presets"""
    
    katana = KatanaMk2Controller()
    
    try:
        # Création de différents presets
        
        # Preset 1: Clean Jazz
        print("Création preset 1: Clean Jazz")
        katana.change_channel(0)  # CLEAN
        katana.set_master_volume(50)
        katana.set_gain(30)
        katana.set_eq(bass=70, mid=60, treble=75)
        katana.toggle_effect('reverb', True)
        katana.toggle_effect('mod', True)  # Pour un effet chorus léger
        katana.preset_save(1)
        
        time.sleep(1)
        
        # Preset 2: Rock Crunch
        print("Création preset 2: Rock Crunch")
        katana.change_channel(1)  # CRUNCH
        katana.set_master_volume(75)
        katana.set_gain(65)
        katana.set_eq(bass=65, mid=70, treble=70)
        katana.toggle_effect('booster', True)
        katana.toggle_effect('delay', True)
        katana.preset_save(2)
        
        time.sleep(1)
        
        # Preset 3: Heavy Lead
        print("Création preset 3: Heavy Lead")
        katana.change_channel(2)  # LEAD
        katana.set_master_volume(80)
        katana.set_gain(90)
        katana.set_eq(bass=60, mid=80, treble=75)
        katana.toggle_effect('booster', True)
        katana.toggle_effect('delay', True)
        katana.toggle_effect('reverb', True)
        katana.preset_save(3)
        
        print("Presets créés avec succès !")
        
        # Test de chargement des presets
        print("\nTest de chargement des presets:")
        for i in range(1, 4):
            print(f"Chargement preset {i}...")
            katana.preset_load(i)
            time.sleep(2)
        
    except Exception as e:
        print(f"Erreur: {e}")
    
    finally:
        katana.close()

def interactive_controller():
    """Contrôleur interactif en ligne de commande"""
    
    katana = KatanaMk2Controller()
    
    try:
        print("\n=== Contrôleur Katana Mk2 Interactif ===")
        print("Commandes disponibles:")
        print("  ch <0-3>     - Changer de canal (0=CLEAN, 1=CRUNCH, 2=LEAD, 3=BROWN)")
        print("  vol <0-100>  - Régler le volume")
        print("  gain <0-100> - Régler le gain")
        print("  bass <0-100> - Régler les basses")
        print("  mid <0-100>  - Régler les médiums")
        print("  treble <0-100> - Régler les aigus")
        print("  fx <effet> <on/off> - Toggle effet (booster, mod, fx, delay, reverb)")
        print("  save <1-4>   - Sauvegarder preset")
        print("  load <1-4>   - Charger preset")
        print("  quit         - Quitter")
        print()
        
        while True:
            try:
                cmd = input("Katana> ").strip().split()
                if not cmd:
                    continue
                
                if cmd[0].lower() == 'quit':
                    break
                
                elif cmd[0].lower() == 'ch' and len(cmd) == 2:
                    katana.change_channel(int(cmd[1]))
                
                elif cmd[0].lower() == 'vol' and len(cmd) == 2:
                    katana.set_master_volume(int(cmd[1]))
                
                elif cmd[0].lower() == 'gain' and len(cmd) == 2:
                    katana.set_gain(int(cmd[1]))
                
                elif cmd[0].lower() == 'bass' and len(cmd) == 2:
                    katana.set_eq(bass=int(cmd[1]))
                
                elif cmd[0].lower() == 'mid' and len(cmd) == 2:
                    katana.set_eq(mid=int(cmd[1]))
                
                elif cmd[0].lower() == 'treble' and len(cmd) == 2:
                    katana.set_eq(treble=int(cmd[1]))
                
                elif cmd[0].lower() == 'fx' and len(cmd) == 3:
                    effect = cmd[1].lower()
                    state = cmd[2].lower() == 'on'
                    katana.toggle_effect(effect, state)
                
                elif cmd[0].lower() == 'save' and len(cmd) == 2:
                    katana.preset_save(int(cmd[1]))
                
                elif cmd[0].lower() == 'load' and len(cmd) == 2:
                    katana.preset_load(int(cmd[1]))
                
                else:
                    print("Commande inconnue ou arguments incorrects")
                
            except (ValueError, IndexError) as e:
                print(f"Erreur dans la commande: {e}")
            except KeyboardInterrupt:
                break
    
    except Exception as e:
        print(f"Erreur: {e}")
    
    finally:
        katana.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'simple':
            simple_example()
        elif sys.argv[1] == 'presets':
            preset_manager()
        elif sys.argv[1] == 'interactive':
            interactive_controller()
        else:
            print("Options: simple, presets, interactive")
    else:
        print("Usage: python katana_simple_example.py [simple|presets|interactive]")
