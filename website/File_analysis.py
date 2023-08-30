from flask import Blueprint, render_template, request, flash, jsonify, send_from_directory
from flask import session
from flask import redirect
from werkzeug.utils import secure_filename
from collections import Counter
from flask import current_app
import re
import os
import time
import random
from sentiment_analyser import SentimentAnalyser
from word_tree_generator import WordTreeGenerator
from Summariser import run_summarizer
from word_cloud_generator import WordCloudGenerator
from Keyword_collocation import KWICAnalyser
import pandas as pd
import plotly.express as px
import threading

import string
from nltk.corpus import stopwords
en_stopwords = list(stopwords.words('english'))
cy_stopwords = open('./website/data/welsh_stopwords.txt', 'r', encoding='iso-8859-1').read().split('\n') # replaced 'utf8' with 'iso-8859-1'
STOPWORDS = set(en_stopwords + cy_stopwords+ ["a", "an", "the", "and", "or", "in", "of", "to", "is", "it", "that", "on", "was", "for", "as", "with", "by"])

PUNCS = string.punctuation

PUNCS += '''!→()-[]{};:'"\,<>./?@#$%^&*_~'''
# Initialize a lock
file_lock = threading.Lock()

FileAnalysis = Blueprint('fileanalysis', __name__)

#### utilities
ALLOWED_EXTENSIONS = {'txt', 'csv', 'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_file(file_path):
    if file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path)
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as f:
            lines = f.readlines()
            data = pd.DataFrame(lines, columns=['Reviews'])
    else:
        data = pd.DataFrame()

    # The Date normalization code from Streamlit can be added here.
    # ...

    return data
import os

def cleanup_expired_sessions():
    filepath = session.get('uploaded_file_path')
    if filepath and not os.path.exists(filepath):
        return

    # Check if the session is expired
    # This is a simple example; your session management might be different.
    if 'expiration_time' in session and session['expiration_time'] <= time.time():
        os.remove(filepath)
        session.pop('uploaded_file_path', None)  # remove the filepath from the session


@FileAnalysis.route('/fileanalysis', methods=['GET', 'POST'])
def fileanalysis():
    sentences = []
    if request.method == 'POST':
        input_method = request.form.get('input-method') or request.json.get('input_method')
      
        if input_method == 'text':
           
            text = request.form.get('text-to-analyze')
            raw_sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
            #sentences = [{"Sentences": sentence} for sentence in raw_sentences]
            sentences = [ sentence for sentence in raw_sentences]
            #print(sentences)
            
        
        elif input_method == 'example':
            example_file = request.form.get('example-data')
            # Modify the path accordingly to point to where your example files are stored
            file_path = os.path.join('website/example_texts_pub', example_file)  
            sentences = read_file(file_path)
        
        elif input_method == 'upload':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
        
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
        
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                session['uploaded_file_path'] = filepath  # save the file path to session
                data = read_file(filepath)
                session['data'] = data.to_json()  # Convert the DataFrame to JSON and store in session
                return jsonify({"columns": list(data.columns)})
                
            else:
                flash('Invalid file type')
                return redirect(request.url)

        elif input_method == 'columns':
            selected_columns = request.json.get('selectedColumns')
    
            data_json = session.get('data')
            if not data_json:
                return jsonify({"message": "No data found in session", "data": []})

            data = pd.read_json(data_json)  # Convert the JSON back to DataFrame
            extracted_data = data[selected_columns].dropna().drop_duplicates().to_dict(orient='records')
            session['extracted_data'] = pd.DataFrame(extracted_data).to_json()
            #print(extracted_data)
            
            return jsonify({"message": "Data extracted", "data": extracted_data})
           
        #cleanup_expired_sessions()
        return jsonify({"sentences": sentences})

    return render_template('Fileanalysis.html')

