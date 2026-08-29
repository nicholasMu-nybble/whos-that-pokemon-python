## Who's That Pokemon?
Uses PokeAPI to keep regular updates

Automatic PokeAPI updates will not include aliases, qualifiers, or skipped pokemon. Aliases are alternate ways to write a pokemon's name, such as specifying a form or writing nidoran instead of nidoran-f. Qualifiers are used in specific mode to require form names to be specified. Skips are used to skip pokemon that are identical for the purposes of this game, yet are included in PokeAPI, such as Alolan Raticate and Totem Alolan Raticate.

Commands (Type the command then hit return/enter):
- POKERAP
    - Enter Pokerap mode, replaces random pokemon with the kanto pokerap
- RESET
    - Resets the game to its original state
- SPECIFIC
    - Require specific qualifiers when guessing pokemon
    - for example: "Mega Venusaur" instead of just "Venusaur" for venusaur-mega
    - qualifiers must be set in pokemon_data.json, and thus will not update automatically
- NOSPECIFIC
    - Disables specific mode
- ONLYSPECIFIC
    - Limit the pool of pokemon to only those affected by specific mode
- INVERT
    - Switch the pokemon pool to all pokemon not in the current pool
- QUIT
    - Closes the game
- CONTAINS:&lt;filter&gt;
    - Restricts the pool to only ids containing filter
- START:&lt;letter&gt;
    - Restricts the pool to only ids starting with letter