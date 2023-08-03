########convert to dataset
import pandas as pd

# Load the CSV file into a pandas DataFrame
df = pd.read_csv("./website/data/Data_all.csv", index_col=False)

# Group by 'word' and 'sense', joining all 'synset' values together into a list
df_grouped = df.groupby(['word', 'sense'])['synset'].apply(list).reset_index()
df_grouped['synset'] = df_grouped['synset'].apply(lambda x: ','.join(map(str, x)))

# Create a new DataFrame where each row is a word-synonym pair
df_pairs = df_grouped.explode('synset')


#############create the database of the goldstandard
import sqlite3

# Create a new connection to the SQLite database
conn = sqlite3.connect('GS-synonyms.db')

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
print(df_pairs)
# Commit the changes and close the connection
conn.commit()
conn.close()

