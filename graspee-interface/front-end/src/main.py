from flask import Flask, request, render_template, redirect, url_for
import os, sys
import time
##################
import bert
import neuspell
from neuspell import BertChecker
##################

########## Language Models #########
# Initialize spelling check model
checker = BertChecker()
checker.from_pretrained()

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
    correct_text = checker.correct(original_text)

    data = {
        'student_name':student_name,
        'assignment_nbr':assignment_nbr,
        'original_text':original_text,
        'correct_text':correct_text
    }
    return render_template('grading.html', data=data)



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
        
    inp_string = [x for x in request.form.values()]
    sent = inp_string[0]
    index = bert.bert_checker(sent)
    print(index)
    return render_template('predict.html', sent=sent, index=index.item())



if __name__ == "__main__":
    app.run(debug=True)