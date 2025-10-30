import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import pokebase as pb

# TODO - account for the dynamic table data with selenium
# TODO - some pokemon in smogon dont normally exist or are forms of another pokemon, must account for that with PokeAPI

'''
FeedBack for first code review - 
1. feels more like a moc-up rather than production code
2. Implement object oriented programming by makking this a class called "PokemonScraper" (DONE)
3. Improve the error handling capabilities. Things like selenium can fail and should be caught (retries on bad API requests)
4. Return a copy of attrs instead of modifying the list of attr in place (Safer)
5. There is no Testing at all (include unit tests or mock API-layer)
6. Documentation needs to be clearer using PEP 257 standards
7. Naming must be consistent (e.g. func --> snake_case, var --> snake_case, Classes --> PascalCase)
8. dependencies should be labled
'''

SMOGON_URL = "https://www.smogon.com/dex/sv/pokemon/"
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon-species"
TYPES = ['Fire', 'Water', 'Grass', 'Electric', 'Ground', 'Rock', 'Normal', 'Bug', 'Flying', 'Ice', 'Ghost', 'Dark', 'Fighting', 'Psychic', 'Fairy', 'Steel', 'Dragon', 'Poison', 'None']
FORMATS = ['Uber', 'OU', 'UU', 'RU', 'NU', 'PU', 'ZU', 'AG', 'NFE', 'LC', 'UUBL', 'RUBL', 'NUBL', 'PUBL', 'ZUBL']

class PokemonScraper():
    def __init__(self, smogon_url, pokeapi_url):
        self.smogon_url = smogon_url
        self.pokeapi_url = pokeapi_url
        self.driver = None
    
    def init_driver(self):
        self.driver = webdriver.Chrome()
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def get_smogon_page(self):
        try:
            self.driver.get(self.smogon_url)
            html = self.driver.page_source
            res = BeautifulSoup(html, "html.parser")
            return res
        except requests.exceptions.RequestException as e:
            print(f"error fetching {self.smogon_url}: {e}") 

    def parse_pokemon_data(self):
        smogon_html = self.get_smogon_page()
        ability_list = []
        attributes = []

        # loaded dynamically using javascript; therefore, we must use selenium to handle dynamic loading. 
        dex_table = smogon_html.select_one('div.DexTable.is-even')
        dex_rows = dex_table.find_all('div', class_="PokemonAltRow")
        
        for i in dex_rows:
            pkm_attr = [t for t in i.stripped_strings]
            attributes.append(self.normalize_attributes(pkm_attr, ability_list))
        return attributes
    
    def normalize_attributes(self, attr_list, ability_list):
        new_attr_list = []
        new_attr_list.insert(0, get_pokemon_number(attr_list[0]))

        # remove descriptions of abilities
        for idx, item in enumerate(attr_list):
            if isinstance(item,str) and " " in item and "." in item:
                ability_list.append((attr_list[idx-1], item))
            else:
                new_attr_list.append(item)

        # remove the stat titles
        new_attr_list.remove("HP")
        new_attr_list.remove("Atk")
        new_attr_list.remove("Def")
        new_attr_list.remove("SpA")
        new_attr_list.remove("SpD")
        new_attr_list.remove("Spe")

        # Normalize types
        if new_attr_list[3] not in TYPES: 
            new_attr_list.insert(3, "None")

        # Normalize abilities (Accounting for hidden ability and second ability)
        abilities = 0
        format_idx = 0
        for i in range(4, len(new_attr_list)):
            if new_attr_list[i] in FORMATS:
                format_idx = i
                break
            abilities += 1
        
        if abilities == 2:
            new_attr_list.insert(format_idx-1, "None")
        if abilities == 1:
            new_attr_list.insert(format_idx, "None")
            new_attr_list.insert(format_idx+1, "None")
        
        return new_attr_list

def get_pokemon(pokemon):
    # function rettrieves json dataa of a certain pokemon from the API endpoint
    try:
        response = requests.get(POKEAPI_URL + "/" + pokemon)
        return response.json()
    
    except requests.exceptions.RequestException as e:
        # if the pokemon name fails it is most likely a different form of the pokemon with a hyphenated name
        print("the pokemon may have another form. Checking...")
        try:
            pokemon = pokemon.split("-")[0]
            response = requests.get(POKEAPI_URL + "/" + pokemon)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"error fetching  {POKEAPI_URL}: {e}")
            return None
    
def get_pokemon_number(pokemon):
    return get_pokemon(pokemon)['id']

def main():
    ability_list = []

    scraper = PokemonScraper(SMOGON_URL, POKEAPI_URL)
    scraper.init_driver()
    scraper.get_smogon_page()
    attributes = scraper.parse_pokemon_data()
    scraper.close_driver()

    print(attributes)

    print(get_pokemon("bulbasaur"))

if __name__=="__main__":
    main()