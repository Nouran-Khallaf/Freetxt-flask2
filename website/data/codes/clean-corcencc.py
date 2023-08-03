import re
Corcencc_data = "/Users/katiana/Documents/Thesawrws-website/website/data/corcencc_clean_sentences.txt"

# Read the file and split it into lines
with open(Corcencc_data, 'r') as f:
    lines = f.read().splitlines()

# Remove duplicates and convert to lowercase
lines = {line.lower() for line in lines}

# Remove sentences less than five words long
lines = [line for line in lines if len(line.split()) >= 5]
# Remove sentences that are less than five words long or more than 20 words long
lines = [line for line in lines if 10 <= len(line.split()) <= 50]
# Remove all occurrences of "s6_anon" with varying numbers
lines = [re.sub(r's\d+_anon', '', line) for line in lines]
# Remove "_anon" from each sentence
lines = [line.replace("_anon", "") for line in lines]
# Overwrite the file with the new sentences
with open(Corcencc_data, 'w') as f:
    for line in lines:
        f.write(line + '\n')
