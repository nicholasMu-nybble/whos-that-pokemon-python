import pokebase as pb
import pygame
import requests
import sys
from io import BytesIO
import random
import json
import time
from PIL import Image
import threading

class CustomThread(threading.Thread):
    # by Biren Mer from https://medium.com/@birenmer/threading-the-needle-returning-values-from-python-threads-with-ease-ace21193c148
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, verbose=None):
        # Initializing the Thread class
        super().__init__(group, target, name, args, kwargs)
        self._return = None

    # Overriding the Thread.run function
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self):
        super().join()
        return self._return

def silhouette(surface):
    result = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    result.fill((0, 0, 0, 255))
    result.blit(surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return result

class GameState:
    def __init__(self, full_list):
        self.pokemon_chosen: bool = False
        self.pokemon_list: list = full_list
        random.shuffle(self.pokemon_list)
        self.pokemon_guessed: bool = False
        self.guess: str = ''
        self.index: int = -1
        self.game_start: float = time.time()
        self.adjusted_game_start: float = 0
        self.randomize_after: bool = True
        self.specific_mode: bool = False
        self.fast_mode: bool = False

    def reset(self, new_list: list, randomize: bool | None = None) -> None:
        if randomize is None:
            randomize = self.randomize_after
        self.pokemon_list = new_list
        self.randomize_after = randomize
        if self.randomize_after:
            random.shuffle(self.pokemon_list)
        self.index = -1
        self.pokemon_chosen = False
        self.game_start = time.time()
        self.adjusted_game_start = 0

class Pokemon:
    def __init__(self, pokemon_name, pokemon_data):
        self.data = pokemon_data[pokemon_name]
        self.id = pokemon_name
        self.species_name = "".join(char for char in self.data["species_name"] if char.isalnum())
        if "aliases" in self.data:
            self.aliases = ["".join(char for char in alias.lower() if char.isalnum()) for alias in (self.data["aliases"] + [self.id])]
        else:
            self.aliases = []

        self.qualifiers = self.data["qualifiers"] if "qualifiers" in self.data else []
        self.qualifiers = ["".join(char for char in qualifier.lower() if char.isalnum()) for qualifier in self.qualifiers]

        # get the image
        self.sprite_address = self.data["image_link"]
        self.response = requests.get(self.sprite_address)
        self.pil_image = Image.open(BytesIO(self.response.content)).convert("RGBA")
        self.img = pygame.image.frombytes(self.pil_image.tobytes(), self.pil_image.size, self.pil_image.mode)
        if self.img.get_size() != (475, 475):
            self.img = pygame.transform.scale(self.img, (475, 475))
        self.shadow_img = silhouette(self.img)

    def guess(self, guess: str, require_qualifiers: bool = False) -> bool:
        guessed_name = "".join(char for char in guess.lower() if char.isalnum())
        if require_qualifiers:
            for qualifier in self.qualifiers:
                if qualifier not in guessed_name:
                    return False
        return guessed_name == self.species_name or guessed_name in self.aliases

def get_next_pokemon(state: GameState, pokemon_data: dict):
    if state.index + 1 < len(state.pokemon_list):
        return Pokemon(state.pokemon_list[state.index + 1], pokemon_data)
    else:
        return Pokemon(state.pokemon_list[0], pokemon_data)

def main():
    pokemon_list = [p['name'] for p in pb.APIResourceList('pokemon')]

    with open('pokemon_data.json', 'r') as file:
        pokemon_data = json.load(file)

    print("Checking for Updates...")

    json_changed = False
    for name in pokemon_list:
        if name not in pokemon_data:
            print(f"Adding {name}.")
            pokemon_resource = pb.pokemon(name)
            pokemon_data[name] = (pokemon_resource.species.name, pokemon_resource.sprites.other.official_artwork.front_default)
            json_changed = True

    if json_changed:
        with open('pokemon_data.json', 'w') as file:
            json.dump(pokemon_data, file, indent = 4)

    for name in pokemon_data:
        if name not in pokemon_list:
            pokemon_list.append(name)

    full_pokemon_list = [pokemon for pokemon in pokemon_list if "skip" not in pokemon_data[pokemon] or not pokemon_data[pokemon]["skip"]]
    pokerap_list = ["electrode", "diglett", "nidoran-m", "mankey",
                "venusaur", "rattata", "fearow", "pidgey",
                "seaking", "jolteon", "dragonite", "gastly",
                "ponyta", "vaporeon", "poliwrath", "butterfree",

                "venomoth", "poliwag", "nidorino", "golduck",
                "ivysaur", "grimer", "victreebel", "moltres",
                "nidoking", "farfetchd", "abra", "jigglypuff",
                "kingler", "rhyhorn", "clefable", "wigglytuff",

                "zubat", "primeape", "meowth", "onix",
                "geodude", "rapidash", "magneton", "snorlax",
                "gengar", "tangela", "goldeen", "spearow",
                "weezing", "seel", "gyarados", "slowbro",

                "kabuto", "persian", "paras", "horsea",
                "raticate", "magnemite", "kadabra", "weepinbell",
                "ditto", "cloyster", "caterpie", "sandshrew",
                "bulbasaur", "charmander", "golem", "pikachu",

                "alakazam", "doduo", "venonat", "machoke",
                "kangaskhan", "hypno", "electabuzz", "flareon",
                "blastoise", "poliwhirl", "oddish", "drowzee",
                "raichu", "nidoqueen", "bellsprout", "starmie",

                "metapod", "marowak", "kakuna", "clefairy",
                "dodrio", "seadra", "vileplume", "krabby",
                "lickitung", "tauros", "weedle", "nidoran-f",
                "machop", "shellder", "porygon", "hitmonchan",

                "articuno", "jynx", "nidorina", "beedrill",
                "haunter", "squirtle", "chansey", 
                "parasect", "exeggcute", "muk", "dewgong",
                "pidgeotto", "lapras", "vulpix", "rhydon",

                "charizard", "machamp", "pinsir", "koffing",
                "dugtrio", "golbat", "staryu", "magikarp",
                "ninetales", "ekans", "omastar",
                "scyther", "tentacool", "dragonair", "magmar",

                "sandslash", "hitmonlee", "psyduck", "arcanine",
                "eevee", "exeggutor", "kabutops", "zapdos",
                "dratini", "growlithe", "mr-mime", "cubone",
                "graveler", "voltorb", "gloom",

                "charmeleon", "wartortle",
                "mewtwo", "tentacruel", "aerodactyl",
                "omanyte", "slowpoke",
                "pidgeot", "arbok"]

    print("Updates complete!\nNote that skips, aliases, and qualifiers must be added manually and will not be covered by the automatic update.")

    random.shuffle(pokemon_list)

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((475, 540))
    pygame.display.set_caption("Who's That Pokémon?")

    font_big = pygame.font.SysFont("Comic Mono", 24)
    font_small = pygame.font.SysFont("Comic Mono", 18)
    bg_color = pygame.Color(42, 117, 187)

    state: GameState = GameState(full_pokemon_list)
    load_start_time = 0
    backspace_held_for = 0

    next_pkmn_thread = CustomThread()
    next_pkmn_thread.start()

    # Game Loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # typing
                if event.key == pygame.K_RETURN:
                    #commands
                    match state.guess.upper():
                        case "POKERAP":
                            print("switching to pokerap mode")
                            state.reset(pokerap_list, False)
                        case "RESET":
                            print("resetting game")
                            state.reset(full_pokemon_list, True)
                        case "SPECIFIC":
                            print("enabling specific mode")
                            state.specific_mode = True
                            state.guess = ""
                        case "NOSPECIFIC":
                            print("disabling specific mode")
                            state.specific_mode = False
                            state.guess = ""
                        case "ONLYSPECIFIC":
                            print("Switching to only pokemon affected by specific mode.")
                            # state.specific_mode = True
                            state.reset([mon for mon in state.pokemon_list if "qualifiers" in pokemon_data[mon]])
                        case "INVERT":
                            print("Inverting pokemon list")
                            state.reset([mon for mon in full_pokemon_list if mon not in state.pokemon_list])
                        case "QUIT":
                            pygame.quit()
                            sys.exit()
                        case "FASTMODE":
                            next_pkmn_thread.join()
                            state.fast_mode = True
                            next_pkmn_thread = CustomThread(target = get_next_pokemon, args = (state, pokemon_data))
                            next_pkmn_thread.start()
                            print("Fast Mode Enabled.")
                        case "NOFAST":
                            next_pkmn_thread.join()
                            state.fast_mode = False
                            print("Fast Mode Disabled.")

                    if state.guess[:9].upper() == "CONTAINS:":
                        print(f"switching to ids containg {state.guess[9:].lower()}")
                        conditions = state.guess[9:].split("|")
                        contains_list = [mon for mon in state.pokemon_list if any(cond in mon for cond in conditions)]
                        state.specific_mode = False
                        state.reset(contains_list, True)
                    elif state.guess[:6].upper() == "START:" and len(state.guess) == 7:
                        print(f"switching to ids starting with {state.guess[-1].lower()}")
                        starts_list = [mon for mon in state.pokemon_list if mon[0] == state.guess[-1].lower()]
                        state.reset(starts_list, True)
                    state.guess = ''
                elif event.key != pygame.K_BACKSPACE:
                    state.guess += event.unicode

                state.pokemon_guessed = pokemon.guess(state.guess, state.specific_mode)

        keys_down = pygame.key.get_pressed()
        if keys_down[pygame.K_BACKSPACE]:
            if (backspace_held_for == 0 or backspace_held_for >= 15):
                if keys_down[pygame.K_LCTRL] or keys_down[pygame.K_RCTRL]:
                    last_index = 0
                    for index, letter in reversed(list(enumerate(state.guess))):
                        if index == len(state.guess) - 1:
                            continue
                        if not letter.isalnum():
                            last_index = index
                            break
                    state.guess = state.guess[:last_index + (1 if last_index != 0 else 0)]
                elif keys_down[pygame.K_LALT] or keys_down[pygame.K_RALT]:
                    state.guess = ""
                else:
                    state.guess = state.guess[:-1]
            backspace_held_for += 1
        else:
            backspace_held_for = 0

        if not state.pokemon_chosen:
            # select the next pokemon
            if len(state.pokemon_list) <= 0:
                state.reset(full_pokemon_list, True)
            state.index += 1
            if state.index >= len(state.pokemon_list):
                if state.randomize_after:
                    random.shuffle(state.pokemon_list)
                state.index = 0
                print(f"Finished in RTA: {time.time() - state.game_start:.2f} / IGT: {now - state.game_start:.2f} seconds")
                state.game_start = time.time()
                state.adjusted_game_start = 0

            # update variables
            if not state.fast_mode:
                pokemon = Pokemon(state.pokemon_list[state.index], pokemon_data)
            else:
                pokemon = next_pkmn_thread.join()   
                next_pkmn_thread = CustomThread(target = get_next_pokemon, args = (state, pokemon_data))
                next_pkmn_thread.start()       
            if state.index == 0 and state.fast_mode:
                # fixes resets when fast mode is on
                pokemon = Pokemon(state.pokemon_list[state.index], pokemon_data)
            state.pokemon_chosen = True
            state.pokemon_guessed = False
            state.guess = ''
            number_guessed_str = f"{state.index} / {len(state.pokemon_list)}"
            guess_start = time.time()
            if state.adjusted_game_start == 0:
                state.adjusted_game_start = time.time()
            else:
                state.adjusted_game_start += (time.time() - load_start_time)

        guess_surface = font_big.render(state.guess, True, pygame.Color(0, 0, 0))
        now = time.time()
        guess_num_surface = font_small.render(f"{number_guessed_str} {now - guess_start:.2f} RTA: {now - state.game_start:.2f} IGT: {now - state.adjusted_game_start:.2f}", True, pygame.Color(0, 0, 0))
        
        screen.fill(bg_color)
        if not state.pokemon_guessed:
            screen.blit(pokemon.shadow_img, (0, 0))
        else:
            state.pokemon_chosen = False
            if not state.fast_mode:
                screen.blit(pokemon.img, (0, 0))
            else:
                screen.blit(pokemon.shadow_img, (0, 0))
            load_start_time = time.time()
        screen.blit(guess_surface, (5, 480))
        screen.blit(guess_num_surface, (5, 510))
        pygame.display.update()
        clock.tick(30)

if __name__ == "__main__":
    main()