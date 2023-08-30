import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import re
import time
import scattertext as st
import spacy
nlp = spacy.load('en_core_web_sm-3.2.0')  # Load the spaCy model
nlp.max_length = 9000000
from nltk.corpus import stopwords
import nltk
nltk.download('punkt')
nltk.download('stopwords')
### stopwords_files
# Update with the Welsh stopwords (source: https://github.com/techiaith/ataleiriau)
en_stopwords = list(stopwords.words('english'))
cy_stopwords = open('./website/data/welsh_stopwords.txt', 'r', encoding='iso-8859-1').read().split('\n') # replaced 'utf8' with 'iso-8859-1'
STOPWORDS = set(en_stopwords + cy_stopwords)
PUNCS = '''!→()-[]{};:'"\,<>./?@#$%^&*_~'''

class SentimentAnalyser:
    def __init__(self):
        # Loading tokenizer and model during initialization to avoid doing it multiple times.
        self.tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
        self.model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")

    def preprocess_text(self,text):
        # remove URLs, mentions, and hashtags
        text = re.sub(r"http\S+|@\S+|#\S+", "", text)
        # remove punctuation and convert to lowercase
        text = re.sub(f"[{re.escape(''.join(PUNCS))}]", "", text.lower())
        # remove stopwords
        text = " ".join(word for word in text.split() if word not in STOPWORDS)
        return text

    def analyse_sentiment(self, input_text, num_classes, max_seq_len=512):
        # Split the input text into separate reviews
        reviews = input_text
        #print(reviews)
        # Initialize sentiment counters
        sentiment_counts = {'Negative': 0, 'Neutral': 0, 'Positive': 0}

        # Predict sentiment for each review
        sentiments = []
        for review in reviews:
            #print(review)
            original_review = review
            review = self.preprocess_text(review)
            
            if review:
                # Tokenize the review
                tokens = self.tokenizer.encode(review, add_special_tokens=True, truncation=True)

                # If the token length exceeds the maximum, split into smaller chunks
                token_chunks = []
                if len(tokens) > max_seq_len:
                    token_chunks = [tokens[i:i + max_seq_len] for i in range(0, len(tokens), max_seq_len)]
                else:
                    token_chunks.append(tokens)

                # Process each chunk
                sentiment_scores = []
                for token_chunk in token_chunks:
                    input_ids = torch.tensor([token_chunk])
                    attention_mask = torch.tensor([[1] * len(token_chunk)])

                    # Run the model
                    outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    scores = outputs.logits.softmax(dim=1).detach().numpy()[0]
                    sentiment_scores.append(scores)

                # Aggregate the scores
                avg_scores = np.mean(sentiment_scores, axis=0)
                sentiment_labels = ['Very negative', 'Negative', 'Neutral', 'Positive', 'Very positive']
                sentiment_index = avg_scores.argmax()

                if num_classes == 3:
                    sentiment_labels_3 = ['Negative', 'Neutral', 'Positive']
                    if sentiment_index < 2:
                        sentiment_index = 0  # Negative
                    elif sentiment_index > 2:
                        sentiment_index = 2  # Positive
                    else:
                        sentiment_index = 1  # Neutral
                    sentiment_label = sentiment_labels_3[sentiment_index]
                else:
                    sentiment_label = sentiment_labels[sentiment_index]

                sentiment_score = avg_scores[sentiment_index]
                sentiment_score = float(format(avg_scores[sentiment_index], ".2f"))

                sentiments.append((original_review, sentiment_label, sentiment_score))

                # Map 'Very negative' and 'Very positive' to 'Negative' and 'Positive'
                if sentiment_label in ['Very negative', 'Negative']:
                    sentiment_counts['Negative'] += 1
                elif sentiment_label in ['Very positive', 'Positive']:
                    sentiment_counts['Positive'] += 1
                else:
                    sentiment_counts['Neutral'] += 1
        #print(sentiments,sentiment_counts)
        return sentiments, sentiment_counts
    

    def generate_scattertext_visualization(self, dfanalysis):
        # Get the DataFrame with sentiment analysis results
        df = dfanalysis
        
        # Parse the text using spaCy
        df['ParsedReview'] = df['Review'].apply(nlp)
        #print(df['ParsedReview'])
        # Create a Scattertext Corpus

        corpus = st.CorpusFromParsedDocuments(
            df,
             category_col="Sentiment Label",
            parsed_col="ParsedReview"
            ).build()
        
        term_scorer = st.RankDifference()
        html = st.produce_scattertext_explorer(
            corpus,
            category="Positive",
            category_name="Positive",   
            not_category_name='Negative_and_Neutral',
            not_categories=df["Sentiment Label"].unique().tolist(),
            minimum_term_frequency=5,
            pmi_threshold_coefficient=5,
            width_in_pixels=1000,
            metadata=df["Sentiment Label"],
            term_scorer=term_scorer
        ) 
        



        filename = f"./website/static/scattertext_visualization.html"
        with open(filename, "w") as f:
            f.write(html)
            f.close()
        
        #wrap_html_content(filename)
        return "/static/scattertext_visualization.html"
    
def wrap_html_content(file_name):
       # Step 1: Read the File
        with open(file_name, 'r', encoding='utf-8') as file:
            content = file.read()

        # Step 2: Wrap Content
        wrapped_content = f"""
        <!DOCTYPE html>
            <html lang="en">
            <head>
             <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Wrapped Content</title>
            </head>
            <body>
            {content}
        </body>
        </html>
         """

        # Step 3: Save to New File
        output_file_name = file_name
        with open(output_file_name, 'w', encoding='utf-8') as file:
            file.write(wrapped_content)

        #print(f"Content wrapped and saved to {output_file_name}")
        return output_file_name
        
