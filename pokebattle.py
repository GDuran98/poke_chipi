import random
from pfinal.pokeload import get_all_pokemons
from time import sleep


def get_player_profile(pokemon_list):
    return {
        "player_name": input("¿Cómo te llamas? "),
        "pokemon_inventory": [random.choice(pokemon_list) for a in range(3)],
        "battles": 0,
        "pokeballs": 1,
        "HP_potions": 1,
        "XP_points": 0,
    }


def any_player_pokemon_lives(player_profile):
    return sum([pokemon["current_health"] for pokemon in player_profile["pokemon_inventory"]])


def get_pokemon_info(pokemon):
    return "{} | Lvl: {} | HP: {}/{}".format(pokemon["name"],
                                          pokemon["level"],
                                          pokemon["current_health"],
                                          pokemon["base_health"])


def choose_pokemon(player_profile):
    chosen = None
    while not chosen:
        print("Elije un pokemon: ")
        for index in range(len(player_profile["pokemon_inventory"])):
            print("{} - {}".format(index, get_pokemon_info(player_profile["pokemon_inventory"][index])))
        try:
            return player_profile["pokemon_inventory"][int(input("¿Cuál eliges? "))]
        except (ValueError, IndexError):
            print("Elección inválida. Elige entre el 1 y el 3.")


def change_pokemon(player_profile, allow_fainted=False):
    while True:
        print("Elige un pokemon: ")
        available_pokemon = []
        for index, pokemon in enumerate(player_profile["pokemon_inventory"]):
            if allow_fainted or pokemon["current_health"] > 0:  # Solo muestra pokemons con vida
                available_pokemon.append((index, pokemon))
                print("{} - {}".format(index + 1, get_pokemon_info(pokemon)))

        if not available_pokemon:
            print("No tienes Pokémon disponibles para elegir.")
            return None

        try:
            choice = int(input("¿Cuál eliges? "))
            if 1 <= choice <= len(available_pokemon):
                index, chosen_pokemon = available_pokemon[choice - 1]
                return chosen_pokemon
            else:
                print("Elección inválida. Elige un número entre 1 y {}.".format(len(available_pokemon)))
        except ValueError:
            print("Entrada inválida. Introduce un número.")

def player_attack(player_pokemon, enemy_pokemon):
    if not player_pokemon["moves"]:  # Verifica si el Pokémon tiene movimientos
        print("{} no tiene movimientos para usar.".format(player_pokemon["name"]))
        return

    while True:
        print("Elige un ataque: ")
        for index, move in enumerate(player_pokemon["moves"]):
            print("{} - {} - (daño: {})".format(index + 1, move["name"], move["damage"]))
        try:
            choice = int(input("¿Cuál eliges? "))
            if 1 <= choice <= len(player_pokemon["moves"]):
                chosen_move = player_pokemon["moves"][choice - 1]
                damage = chosen_move["damage"]
                enemy_pokemon["current_health"] -= damage
                print("{} usa {} contra {} y le hace {} de daño.".format(player_pokemon["name"], chosen_move["name"],
                                                                         enemy_pokemon["name"], damage))
                if enemy_pokemon["current_health"] < 0:
                    enemy_pokemon["current_health"] = 0
                print("{} | HP: {}/{}".format(enemy_pokemon["name"], enemy_pokemon["current_health"],
                                              enemy_pokemon["base_health"]))
                return
            else:
                print("Elección inválida. Elige un número entre 1 y {}.".format(len(player_pokemon["moves"])))
        except ValueError:
            print("Entrada inválida. Introduce un número.")


def enemy_attack(enemy_pokemon, player_pokemon):
    if not enemy_pokemon["moves"]:  # Verifica si el Pokémon tiene movimientos
        print("{} no tiene movimientos para usar.".format(enemy_pokemon["name"]))
        return

    chosen_move = random.choice(enemy_pokemon["moves"])
    damage = chosen_move["damage"]
    player_pokemon["current_health"] -= damage
    print("{} usa {} contra {} y le hace {} de daño.".format(enemy_pokemon["name"], chosen_move["name"],
                                                             player_pokemon["name"], damage))
    if player_pokemon["current_health"] < 0:
        player_pokemon["current_health"] = 0
    print("{} | HP: {}/{}".format(player_pokemon["name"], player_pokemon["current_health"],
                                  player_pokemon["base_health"]))


