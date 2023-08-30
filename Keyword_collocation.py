import string
import re
import time
import os 
from collections import Counter
import spacy
from flask import Flask, render_template, request, jsonify
import pandas as pd
import networkx as nx
from pyvis.network import Network

STOPWORDS = set(["a", "an", "the", "and", "or", "in", "of", "to", "is", "it", "that", "on", "was", "for", "as", "with", "by"])  # Modify with actual stopwords
PUNCS = string.punctuation
nlp = spacy.load('en_core_web_sm-3.2.0')



import time
import os

def cleanup_old_graphs(directory, age_in_seconds=20): 
    current_time = time.time()

    for filename in os.listdir(directory):
        if filename.startswith("network_") and filename.endswith(".html"):
            file_timestamp = int(filename.split("_")[1].split(".")[0])
            file_age = current_time - file_timestamp

            if file_age > age_in_seconds:
                os.remove(os.path.join(directory, filename))


class KWICAnalyser:

    def __init__(self, text):
        self.text = self._preprocess_text(text)

    def _preprocess_text(self,text):
        # remove URLs, mentions, and hashtags
        #text = re.sub(r"http\S+|@\S+|#\S+", "", text)
        # remove punctuation and convert to lowercase
        text = re.sub(f"[{re.escape(''.join(PUNCS))}]", "", text.lower())
        # remove stopwords
        text = " ".join(word for word in text.split() if word not in STOPWORDS)
        return text

    def get_kwic(self, keyword, window_size=5, max_instances=30, lower_case=False):
        tokens = self.text.split()
        keyword_indexes = [i for i in range(len(tokens)) if tokens[i].lower() == keyword.lower()]
        kwic_insts = []

        for index in keyword_indexes[:max_instances]:
            left_context = ' '.join(tokens[index-window_size:index])
            target_word = tokens[index]
            right_context = ' '.join(tokens[index+1:index+window_size+1])
            kwic_insts.append((left_context, target_word, right_context))
        return kwic_insts

    def get_top_n_words(self, remove_stops=False, topn=30):
        text_tokens = [word for word in self.text.split() if word not in STOPWORDS] if remove_stops else self.text.split()
        return Counter(text_tokens).most_common(topn)

    def get_collocs(self, kwic_insts, topn=30):
        words = []
        for l, t, r in kwic_insts:
            words += l.split() + r.split()
        all_words = [word for word in words if word not in STOPWORDS]
        return Counter(all_words).most_common(topn)

    def plot_coll_14(self, keyword, collocs, output_file='network.html'):
        words, counts = zip(*collocs)
        top_collocs_df = pd.DataFrame(collocs, columns=['word', 'freq'])
        top_collocs_df.insert(1, 'source', keyword)
        top_collocs_df = top_collocs_df[top_collocs_df['word'] != keyword]  # remove row where keyword == word
        G = nx.from_pandas_edgelist(top_collocs_df, source='source', target='word', edge_attr='freq')
        n = max(counts)

        most_frequent_word = max(collocs, key=lambda x: x[1])[0]

        net = Network(notebook=True, height='750px', width='100%')
        gravity = -200 * n / sum(counts)
        net.barnes_hut(gravity=gravity* 30)

        for node, count in zip(G.nodes(), counts):
            node_color = 'green' if node == most_frequent_word else 'gray' if node == keyword else 'blue'
            node_size = 100 * count / n
            font_size = max(6, int(node_size / 2))
            net.add_node(node, label=node, title=node, color=node_color, size=node_size, font={'size': font_size, 'face': 'Arial'})

        for source, target, freq in top_collocs_df[['source', 'word', 'freq']].values:
            if source in net.get_nodes() and target in net.get_nodes():
                net.add_edge(source, target, value=freq)

        cleanup_old_graphs("website/static/network_graphs")
        timestamp = int(time.time())
        filename =  f"network_{timestamp}.html"
        graph_path = os.path.join("website/static/network_graphs", filename)
        net.save_graph(graph_path)

        # Return the relative path to the saved graph
        return f"/static/network_graphs/{filename}"


