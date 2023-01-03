from flask import Flask, request, render_template, redirect, url_for, jsonify
import os, sys
import time
import math
import re
##################
import neuspell
from neuspell import BertChecker
#from transformers import BertForSequenceClassification, BertTokenizer
#import bert
from transformers import pipeline
##################

########## Language Models #########
# Initialize spelling check model
checker = BertChecker()
checker.from_pretrained()

# Initialize grammar check model
#print('Loading BERT tokenizer...')
#output_dir = '/home/faten/ml4ed/adaptive_grading_support/graspee-interface/front-end/lib/model_bert/'
#model_loaded = BertForSequenceClassification.from_pretrained(output_dir)
#tokenizer = BertTokenizer.from_pretrained(output_dir)

# Initialize pipeline for the argumentation check (text classification model)
text_classifier = pipeline("sentiment-analysis", model="fatenghali/text_classification_model")

#####################################

app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET','POST'])
def index():
    if  request.method == 'POST':
        assignment_nbr = request.form['assignment-nbr']
        student_name = request.form['student-name']
        text = request.form['text-body']
        return redirect(url_for("grading", text=text, assignment_nbr=assignment_nbr, student_name=student_name))
    
    return render_template("index.html")

@app.route('/grading', methods=['GET', 'POST'])
def grading():
    """ 
    if  request.method == 'POST':
        feedback = request.form['feedback-text']
        sub_grade_1 = request.form['sub-grade-1']
        sub_grade_2 = request.form['sub-grade-2']
        sub_grade_3 = request.form['sub-grade-3']
        sub_grade_4 = request.form['sub-grade-4']
        return redirect(url_for("summary", feedback=feedback, sub_grade_1=sub_grade_1, sub_grade_2=sub_grade_2, sub_grade_3=sub_grade_3, sub_grade_4=sub_grade_4))

    original_text = request.args.get('text', None)
    assignment_nbr = request.args.get('assignment_nbr', None)
    student_name = request.args.get('student_name', None)

    #Spell check
    spell_correct_text = checker.correct(original_text)

    #grammar check
    list_sentences = original_text.split('.')
    list_sentences = list(filter(None, list_sentences))
    indices = list(map(lambda sent: bert.bert_checker(model_loaded, tokenizer, sent), list_sentences))
    indices = list(map(lambda index: index.item(), indices))
    grammar_check_results = dict(zip(list_sentences, indices))
    print(grammar_check_results)

    #-------
    data = {
        'student_name':student_name,
        'assignment_nbr':assignment_nbr,
        'original_text':original_text,
        'spell_correct_text':spell_correct_text,
        'grammar_check_results':grammar_check_results
    }
    """
    return render_template('grading.html', data=data)

@app.route('/comparison')
def comparison():
    return render_template('comparison.html')

@app.route('/summary')
def summary():
    feedback = request.args.get('feedback', None)
    sub_grade_1 = request.args.get('sub_grade_1', None)
    sub_grade_2 = request.args.get('sub_grade_2', None)
    sub_grade_3 = request.args.get('sub_grade_3', None)
    sub_grade_4 = request.args.get('sub_grade_4', None)
    return render_template('summary.html', feedback=feedback, sub_grade_1=sub_grade_1, sub_grade_2=sub_grade_2, sub_grade_3=sub_grade_3, sub_grade_4=sub_grade_4)




@app.route('/predict', methods=['GET','POST'])
def predict():
    '''
    For rendering results on HTML GUI
    '''
    if request.method == 'GET':
        return render_template('predict.html')
    
    start = time.time()
    inp_string = [x for x in request.form.values()]
    sent = inp_string[0]
    list_sentences = sent.split('.')
    print("list_sentences before = ", list_sentences)
    list_sentences = list(filter(None, list_sentences))
    print("list_sentences filtered = ", list_sentences)

    indices = list(map(lambda sent: bert.bert_checker(model_loaded, tokenizer, sent), list_sentences))
    indices = list(map(lambda index: index.item(), indices))
    print(time.time()-start)
    res_prediction = dict(zip(list_sentences, indices))
    return render_template('predict.html', sent=sent, res_prediction=res_prediction)

###############
@app.route('/grading-comparison', methods=['GET', 'POST'])
def grade_compare():
    if request.method == 'GET':
        return render_template("grading_comparison.html")

    if request.method == 'POST':
        original_text = request.get_json()['original_text']

        #Spell check

        text, n = re.subn('[.,;:!?(){\}<>"-*@+]', ' ', original_text.lower())
        correct = checker.correct(text)

        def uncommonWords(text, correct):
            count = {}
            # insert words of string A to hash
            for word in text.split():
                count[word] = count.get(word, 0) + 1

            # insert words of string B to hash
            for word in correct.split():
                count[word] = count.get(word, 0) - math.inf

            # return required list of words
            return [word for word in count if count[word] > 0 ]

        misspelled_words = uncommonWords(text, correct)

        #argumentation check
        print("\n************* argumentation check *******************\n")
        sentences = original_text.split('. ')
        print("\n",sentences,"\n")
        predictions = text_classifier(sentences)
        for pred, sent in zip(predictions, sentences): #append sentences to their labels
            pred['sentence'] = sent
        print("************* argumentation check finished *******************")
        #-------
        data = {
            'misspelled_words': misspelled_words,
            'predictions': predictions,
        }
        return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)