def health_potion(player_profile, chosen_pokemon):
    if player_profile["HP_potions"] > 0:
        print("Tienes {} pociones de vida".format(player_profile["HP_potions"]))
        ans = input("¿Quieres gastar una poción? [S]i o [N]o: ").upper()
        if ans == "S":
            player_profile["HP_potions"] -= 1
            print("Ahora tienes {} pociones de vida".format(player_profile["HP_potions"]))
            print("Aumentando la vida del pokemon...")
            chosen_pokemon["current_health"] = min(chosen_pokemon["current_health"] + 50,
                                                   chosen_pokemon["base_health"])  # Evite sobrepasar la curación máxima
            print("Vida de {} aumentada a {}.".format(chosen_pokemon["name"], chosen_pokemon["current_health"]))
            return
        elif ans == "N":
            print("No has gastado ninguna poción de vida.")
            return
        else:
            print("Respuesta inválida.")
    else:
        print("No tienes pociones de vida.")


def catch_pokemon(player_profile, enemy_pokemon):
    if player_profile["pokeballs"] <= 0:  # Verifica si el jugador tiene Pokeballs
        print("No tienes Pokeballs.")
        return False

    player_profile["pokeballs"] -= 1  # Resta una Pokeball

    health_percentage = (enemy_pokemon["current_health"] / enemy_pokemon["base_health"]) * 100

    if health_percentage > 80:
        catch_rate = 5
    elif 60 < health_percentage <= 80:
        catch_rate = 15
    elif 40 < health_percentage <= 60:
        catch_rate = 25
    elif 20 < health_percentage <= 40:
        catch_rate = 45
    else:
        catch_rate = 85

    print("Lanzando Pokeball... (Te quedan {} Pokeballs)".format(player_profile["pokeballs"]))
    if random.randint(1, 100) <= catch_rate:
        print("¡Atrapaste a {}!".format(enemy_pokemon["name"]))
        player_profile["pokemon_inventory"].append(enemy_pokemon)
        return True
    else:
        print("{} se ha escapado de la Pokeball.".format(enemy_pokemon["name"]))
        return False


def player_pokemon_faint(player_profile, player_pokemon, enemy_pokemon):
    """Revisa si el Pokémon del jugador se debilita."""
    if player_pokemon["current_health"] <= 0:
        print("{} ha sido derrotado!".format(player_pokemon["name"]))
        new_pokemon = change_pokemon(player_profile)
        if new_pokemon is None:
            print("Te has quedado sin Pokémon disponibles para combatir.")
            return True, enemy_pokemon["name"]  # Batalla terminada, devuelve ganador
        print("Entra {} en combate".format(new_pokemon["name"]))
        return False, new_pokemon  # Batalla continúa, devuelve nuevo Pokémon
    return False, player_pokemon #Devuelve el mismo pokemon si no se ha debilitado


def evolve_pokemon(pokemon):
    """Intenta evolucionar al Pokémon si cumple las condiciones."""
    if pokemon["level"] % 5 == 0 and pokemon.get("evolves_to"): #verifica si el nivel es multiplo de 5 y si tiene evolucion
        evolved_name = pokemon["evolves_to"]
        print("{} está evolucionando a {}!".format(pokemon["name"], evolved_name))

        # Buscar la información del Pokémon evolucionado en la lista de todos los Pokémon
        all_pokemons = get_all_pokemons()
        evolved_pokemon_data = next((p for p in all_pokemons if p["name"] == evolved_name), None)

        if evolved_pokemon_data:
            # Crea un nuevo diccionario para el Pokémon evolucionado
            evolved_pokemon = evolved_pokemon_data.copy()
            evolved_pokemon["current_health"] = evolved_pokemon["base_health"]
            evolved_pokemon["level"] = pokemon["level"]
            print("{} ha evolucionado a {}!".format(pokemon["name"], evolved_name))
            return evolved_pokemon
        else:
            print("No se encontró información para {} en la base de datos.".format(evolved_name))
            return pokemon #retorna el mismo pokemon en caso de no encontrarlo
    return pokemon #retorna el mismo pokemon si no cumple las condiciones


