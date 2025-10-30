import pytest
import backend.scraper as scraper

def test_get_pokemon():
    pokemon = scraper.get_pokemon("bulbasaur")

    assert pokemon['id'] == 1
    assert pokemon['is_legendary'] == False
    assert pokemon['color']['name'] == 'green'


def test_get_pokemon_number():
    pokemon = scraper.get_pokemon_number("bulbasaur")

    assert pokemon == 1