@FileAnalysis.route('/process_sentences', methods=['GET', 'POST'])
def handle_selected_sentences():
    data = request.get_json()
    selected_sentences = data.get('sentences', [])
   
    search_word = data.get('search_word', 'see')
    # Get word frequencies
    words = []
    for sentence in selected_sentences:
        extracted_words = re.findall(r'\w+', sentence.lower())
        filtered_words = [word for word in extracted_words if word not in STOPWORDS and word not in PUNCS]
        words.extend(filtered_words)

            # Counting frequencies
    word_frequencies = dict(Counter(words))
    # Sorting by highest frequency
    sorted_word_frequencies = dict(sorted(word_frequencies.items(), key=lambda item: item[1], reverse=True))

    sentiment_analyser = SentimentAnalyser()
    # Get sentiment analysis results
    sentiment_data, sentiment_counts, pie_chart_html,bar_chart_html = sentiment_analysis(selected_sentences)
    df_sentiment= pd.DataFrame(sentiment_data)
    with file_lock:
        scatter_text_html = sentiment_analyser.generate_scattertext_visualization(df_sentiment)
    ## Word Tree Generator
    sentences = [[s] for s in selected_sentences]
    #sentences = ''.join(str(sentences))
    #generator = WordTreeGenerator(selected_sentences)
    #word_tree_html = generator.generate_html(search_word,selected_sentences)
    wordTreeData = sentences  # This should be a list
    summary = summarize(' '.join(selected_sentences),20/100)
    #print(summary)
    return jsonify({
        "status": "success", 
        "wordFrequencies": sorted_word_frequencies, 
        "sentimentData": sentiment_data, 
        "sentimentCounts": sentiment_counts,
        'sentimentPlotPie': pie_chart_html,
        'sentimentPlotBar': bar_chart_html,
        "wordTreeData": wordTreeData, "search_word": search_word, "summary": summary,  "scatterTextHtml": scatter_text_html
    })

def sentiment_analysis(sentences):
    analyser = SentimentAnalyser()
    results = analyser.analyse_sentiment(sentences, 5)
    if results:
        sentiments, sentiment_counts = results
        dfanalysis = pd.DataFrame(sentiments, columns=['Review', 'Sentiment Label', 'Sentiment Score'])
        data = dfanalysis.to_dict(orient='records')
        
        # Generating the pie chart
        fig = px.pie(values=sentiment_counts.values(), names=sentiment_counts.keys(), title='Sentiment Distribution')
        plot_html_pie = fig.to_html(full_html=False)
        # Generating the bar chart
        fig_bar = px.bar(x=list(sentiment_counts.keys()), y=list(sentiment_counts.values()), 
             title='Sentiment Distribution', labels={'x':'Sentiment', 'y':'Count'})

        plot_html_bar = fig_bar.to_html(full_html=False)
        return data, sentiment_counts, plot_html_pie, plot_html_bar
    return None, None, None

def summarize(text, chosen_ratio):
    summary = run_summarizer(text, chosen_ratio) 
    #print(summary)
    return summary



@FileAnalysis.route('/summarise', methods=['POST'])
def summarize_route():
    data = request.get_json()
    text = data.get('sentences', [])
    chosen_ratio = float(request.form.get('chosen_ratio', 10)) / 100
    summary = run_summarizer(text, chosen_ratio) 
    print('Generated summary',summary)
    return jsonify({"summary": summary})


@FileAnalysis.route('/clear-session', methods=['POST'])
def clear_session():
    filepath = session.get('uploaded_file_path')
    print(filepath)
    if filepath and os.path.exists(filepath):
        os.remove(filepath)
        session.pop('uploaded_file_path', None)  # remove the filepath from the session
    session.clear()  # clear other session data if needed
    return jsonify({"message": "Session cleared"})

