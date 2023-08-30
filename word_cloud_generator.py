import os
import numpy as np
import pandas as pd
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
from PIL import Image as PilImage
import matplotlib.pyplot as plt
import nltk
import time
from collections import Counter
import requests
import io
from langdetect import detect
import spacy
import math
import imageio
nlp = spacy.load('en_core_web_sm-3.2.0')  # Load the spaCy model
nlp.max_length = 9000000
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')
### stopwords_files
# Update with the Welsh stopwords (source: https://github.com/techiaith/ataleiriau)
en_stopwords = list(stopwords.words('english'))
cy_stopwords = open('./website/data/welsh_stopwords.txt', 'r', encoding='iso-8859-1').read().split('\n') # replaced 'utf8' with 'iso-8859-1'
STOPWORDS = set(en_stopwords + cy_stopwords)
def cleanup_old_graphs(directory, age_in_seconds=20): 
    current_time = time.time()

    for filename in os.listdir(directory):
        if filename.startswith("wordcloud_") and filename.endswith(".png"):
            file_timestamp = int(filename.split("_")[1].split(".")[0])
            file_age = current_time - file_timestamp

            if file_age > age_in_seconds:
                os.remove(os.path.join(directory, filename))
class WordCloudGenerator:

    def __init__(self):
        self.STOPWORDS = set(STOPWORDS)
        self.PUNCS = [".", ",", "!", ":", ";", "-", "_", "?", "&", "*", "(", ")", "$", "@", "#", "%", "^", "+", "=", "<", ">", "/", "|", "]", "[", "{", "}", "\\", "'", "\""]
        self.pymusaslist = pd.read_csv('./website/data/Pymusas-list.txt', names= ['USAS Tags', 'Equivalent Tag'])
        
    def load_image(self, image_file):
        return PilImage.open(image_file)

    def preprocess_data(self, data):
        # Tokenize and clean data
        tokenizer = nltk.RegexpTokenizer(r"\w+")
        tokens = tokenizer.tokenize(data)
        tokens = [word for word in tokens if word.lower() not in self.STOPWORDS and word.lower() not in self.PUNCS]
        tokens = [word for word in tokens if len(word) > 1]  # remove single-letter words
        
        # Further text processing based on language can be added here 
        return tokens
    
    def Pymsas_tags(self, text):
        words=''
        for _, row in text.iterrows():
            words += ' '.join(row) + '\n'
        with open('cy_tagged.txt', 'w') as f:
            f.write(words)

        lang_detected = detect(words)

        if lang_detected == 'cy':
            files = {
   	    'type': (None, 'rest'),
    	'style': (None, 'tab'),
    	'lang': (None, 'cy'),
    	'text': text,
		}

            response = requests.post('http://ucrel-api-01.lancaster.ac.uk/cgi-bin/pymusas.pl', files=files)

            # Read the response into a DataFrame
            cy_tagged = pd.read_csv(io.StringIO(response.text), sep='\t')
            cy_tagged['USAS Tags'] = cy_tagged['USAS Tags'].str.split('[,/mf]').str[0].str.replace('[\[\]"\']', '', regex=True)
            
            cy_tagged['USAS Tags'] = cy_tagged['USAS Tags'].str.split('+').str[0]
            
            merged_df = pd.merge(cy_tagged, self.pymusaslist, on='USAS Tags', how='left')
        
            merged_df.loc[merged_df['Equivalent Tag'].notnull(), 'USAS Tags'] = merged_df['Equivalent Tag'] 
            merged_df = merged_df.drop(['Equivalent Tag'], axis=1)
            tags_to_remove = ['Unmatched', 'Grammatical bin', 'Pronouns', 'Period']
            merged_df = merged_df[~merged_df['USAS Tags'].str.contains('|'.join(tags_to_remove))]
            return merged_df['USAS Tags']

        elif lang_detected == 'en':
            nlp = spacy.load('en_core_web_sm-3.2.0')	
            english_tagger_pipeline = spacy.load('en_dual_none_contextual')
            nlp.add_pipe('pymusas_rule_based_tagger', source=english_tagger_pipeline)
            output_doc = nlp(words)
            cols = ['Text', 'Lemma', 'POS', 'USAS Tags']
            tagged_tokens = []
            for token in output_doc:
                tagged_tokens.append((token.text, token.lemma_, token.tag_, token._.pymusas_tags[0]))
            tagged_tokens_df = pd.DataFrame(tagged_tokens, columns = cols)
            tagged_tokens_df['USAS Tags'] = tagged_tokens_df['USAS Tags'].str.split('[/mf]').str[0].str.replace('[\[\]"\']|-{2,}|\+{2,}', '', regex=True)
            merged_df = pd.merge(tagged_tokens_df, self.pymusaslist, on='USAS Tags', how='left')
            merged_df.loc[merged_df['Equivalent Tag'].notnull(), 'USAS Tags'] = merged_df['Equivalent Tag'] 
            merged_df = merged_df.drop(['Equivalent Tag'], axis=1)
            tags_to_remove = ['Unmatched', 'Grammatical bin', 'Pronouns', 'Period']
            merged_df = merged_df[~merged_df['USAS Tags'].str.contains('|'.join(tags_to_remove))]
            return merged_df['USAS Tags']

        return None  # Return None if the language is neither 'cy' nor 'en'
    def calculate_measures(self,df,measure,language):

        # Convert the frequency column to an integer data type
        df['freq'] = df['freq'].astype(int)
        # Calculate the total number of words in the text
        total_words = df['freq'].sum()
        # Calculate the total number of words in the reference corpus
        if language == 'en':
            ref_words = 968267
        elif language == 'cy':
            ref_words = 13487210
        # Calculate the KENESS and log-likelihood measures for each word
        values = []
        for index, row in df.iterrows():
            observed_freq = row['freq']
            expected_freq = row['f_Reference'] * total_words / ref_words
            if measure == 'KENESS':
                value = math.log(observed_freq / expected_freq) / math.log(2)
            elif measure == 'Log-Likelihood':
                value = 2 * (observed_freq * math.log(observed_freq / expected_freq) +
                          (total_words - observed_freq) * math.log((total_words - observed_freq) / (total_words - expected_freq)))
            values.append(value)

    # Add the measure values to the dataframe
        df[measure] = values
        return df

    def filter_words(self, word_list):
        """Return a list with stopwords and punctuation removed."""
        return [word for word in word_list if word not in self.STOPWORDS and word not in self.PUNCS]



    def get_wordcloud(self, word_list, cloud_shape_path, cloud_outline_color):
        # Filter out stopwords and punctuation
        filtered_words = self.filter_words(word_list)
    
        image_mask = imageio.imread(cloud_shape_path)

        # Create a frequency distribution
        frequency_dist = Counter(filtered_words)

        wordcloud = WordCloud(
        width=2000,
        height=2000,
        stopwords=self.STOPWORDS,
        mask=image_mask,
        background_color='rgba(255, 255, 255, 0)',  # transparent background
        mode='RGBA'  # Ensure the mode is set to RGBA
        ).generate_from_frequencies(frequency_dist)
        cleanup_old_graphs("website/static/wordcloud")
        # Generate a unique image name using the current timestamp
        timestamp = int(time.time())
        wc_image_path = os.path.join("website/static/wordcloud", f"wordcloud_{timestamp}.png")
    
        wordcloud.to_file(wc_image_path)

        return f'static/wordcloud/wordcloud_{timestamp}.png', filtered_words


  
    def compute_word_frequency(self, input_data, language):
        if language == 'en':
            Bnc_corpus = pd.read_csv('./website/static/keness/Bnc.csv')
            words = nltk.tokenize.word_tokenize(input_data)
            fdist1 = nltk.FreqDist(words)
            filtered_word_freq = dict((word, freq) for word, freq in fdist1.items() if not word.isdigit())

            word_freq = pd.DataFrame({
                'word': list(filtered_word_freq.keys()),
                'freq': list(filtered_word_freq.values())
            })
            
            # Merge with BNC corpus
            word_freq = word_freq.merge(Bnc_corpus[Bnc_corpus['word'].isin(word_freq['word'])], how='inner', on='word')

            df = word_freq[['word', 'freq', 'f_Reference']]

        elif language == 'cy':
            column_names = ['word', 'f_Reference']
            corcencc_corpus = pd.read_csv('./website/static/keness/file.raw.pos.sem.wrd.fql', sep='\t', names=column_names)
           

            words = nltk.tokenize.word_tokenize(input_data)
            fdist1 = nltk.FreqDist(words)
            filtered_word_freq = dict((word, freq) for word, freq in fdist1.items() if not word.isdigit())

            word_freq = pd.DataFrame({
                'word': list(filtered_word_freq.keys()),
                'freq': list(filtered_word_freq.values())
            })
            
            # Merge with CorCenCC corpus
            word_freq = word_freq.merge(corcencc_corpus[corcencc_corpus['word'].isin(word_freq['word'])], how='inner', on='word')

            df = word_freq[['word', 'freq', 'f_Reference']]
        
        return df
    
    def generate_wordcloud_type(self, input_data,cloud_type, language):
        json_data = input_data.to_json(orient="records")
        df = self.compute_word_frequency( json_data, language)
       
        all_words = []
        
        if cloud_type == 'all_words':
            df = self.calculate_measures(df, 'KENESS', language)
            all_words = df['word'].tolist()
            
            
        elif cloud_type == '2_word_clusters':
            all_words = list(set([' '.join(g) for g in nltk.ngrams(json_data.split(), 2)]))
            
        elif cloud_type == '3_word_clusters':
            all_words = list(set([' '.join(g) for g in nltk.ngrams(json_data.split(), 3)]))
            
        elif cloud_type == '4_word_clusters':
            all_words = list(set([' '.join(g) for g in nltk.ngrams(json_data.split(), 4)]))
            
        elif cloud_type in ['nouns', 'proper nouns', 'verbs', 'adjectives', 'adverbs', 'numbers']:
            pos_dict = {'nouns': 'NOUN', 'proper nouns': 'PROPN', 'verbs': 'VERB', 
                        'adjectives': 'ADJ', 'adverbs': 'ADV', 'numbers': 'NUM'}
            doc = nlp(json_data) 
            all_words = [token.text for token in doc if token.pos_ == pos_dict[cloud_type]]
            
        elif cloud_type == 'semantic_tags':
            tags = self.Pymsas_tags(input_data) 
            tags_freq = tags.value_counts().reset_index()
            tags_freq.columns = ['USAS Tags', 'freq']

            # Handle semantic tags based on language
            if language == 'en':
                # This Bnc_sementic_tags loading can be done earlier for efficiency
                Bnc_sementic_tags = pd.read_csv('./website/static/keness/BNC_semantictags.csv')
                merged_df = pd.merge(tags_freq, Bnc_sementic_tags, on='USAS Tags', how='inner')
                
            elif language == 'cy':
                # You can load corcencc_sementic_tags earlier for efficiency
                corcencc_sementic_tags = pd.read_csv('./website/static/keness/Cy_semantictags.csv')
                merged_df = pd.merge(tags_freq, corcencc_sementic_tags, on='USAS Tags', how='inner')
            
            merged_df = merged_df.rename(columns={'USAS Tags': 'word','f_reference':'f_Reference' })
            print(merged_df)
            Tags_f_reference = self.calculate_measures(merged_df[['word', 'freq', 'f_Reference']], 'KENESS', language)
            all_words = Tags_f_reference['word'].tolist()
            
        else: 
            pass
        return all_words
    



    def generate_wordcloud(self, input_data, cloud_shape_path, cloud_outline_color, cloud_type, language):
        
        words_for_cloud = self.generate_wordcloud_type(input_data, cloud_type, language)
        return self.get_wordcloud(words_for_cloud, cloud_shape_path, cloud_outline_color)
