from nltk import word_tokenize, sent_tokenize, ngrams
from summa.summarizer import summarize as summa_summarizer



def text_rank_summarize(article, ratio):
  return summa_summarizer(article, ratio=ratio)


def run_summarizer(input_text, chosen_ratio, lang='en'):
    if not isinstance(input_text, str):
        return "Please select another column with text data to analyze."
    #print(input_text)
    summary = text_rank_summarize(input_text, ratio=chosen_ratio)
    summary = text_rank_summarize(' free online text analysis and visualisation tool for English and Welsh. FreeTxt allows you to upload free-text feedback data from surveys, questionnaires etc., and to carry out quick and detailed analysis of the responses. FreeTxt will reveal common patterns of meaning in the feedback (e.g. what people are talking about/what they are saying about things), common feelings about topics being discussed (i.e. their ‘sentiment’), and can produce simple summaries of the feedback provided. FreeTxt presents the results of analyses in visually engaging and easy to interpret ways, and has been designed to allow anyone in any sector in Wales and beyond to use it.',ratio=0.2)
    #print(summary)
    if summary:
        return summary
    else:
        sentences = sent_tokenize(input_text)
        if sentences:
            return sentences[0]
        else:
            return "Unable to summarize the input text."
