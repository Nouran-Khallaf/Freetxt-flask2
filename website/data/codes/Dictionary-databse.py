import pandas as pd
import sqlite3

# read the csv file
df = pd.read_csv('/Users/katiana/Documents/Thesawrws-website/website/data/Welsh_wordlist.csv')

# melt the dataframe
df_melted = df.melt(id_vars=['word', 'sense'], 
                    value_vars=[f'WelshSynset_{i+1}' for i in range(47)], 
                    value_name='synset')

# remove empty synset rows
df_melted = df_melted.dropna(subset=['synset'])

# Group by 'word' and 'sense', joining all 'synset' values together into a list
df_grouped = df_melted.groupby(['word', 'sense'])['synset'].apply(list).reset_index()
df_grouped['synset'] = df_grouped['synset'].apply(lambda x: ','.join(map(str, x)))
print(df_grouped)
df_pairs = df_grouped.explode('synset')
print (df_pairs)



# Create a new connection to the SQLite database
conn = sqlite3.connect('Dict-synonyms.db')

# Create a new cursor
c = conn.cursor()

# Drop the old 'synonyms' table
c.execute('DROP TABLE IF EXISTS synonyms')

# Create the new 'synonyms' table
c.execute('''
    CREATE TABLE IF NOT EXISTS synonyms (
        word TEXT,
        sense TEXT,
        synset TEXT
    )
''')

# Write the data frame to the new table
df_pairs.to_sql('synonyms', conn, if_exists='append', index=False)

# Commit the changes and close the connection
conn.commit()
conn.close()
