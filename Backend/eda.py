import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def primary_type_distr(df):
    type_colors = {'Normal': '#A8A77A',
                    'Fire': '#EE8130',
                    'Water': '#6390F0',
                    'Grass': '#7AC74C',
                    'Electric': '#F7D02C',
                    'Ice': '#96D9D6',
                    'Fighting': '#C22E28',
                    'Poison': '#A33EA1',
                    'Ground': '#E2BF65',
                    'Flying': '#A98FF3',
                    'Psychic': '#F95587',
                    'Bug': '#A6B91A',
                    'Rock': '#B6A136',
                    'Ghost': '#735797',
                    'Dragon': '#6F35FC',
                    'Dark': '#705746',
                    'Steel': '#B7B7CE',
                    'Fairy': '#D685AD'}
    
    counts = df['primary type'].value_counts()
    list_of_types = counts.index.tolist()
    custom_colors = [type_colors[t] for t in list_of_types]
    
    plt.pie(counts, labels=counts.index.tolist(), colors=custom_colors, autopct='%1.1f%%')
    plt.ylabel("")
    plt.title("primary type distribution")
    plt.legend(labels=counts.index.tolist(), loc = [1.2, 0.1])
    plt.show()


def main():
    df = pd.read_csv("pokemon_data.csv")
    print(df.head())
    df.info()
    df.describe()
    df['bst'] = df[['hp','atk','def','spa','spd','spe']].sum(axis=1)

    primary_type_distr(df)
    
    


if __name__=="__main__":
    main()