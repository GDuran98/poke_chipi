import pickle
import requests


def get_in_spanish(url):
    #Obtiene el nombre en español desde una URL de la PokeAPI.
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for name in data['names']:
            if name['language']['name'] == 'es':
                return name['name']
        return None
    except requests.exceptions.RequestException as e:
        print("Error al obtener datos de la API: {}".format(e))
        return None
    except KeyError as e:
        print("Error al procesar los datos JSON (clave faltante): {}".format(e))
        return None

def get_moves(url_movement):
    # Obtiene el nombre, tipo y daño de un movimiento en español, solo si tiene daño.
    try:
        move_response = requests.get(url_movement)
        move_response.raise_for_status()
        move_data = move_response.json()

        # Verificar si el movimiento tiene daño
        if 'power' not in move_data or move_data['power'] is None:
            return None  # Devuelve None si no tiene daño

        move_name = get_in_spanish(url_movement)

        move_type = get_in_spanish(move_data['type']['url']) if 'type' in move_data else "No tiene tipo"

        move_dmg = move_data['power']

        return {
            "name": move_name,
            "type": move_type,
            "damage": move_dmg
        }
    except requests.exceptions.RequestException as e:
        print("Error al obtener datos del movimiento: {}".format(e))
        return None
    except KeyError as e:
        print("Error al procesar los datos del movimiento JSON (clave faltante): {}".format(e))
        return None

def get_evolution_chain(species_url):
    try:
        species_response = requests.get(species_url)
        species_response.raise_for_status()
        species_data = species_response.json()

        evolution_chain_url = species_data.get('evolution_chain', {}).get('url') # Manejo si no existe 'evolution_chain'

        if not evolution_chain_url: # Si evolution_chain_url es None o vacío
            print("Este Pokémon no tiene cadena de evolución.")
            return [] # Devuelve una lista vacía

        evolution_chain_response = requests.get(evolution_chain_url)
        evolution_chain_response.raise_for_status()
        evolution_chain_data = evolution_chain_response.json()

        chain = evolution_chain_data.get('chain')
        if not chain:
            print("Error: Estructura de cadena de evolución inesperada.")
            return []

        evolutions = []
        while chain:
            species_name = chain.get('species', {}).get('name')
            if species_name:
                evolution_name = get_in_spanish(f"https://pokeapi.co/api/v2/pokemon-species/{species_name}")
                if evolution_name:
                    evolutions.append(evolution_name)

            evolves_to = chain.get('evolves_to', [])
            if evolves_to:
                chain = evolves_to[0]  # Avanza a la siguiente evolución
            else:
                chain = None # Termina el bucle si no hay más evoluciones
        return evolutions

    except requests.exceptions.RequestException as e:
        print("Error al obtener la cadena de evolución: {}".format(e))
        return None
    except KeyError as e:
        print("Error al procesar la cadena de evolución JSON: {}".format(e))
        return None
    except AttributeError as e: #Manejo de errores por atributo inexistente
        print("Error de atributo en la cadena de evolución: {}".format(e))
        return None

def get_pokemon_data(pokemon_id):
    pokemon_base = {
        "name": "",
        "current_health": 100,
        "base_health": 100,
        "level": 1,
        "current_XP": 0,
        "type": None,
        "moves": None,
        "evolves": []
    }

    try:
        url_pokemon = "https://pokeapi.co/api/v2/pokemon/{}".format(pokemon_id)
        pokemon_response = requests.get(url_pokemon)
        pokemon_response.raise_for_status()
        pokemon_data = pokemon_response.json()

        pokemon_base["name"] = get_in_spanish(pokemon_data['species']['url'])

        spanish_types = []
        for type in pokemon_data['types']:
            spanish_type_name = get_in_spanish(type['type']['url'])
            if spanish_type_name:
                spanish_types.append(spanish_type_name)

        pokemon_base["type"] = spanish_types

        movement_specs = []
        num_moves = 0
        for move in pokemon_data['moves']:
            if num_moves >= 4:
                break

            detail_movement = get_moves(move['move']['url'])
            if detail_movement:
                movement_specs.append(detail_movement)
                num_moves += 1

        pokemon_base["moves"] = movement_specs

        evolution_chain = get_evolution_chain(pokemon_data['species']['url'])
        if evolution_chain:
            pokemon_base["evolves"] = evolution_chain

        return pokemon_base

    except requests.exceptions.RequestException as e:
        print("Error al obtener datos del Pokémon {}: {}".format(pokemon_id, e))
        return None
    except KeyError as e:
        print("Error al procesar los datos del Pokémon {} JSON (clave faltante): {}".format(pokemon_id, e))
        return None

def get_all_pokemons():
    try:
        print("Cargando archivo de pokemons...")
        with open("pokefile.pkl", "rb") as pokefile:
            all_pokemons = pickle.load(pokefile)
            return all_pokemons
    except FileNotFoundError:
        print("Archivo no encontrado. Generando archivo...")
        all_pokemons = []
        for i in range(1, 152):
            file = get_pokemon_data(i)
            if file:
                all_pokemons.append(file)
                print("Guardando datos del pokemon {}...".format(i))  # .format() aquí
                for index, pokemon in enumerate(all_pokemons): #Cambio de i a index para evitar confusion
                    print("Datos de {}".format(pokemon["name"]))
                    print("Es de tipo: {}".format(pokemon["type"]))
                    print("Nivel de experiencia: {}".format(pokemon["level"]))
                    print("Vida actual: {}".format(pokemon["current_health"]))
                    print("Sus movimientos son:")
                    if pokemon["moves"]:
                        for move in pokemon["moves"]:
                            print("- {} (Tipo: {}, Daño: {})".format(move['name'], move['type'], move['damage'])) # .format() aquí
                    print("Evoluciones: {}".format(pokemon["evolves"]))
                    print("-------------------------------------------------")
            else:
                print("No se pudo crear la ficha para el Pokémon {}.".format(i)) # .format() aquí

        with open("pokefile.pkl", "wb") as pokefile:
            pickle.dump(all_pokemons, pokefile)
        return all_pokemons


get_all_pokemons()