def lottery(player_profile, last_battle_winner):
    """Simula una lotería donde el jugador puede ganar una Pokeball, una Poción de Vida o subir de nivel a un Pokémon."""

    gifts = ["pokeball", "potion", "level_up"]
    gift_gain = random.choice(gifts)

    print("¡Has participado en la lotería!")

    if gift_gain == "pokeball":
        player_profile["pokeballs"] += 1
        print("¡Has ganado una Pokeball! Ahora tienes {} Pokeballs.".format(player_profile["pokeballs"]))
    elif gift_gain == "potion":
        player_profile["HP_potions"] += 1
        print("¡Has ganado una Poción de Vida! Ahora tienes {} Pociones de Vida.".format(player_profile["HP_potions"]))
    elif gift_gain == "level_up":
        if last_battle_winner:  # Comprueba que el ganador existe
            print("Intentando subir de nivel a {}".format(last_battle_winner["name"]))
            last_level = last_battle_winner.get("level", 1)
            last_battle_winner["level"] = last_level + 1
            last_battle_winner["base_health"] += 100
            last_battle_winner["current_health"] = last_battle_winner["base_health"]
            print(
                "¡{} ha subido de nivel a {}, su salud base ha aumentado a {} y su salud actual se ha recuperado al máximo!".format(
                    last_battle_winner["name"], last_battle_winner["level"], last_battle_winner["base_health"]))
            evolve_pokemon(last_battle_winner)
        else:
            print("No hay Pokémon ganador para subir de nivel.")

    input("Presiona ENTER para continuar")

def check_heal_enemy_up(player_profile, pokemon_list):
    """Verifica si el número de combates es múltiplo de 5, cura a los Pokémon del jugador y aumenta la vida de los enemigos, si es el caso."""
    if player_profile["battles"] > 0 and player_profile["battles"] % 5 == 0:
        print("¡Has superado 5 combates seguidos!")
        sleep(0.5)
        if player_profile["pokemon_inventory"]:
            for i, pokemon in enumerate(player_profile["pokemon_inventory"]):
                pokemon["current_health"] = pokemon["base_health"]
                player_profile["pokemon_inventory"][i] = evolve_pokemon(pokemon) #intenta evolucionar
            print("¡Todos tus Pokémon han sido curados!")
        else:
            print("No tienes Pokémon que curar.")

        for pokemon in pokemon_list:
            pokemon["base_health"] += 100
            if pokemon["current_health"] > 0:
                pokemon["current_health"] = pokemon["base_health"]
        print("La vida base de los pokemons rivales ha aumentado")

        input("Presiona ENTER para continuar")


def show_inventory(player_profile):
    print("--- INVENTARIO ---")
    print("Pokeballs: {}".format(player_profile['pokeballs']))
    print("Pociones: {}".format(player_profile['HP_potions']))
    if player_profile["pokemon_inventory"]:
        print("Pokémon:")
        for i, pokemon in enumerate(player_profile["pokemon_inventory"]):
            print("{}. {}".format(i+1, get_pokemon_info(pokemon)))
    else:
        print("No tienes Pokémon en tu inventario.")
    print("-" * 25)

def show_battle_summary(battle_number, winner):
    print("--- RESUMEN DEL COMBATE {} ---".format(battle_number))
    if winner:
        print("El ganador es: {}".format(winner["name"]))
    else:
        print("El combate terminó en empate o se interrumpió.")
    print("-" * 25)

