# Pokemon VGC team recommendation project

This is a passion project centered around the Pokemon video game championship. I've always loved Pokemon and wanted to get into the competitve side of the game. It has always been out of reach but with some coding, I will have a better understanding of competitve play.

I don't want to get abandon this project like I have many times in the past. I will implement checkpoints for myself to keep myself motivated.

1. Set up the backend environment

   - install relevant packages (pandas, numpy, requests, beautiful soup)

2. Scrape pokemon data from smogon, serebii, pokeAPI, and others

   a. Scrape for Pokemon type, stats, and sprites first

   b. Scrape for Pokemon moves and abilities - move data should include type, power, classification, description, and effects. Ability should include name and description

3. use the scraped data to make a visualization with javascript and html

   - frontend only to visualize a pokemon almost like a dashboard.
   - toggle between moves and stat spread

4. create a pokemon

   - Allow user-defined pokemon builds for analysis. Choose a pokemon, its ability, and its moves and store this pokemon into a data set to be analyzed

5. Exploratory data analysis

   - identify what qualifies a pokemon as "competitively viable"
   - scrape data from smogon
   - utilize meta data from smogon to compare against pokemon entered into created dataset

6. scoring systems

   - use smogon data to guide scoring system. For an entire team.

7. recommendation algorithm
   - use the score to simulate teams and rank their competitive viability.

THINGS LEARNED:

- Scrollable divs act like tables but can operate dynamically on webpages

ISSUES FOUND:

- all paradox forms exist in pokeAPI but the way they are deonted in smogon it cannot be accessed
- NOT every pokemon is in scarlet and violet. we would have to account for different games and formats
- Think about the regulations (reg I, reg H, reg G, etc.)
