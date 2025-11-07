import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pokebase as pb
import os
import json

# TODO: code works well for scraping the SV era of pokemon competitive play, but not others. Adapt the code to account for each generation of pokemon (champions and gen 10)
# TODO: May need to address the pokemon with forms and how to id them in the data frame.
# TODO: Be more specific about the exceptions being reaised (Structured logging instead of prints). 
# TODO: too many API calls, we need a caching system. 

# TODO: Probably only want to init the driver when parsing the data. If the cache exists we dont need the webdriver
# TODO: Either get the IDs and save them so we can access pokeapi's sprites or just go with the models from the smogon.(will take more time but will look best with the API sprites)

SMOGON_URL = "https://www.smogon.com/dex/sv/pokemon/"
POKEAPI_URL = "https://pokeapi.co/api/v2/pokemon-species/"
CACHE_DIR = "pokemon_cache"
SMOGON_CACHE_DIR = "smogon_cache"
TYPES = ['Fire', 'Water', 'Grass', 'Electric', 'Ground', 'Rock', 'Normal', 'Bug', 'Flying', 'Ice', 'Ghost', 'Dark', 'Fighting', 'Psychic', 'Fairy', 'Steel', 'Dragon', 'Poison', 'None']
FORMATS = ['Uber', 'OU', 'UU', 'RU', 'NU', 'PU', 'ZU', 'AG', 'NFE', 'LC', 'UUBL', 'RUBL', 'NUBL', 'PUBL', 'ZUBL']

class PokemonScraper():
    """
    A class designed to scrape data from sources like Smogon, a community website for competitive pokemon, and POKEAPI

    public methods: 
        get_smogon_page(): returns a list containing all html on the smogon pokedex page
        parse_pokemon_data(): parses html to extract and return all the data from each pokemon
        normalize_attributes(attr_list, ability_list): normalize the extracted data from the list of pokemon data
    """

    def __init__(self, smogon_url, pokeapi_url):
        """
        Initializes the object with both source URLs

        Args:
            smogon_url (str): the url link to the smogon pokedex 
            pokeapi_url (str): the base url link to pokeapi 
        """
        self.smogon_url = smogon_url
        self.pokeapi_url = pokeapi_url
        self.driver = None
    
    def init_driver(self):
        self.driver = webdriver.Chrome()
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def get_smogon_page(self):
        """
        use selenium to scroll through the pokedex page and return a list of the html scraped after each scroll

        Returns:
            pokemon_data_list (list) - list containing all the html that is scrolled through
        """

        # if the smogon cache contains the list, load data from the cache
        smogon_cache_path = os.path.join(SMOGON_CACHE_DIR, "data_list.json")
        if os.path.exists(smogon_cache_path):
            print("path exists... driver is not scrolling")
            with open(smogon_cache_path, 'r') as f:
                return json.load(f)
        
        # init variables
        pokemon_data_list = set()       
        self.init_driver()
        self.driver.get(self.smogon_url)
        window_height = self.driver.execute_script("return window.innerHeight")
        scroll_height = self.driver.execute_script("return document.body.scrollHeight")
        current_height = 0

        try:
            
            # scroll until the webpage reaches part of the table that has a "DexNonstd" class name
            while current_height < scroll_height:
                current_height += window_height

                scroll_div = self.driver.find_element(By.CLASS_NAME, "DexTable")

                html = scroll_div.get_attribute("innerHTML")

                if len(scroll_div.find_elements(By.CLASS_NAME, "DexNonstd")) > 0:
                    break

                # collect the html from this pass and add it to the data list
                pokemon_data_list.add(html)

                self.driver.execute_script(f"window.scrollTo(0, {current_height});")

                time.sleep(1)

            # dump the data into the cache
            pokemon_data_list = list(pokemon_data_list)
            smogon_cache_path = os.path.join(SMOGON_CACHE_DIR, "data_list.json")
            with open(smogon_cache_path, "w") as f:
                json.dump(pokemon_data_list, f, indent=4)

            self.close_driver()
            return pokemon_data_list
        
        except requests.exceptions.RequestException as e:
            print(f"error fetching {self.smogon_url}: {e}") 

    def parse_pokemon_data(self):
        """
            go through the list of smogon html to strip away the html and extract the metadata

            Returns:
                attributes: list of smogon html data fully parsed and cleaned
        """

        # retreive html and init variables
        smogon_html = self.get_smogon_page()
        ability_list = []
        attributes = []

        # iterate through the list of smogon html and extract metadata from each section of the table
        for html in smogon_html:
            bs = BeautifulSoup(html, "html.parser")
            for i in bs:
                pkm_attr = [t for t in i.stripped_strings]
                attributes.append(self.normalize_attributes(pkm_attr, ability_list)) # clean and add the metadata to the attributes list
        return attributes
    
    def normalize_attributes(self, attr_list, ability_list):

        """
            given a list of attributes, prune unnecessary data and return a copy of the list containing only the relevent data points

            Args:
                attr_list (list): list containing uncleaned metadata extracted from the smogon html
                ability_list (list): empty list of abilities to seperate the abilities and descriptions from the pokemon data. 

            Returns: 
                list: a copy of the original attribute list (attr_list) that contains only the relevent data points
        """

        new_attr_list = []
        pokemon_number = get_pokemon_dex_number(attr_list[0])

        # if a pokemon has an associated dex number then process the data, otherwise remove the attributes all together 
        if pokemon_number:
            new_attr_list.insert(0, pokemon_number)

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

            # account for single types
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
        else:
            print(f"removed {attr_list}")
        
        new_attr_list
        return new_attr_list