def battle(player_profile, pokemon_list):
    player_profile["battles"] += 1
    battle_number = player_profile["battles"]
    print("--- COMIENZA EL COMBATE {} ---".format(battle_number))
    player_pokemon = choose_pokemon(player_profile)
    if player_pokemon is None:
        print("No tienes Pokémon disponibles para combatir.")
        show_battle_summary(battle_number, None) # Muestra resumen con ganador None
        return None  # Importante: Retornar None para indicar que no hubo batalla

    enemy_pokemon = random.choice(pokemon_list).copy()
    enemy_pokemon["current_health"] = enemy_pokemon["base_health"]

    print("Se enfrentarán {} y {}.".format(get_pokemon_info(player_pokemon), get_pokemon_info(enemy_pokemon)))

    winner_pokemon = None
    battle_ended = False

    while any_player_pokemon_lives(player_profile) and enemy_pokemon["current_health"] > 0:
        action = None
        while action not in ["A", "P", "V", "C", "I", "H"]:
            print("[A]tacar             Poción de [V]ida")
            print("[P]okeball           [C]ambiar pokemon")
            print("[I]nventario         [H]uir y finalizar")
            action = input("¿Que deseas hacer?: ").upper()

        if action == "A":
            player_attack(player_pokemon, enemy_pokemon)
            if enemy_pokemon["current_health"] > 0:
                enemy_attack(enemy_pokemon, player_pokemon)
            battle_ended, player_pokemon = player_pokemon_faint(player_profile, player_pokemon, enemy_pokemon)
            if battle_ended:
                break

        elif action == "P":
            if catch_pokemon(player_profile, enemy_pokemon):
                break
            else:
                enemy_attack(enemy_pokemon, player_pokemon)
            battle_ended, player_pokemon = player_pokemon_faint(player_profile, player_pokemon, enemy_pokemon)
            if battle_ended:
                break

        elif action == "V":
            health_potion(player_profile, player_pokemon)
            if enemy_pokemon["current_health"] > 0:
                enemy_attack(enemy_pokemon, player_pokemon)
            battle_ended, player_pokemon = player_pokemon_faint(player_profile, player_pokemon, enemy_pokemon)
            if battle_ended:
                break

        elif action == "C":
            new_pokemon = choose_pokemon(player_profile)
            if new_pokemon is not None and new_pokemon != player_pokemon:
                player_pokemon = new_pokemon
                print("Has cambiado a {}".format(get_pokemon_info(player_pokemon)))
                if enemy_pokemon["current_health"] > 0:
                    enemy_attack(enemy_pokemon, player_pokemon)
            elif new_pokemon == player_pokemon:
                print("Ya tienes a ese pokemon en combate")
            else:
                print("No se ha podido cambiar de pokemon")
            battle_ended, player_pokemon = player_pokemon_faint(player_profile, player_pokemon, enemy_pokemon)
            if battle_ended:
                break

        elif action == "I":
            show_inventory(player_profile)

        elif action == "H":
            show_battle_summary(battle_number, winner_pokemon)
            exit(True)

        else:
            print("Elije una de las opciones validas.")
    if enemy_pokemon["current_health"] <= 0:
        winner_pokemon = player_pokemon  # Pasar el diccionario completo
        print("{} ha sido derrotado!".format(enemy_pokemon["name"]))
        check_heal_enemy_up(player_profile, pokemon_list)
        lottery(player_profile, last_battle_winner=winner_pokemon)
    elif not any_player_pokemon_lives(player_profile):
        winner_name = enemy_pokemon["name"]
        print("Te has quedado sin pokemon disponibles!")
    elif not any_player_pokemon_lives(player_profile) and enemy_pokemon["current_health"] <= 0:
      print("Ha sido un empate")

    show_battle_summary(battle_number, winner_pokemon)
    print("--- EL COMBATE HA FINALIZADO ---")
    sleep(1)
    input("Presiona ENTER para continuar.")
    return winner_pokemon

def main():
    pokemon_list = get_all_pokemons() # Lista todos los pokemons
    player_profile = get_player_profile(pokemon_list) # Genera un perfil del jugador
    print("Bienvenido {}".format(player_profile["player_name"]))
    print("Se te han asignado estos 3 pokemons para poder combatir: ")
    for i, pokemon in enumerate(player_profile["pokemon_inventory"]):
        print("-------------------------------------------------")
        print("Datos de {}".format(pokemon["name"]))
        print("Es de tipo: {}".format(pokemon["type"]))
        print("Nivel de experiencia: {}".format(pokemon["level"]))
        print("Vida actual: {}".format(pokemon["current_health"]))
        print("Sus movimientos son:".format(pokemon["moves"]))
        if pokemon["moves"]:
            for move in pokemon["moves"]:
                print("- {} (Tipo: {}, Daño: {})".format(move['name'], move['type'], move['damage']))
        sleep(1)

    print("\n")
    print("\n")
    while any_player_pokemon_lives(player_profile): # Combates hasta perder todos los pokemons
        battle(player_profile, pokemon_list)
    print("Te has quedado sin pokemon disponibles!")


if __name__ == "__main__":
    main()