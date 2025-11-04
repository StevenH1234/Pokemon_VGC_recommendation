import pytest
import backend.scraper as scraper

SMOGON_URL = "https://www.smogon.com/dex/sv/pokemon/"
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon-species"

def test_get_pokemon():
    pokemon = scraper.get_pokemon("bulbasaur")

    assert pokemon['id'] == 1
    assert pokemon['is_legendary'] == False
    assert pokemon['color']['name'] == 'green'


def test_get_pokemon_number():
    pokemon = scraper.get_pokemon_number("bulbasaur")

    assert pokemon == 1

def test_pokemon_scraper_normalization():
    ability_list = []
    pokemon_scraper = scraper.PokemonScraper(SMOGON_URL, POKEAPI_URL)
    correctly_normed_attrs = [3, "venusaur", "Grass", "Poison", "overgrow", "None", "chlorphyll", "ZU", 80, 82, 83, 100, 100, 80]

    attributes = ["venusaur", "Grass", "Poison", "overgrow", "At 1/3 or half of its max hp.", "chlorphyll", "in harsh sunlight.", "ZU", "HP", 80, "Atk", 82, "Def", 83, "SpA", 100, "SpD", 100, "Spe", 80]
    normed_attributes = pokemon_scraper.normalize_attributes(attributes, ability_list)
    print(normed_attributes)

    assert normed_attributes == correctly_normed_attrs

def test_pokemon_scraper_normalization_length():
    ability_list = []
    pokemon_scraper = scraper.PokemonScraper(SMOGON_URL, POKEAPI_URL)

    attributes = ["venusaur", "Grass", "Poison", "overgrow", "At 1/3 or half of its max hp.", "chlorphyll", "in harsh sunlight.", "ZU", "HP", 80, "Atk", 82, "Def", 83, "SpA", 100, "SpD", 100, "Spe", 80]
    normed_attributes = pokemon_scraper.normalize_attributes(attributes, ability_list)
    assert len(normed_attributes) == 14