def cache_pokemon_json(pokemon, json_data):
    """
    creates a dedicated path for the pokemon json file and stores it in the local cache

    Args:
        pokemon (str): name of the pokemon as a string
        json_data (dict): python json_data dictionary object containing data from PokeAPI
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

    cache_path = os.path.join(CACHE_DIR, f"{pokemon}.json")

    with open(cache_path, "w") as f:
        json.dump(json_data, f, indent=4)
    # print("cached complete...")


def get_pokemon(pokemon):

    """
    Returns a single pokemon's data in the form of a json file

    Args:
        pokemon (str): name of the pokemon as a string

    Returns:
        json: json file containing information about the pokemon species

    Exceptions:

    """

    try:
        # some pokemon have two word names (i.e. walking wake, raging bolt, flutter mane, etc.) add a dash to help find these pokemon in the api
        if " " in pokemon:
            pokemon = pokemon.replace(' ', '-')

        # check if it is cached
        cache_path = os.path.join(CACHE_DIR, f"{pokemon}.json")
        if os.path.exists(cache_path):
             with open(cache_path, 'r') as f:
                 return json.load(f)
        else:
            response = requests.get(POKEAPI_URL + "/" + pokemon)
            data = response.json()
            cache_pokemon_json(pokemon, data)
            return data
    
    except requests.exceptions.RequestException as e:
        # if the pokemon name fails it is most likely a different form of the pokemon with a hyphenated name
        # print(f"the pokemon {pokemon} may have another form. Checking...")
        try:
            pokemon = pokemon.split("-")[0]

            # check if it is cached
            cache_path = os.path.join(CACHE_DIR, f"{pokemon}.json")
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    return json.load(f)
            else:
                response = requests.get(POKEAPI_URL + "/" + pokemon)
                data = response.json()
                cache_pokemon_json(pokemon, data)
                return data
        
        except requests.exceptions.RequestException as e:
            print(f"error fetching: {e}")
    
def get_pokemon_dex_number(pokemon):
    """
    returns the pokedex number of any given pokemon

    Args: 
        pokemon (str): name of the pokemon as a string

    returns:
        id (int): pokedex number of the pokemon
    """

    pokemon_json = get_pokemon(pokemon)
    if pokemon_json:
        return pokemon_json['id']
    return None

def main():
    ability_list = []
    scraper = PokemonScraper(SMOGON_URL, POKEAPI_URL)
    attributes = scraper.parse_pokemon_data()

    for names in attributes:
        print(names)
    print(len(attributes))


if __name__=="__main__":
    main()