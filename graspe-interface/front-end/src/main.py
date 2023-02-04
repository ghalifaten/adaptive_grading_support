from flask import Flask, request, render_template, redirect, url_for, jsonify
import os, sys
import time
import math
import re

import neuspell
from neuspell import BertChecker
from transformers import BertForSequenceClassification, BertTokenizer
import bert
from transformers import pipeline
##################

########## Language Models #########
# Initialize spelling check model
print('\nLoading spelling checker...\n')
checker = BertChecker()
checker.from_pretrained("./neuspell-subwordbert-probwordnoise/")

# Initialize grammar check model
print('\nLoading BERT model and tokenizer...\n')
tokenizer = BertTokenizer.from_pretrained("fatenghali/bert-tokenizer")
model_loaded = BertForSequenceClassification.from_pretrained("fatenghali/bert-grammar-checker")

# Initialize pipeline for the argumentation check (text classification model)
print('\nLoading argumentation check model...\n')
text_classifier = pipeline("sentiment-analysis", model="fatenghali/text_classification_model")

#####################################

app = Flask(__name__, template_folder='templates')

## STUDENT INTERFACE ##
@app.route('/submit', methods=['GET','POST'])
def submit():    
    return render_template("submit.html")


def uncommonWords(text, correct):
    """
    find the list of uncommon words between two texts.
    """
    count = {}
    # insert words of string A to hash
    for word in text.split():
        count[word] = count.get(word, 0) + 1

    # insert words of string B to hash
    for word in correct.split():
        count[word] = count.get(word, 0) - math.inf

    # return required list of words
    return [word for word in count if count[word] > 0 ]

## TEACHER INTERFACE ##
@app.route('/', methods=['GET', 'POST'])
def grade_compare():
    if request.method == 'GET':
        return render_template("grading_comparison.html")

    if request.method == 'POST':
        s1 = time.time()
        original_text = request.get_json()['original_text']
        print("\n text received by Flask : ", time.time() - s1, "\n")
        """
        Spelling check
        """
        s2 = time.time()
        #passing batches of sentences instead of large text avoids text truncation when text is too long for the model.
        batches = original_text.split('. ')
        print("split: ", time.time() - s2)
        ss2 = time.time()
        corrected_batches = checker.correct_strings(batches)
        print("checker: ", time.time() - ss2)
        sss2 = time.time()
        #Neuspell separates words from punctuation and inserts space before each in the returned result. So we fix that here to make the corrected text prettier and easier to compare to the original.
        for i in range(len(corrected_batches)):
            sentence = corrected_batches[i]
            sentence = sentence.replace(' , ', ', ')\
                                .replace(' ; ', '; ')\
                                .replace(' - ', '-')\
                                .replace(" ' ", "'")\
                                .replace(' ! ', '! ')\
                                .replace(' ? ', '? ')\
                                .replace(' % ', '% ')\
                                .replace(' @ ', '@')\
                                .replace(' ( ', ' (')\
                                .replace(' ) ', ') ')\
                                .replace(' .', '.')
            corrected_batches[i] = sentence
        print("for loop: ", time.time() - sss2)
        #Compare between each couple of sentences (original and corrected) to find uncommon words, aka spelling mistakes
        mistakes_nbr = 0
        highlighted_text = ''
        ssss2 = time.time()
        for (orig, corr) in zip(batches, corrected_batches):
            mistakes = uncommonWords(orig, corr)
            mistakes_nbr += len(mistakes)
            for m in mistakes:
                orig = orig.replace(m, '<span style="color: red">'+m+'</span>')
            highlighted_text += orig + '. ' 
        print("2nd for loop: ", time.time() - ssss2)
        print("\n SPELLING CHECK IS DONE: ", time.time() - s2, "\n")

        """
        Grammar check
        """
        s3 = time.time()
        sentences = original_text.split('. ')
        sentences = list(filter(None, sentences))
        indices = list(map(lambda sent: bert.bert_checker(model_loaded, tokenizer, sent), sentences))
        indices = list(map(lambda index: index.item(), indices))

        grammar_check_results = [(sentences[i], indices[i]) for i in range(0, len(sentences))] #merge sentences and corresponding indices in list of tuples to keep order of sentences when sent to JavaScript

        print("\n GRAMMAR CHECK IS DONE: ", time.time() - s3, "\n")

        """
        Argumentation check
        """
        s4 = time.time()
        sentences = original_text.split('. ')
        predictions = text_classifier(sentences)
        for pred, sent in zip(predictions, sentences): #append sentences to their labels
            pred['sentence'] = sent

        print("\n ARGUMENTATION CHECK IS DONE: ", time.time() - s4, "\n")

        #-------
        data = {
            'spell_check_result': highlighted_text,
            'spell_check_mistakes': mistakes_nbr,
            'grammar_check_results':grammar_check_results,
            'predictions': predictions,
        }

        return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)