@FileAnalysis.route('/process_rows', methods=['GET', 'POST'])
def handle_selected_rows():
    data = request.get_json()
    merged_rows = data.get('mergedData', [])

    # Get word frequencies
    words = []
    for sentence in merged_rows:
        extracted_words = re.findall(r'\w+', sentence.lower())
        filtered_words = [word for word in extracted_words if word not in STOPWORDS and word not in PUNCS]
        words.extend(filtered_words)

            # Counting frequencies
    word_frequencies = dict(Counter(words))
    # Sorting by highest frequency
    sorted_word_frequencies = dict(sorted(word_frequencies.items(), key=lambda item: item[1], reverse=True))

    # Choose a random word from the list as the search word
    search_word = random.choice(words) if words else 'castle'
    sentiment_analyser = SentimentAnalyser()
    # Get sentiment analysis results
    sentiment_data, sentiment_counts, pie_chart_html, bar_chart_html = sentiment_analysis(merged_rows)

    df_sentiment= pd.DataFrame(sentiment_data)
    with file_lock:
        scatter_text_html = sentiment_analyser.generate_scattertext_visualization(df_sentiment)

    # Word Tree Generator
    sentences = [[s] for s in merged_rows]
    wordTreeData = sentences
    
    summary = summarize(' '.join(merged_rows), 20/100)

    return jsonify({
        "status": "success",
        "wordFrequencies": word_frequencies,
        "sentimentData": sentiment_data,
        "sentimentCounts": sentiment_counts,
        'sentimentPlotPie': pie_chart_html,
        'sentimentPlotBar': bar_chart_html,
        "wordTreeData": wordTreeData,
        "search_word": search_word,
        "summary": summary,
        "scatterTextHtml": scatter_text_html
    })

@FileAnalysis.route('/get_exampledata_files')
def get_files():
    directory = 'website/example_texts_pub'
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    return jsonify(files)


@FileAnalysis.route('/generate_wordcloud', methods=['POST','GET'])
def generate_wordcloud():
    if request.method == 'POST':
        request_data = request.get_json(force=True)
        print(request.headers.get('Content-Type'))
        cloud_shape_path = request_data.get('cloud_shape')
        cloud_outline_color = request_data.get('cloud_outline_color')
        cloud_type = request_data.get('cloud_type')
        print(cloud_shape_path)
        if cloud_type is None:
            request_data = request.json
            cloud_type = request_data['cloud_type']
            cloud_shape_path = request_data['cloud_shape']
            cloud_outline_color = request_data['cloud_outline_color']
            if cloud_type is None:
                cloud_type = 'all_words'
                cloud_shape_path = './website/static/images/img/cloud.png'
                cloud_outline_color= 'white'
        cloud_generator = WordCloudGenerator()
        language = 'en'
        data_json = session.get('extracted_data')
        input_data = pd.read_json(data_json)
        cloud_generator = WordCloudGenerator()
        wc_path,word_list = cloud_generator.generate_wordcloud(input_data, cloud_shape_path, cloud_outline_color, cloud_type, language)
        return jsonify({
            "status": "success",
            "wordcloud_image_path": wc_path,
            "word_list":word_list
        })
    return jsonify({"status": "error", "message": "Invalid request method"})


@FileAnalysis.route('/Keyword_collocation', methods=['POST'])
def analyse():
    if 'word_selection' in request.form:
        selected_word = request.form['word_selection']
        
        data_json = session.get('extracted_data')
        #input_data = pd.DataFrame(data_json)
        
        analyzer = KWICAnalyser(data_json)
        kwic_results = analyzer.get_kwic(selected_word)
        collocs = analyzer.get_collocs(kwic_results)
        
        analyzer.plot_coll_14(selected_word, collocs)
        word_frequencies = analyzer.get_top_n_words(remove_stops=True)
        graph_path = analyzer.plot_coll_14(selected_word, collocs)
        # Assuming you want to send back the results as a JSON for AJAX processing
        return jsonify({
            "kwic_results": kwic_results,
            "collocs": collocs,"graph_path": graph_path
        
        })
    else:
        return jsonify({"error": "No word selected!"})

