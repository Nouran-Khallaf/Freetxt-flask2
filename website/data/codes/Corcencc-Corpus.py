import os
import nltk

# Define path to the corpus folder
corpus_folder = "CorCenCC_corpus"

# Create an empty list to store the corpus sentences
corpus_sentences = []

# Loop through each file in the corpus folder
for filename in os.listdir(corpus_folder):

    # Construct the full file path
    file_path = os.path.join(corpus_folder, filename)

    # Check if the file is a text file
    if filename.endswith(".txt"):

        # Open the file and read its contents
        with open(file_path, 'r') as f:
            file_text = f.read()

        # Tokenize the file into sentences and add to the corpus sentences list
        file_sentences = nltk.sent_tokenize(file_text)
        corpus_sentences.extend(file_sentences)

# Convert the corpus sentences list to a set to remove duplicates
corpus_sentences = set(corpus_sentences)

# Print the number of sentences in the corpus
print("Number of sentences in corpus: ", len(corpus_sentences))

# Print the first 10 sentences in the corpus
print("First 10 sentences in corpus: ", list(corpus_sentences)[:10])
