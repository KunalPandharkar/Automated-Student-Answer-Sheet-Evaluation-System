from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import numpy as np
import os
import os,io
from google.cloud import vision_v1
import string
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import re
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/subjective_analysis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database object
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll = db.Column(db.String(30))
    marks = db.Column(db.Integer)
    total_marks = db.Column(db.Integer)

class QuestionAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100))
    answer = db.Column(db.String(600))
    question_marks = db.Column(db.Integer)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Get the uploaded image file
        # uploaded_file = request.files['file']
        uploaded_files = request.files.getlist('file')
        

        ans_text = ''

        for uploaded_file in uploaded_files:
            all_text = ''
            image_path = 'static/images/' + uploaded_file.filename
            uploaded_file.save(image_path)

        # Get the standard answer and marks
        # standard_answer = request.form['standard_answer']
        # marks = int(request.form['marks'])

            #Process Image
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'Google_Key.json'
            client = vision_v1.ImageAnnotatorClient()

            with io.open(os.path.join(image_path),'rb') as image_file:
                content = image_file.read()

            image = vision_v1.types.Image(content=content)

            response = client.text_detection(image=image)
            texts = response.text_annotations
            # Concatenate only the first item in the texts list
            all_text = texts[0].description if len(texts) > 0 else ''

            all_text = all_text.replace('\n', ' ')
            ans_text = ans_text + all_text


        print(ans_text)

        all_text = ans_text
        str_ans = all_text
        questions = {}
        index = 1

        for i in range(len(str_ans) - 1):
            if str_ans[i] == 'Q':
                i+=1
                while(str_ans[i] == ' '):
                    i += 1
                if str_ans[i].isdigit():
                    index = str_ans[i]
                    i += 1
                    j = i
                    temp_str = ''
                    while(True):
                        if(str_ans[j] == 'Q'):
                            temp = j
                            temp +=1 
                            while(str_ans[temp] == ' '):
                                temp += 1
                            if(str_ans[temp].isdigit()):
                                break
                        if j+1 == len(str_ans):
                            break
                        temp_str += str_ans[j]
                        j += 1
                    questions[index] = temp_str

       
        print("================================================================")
        print(questions)

        # Using replace() method to remove spaces
        output_str = all_text

        # output_str = output_str.lower()
        # print(output_str)

        # Using regular expression to extract roll number
        # Using regular expressions to extract roll number, name, and subject
        roll_pattern = r"\bBE\d+\w*"
        roll_match = re.search(roll_pattern, output_str)
        
        roll_number = 0

        if roll_match:
            roll_number = roll_match.group(0)
        else:
            print("No roll number found in the input string.")

        answers_db = QuestionAnswers.query.all()

        question_index = 0

        marks_scored = 0

        total_question_marks = 0
        
        for key,value in questions.items():
            # print('here-' ,value)
            # Define two sample answers
            answer_1 = str(value)
            answer_2 = answers_db[question_index].answer

        


            # Preprocess the text by removing punctuation and converting to lowercase
            translator = str.maketrans('', '', string.punctuation)
            answer_1 = answer_1.translate(translator).lower()
            answer_2 = answer_2.translate(translator).lower()

            # Tokenize the text by splitting on whitespace
            tokens_1 = nltk.word_tokenize(answer_1)
            tokens_2 = nltk.word_tokenize(answer_2)

            # Create a set of unique tokens
            unique_tokens = set(tokens_1 + tokens_2)

            # Vectorize the text using TF-IDF
            vectorizer = TfidfVectorizer(vocabulary=unique_tokens)
            vectors = vectorizer.fit_transform([answer_1, answer_2]).toarray()

            # Calculate the cosine similarity between the two vectors
            similarity = cosine_similarity([vectors[0]], [vectors[1]])[0][0]

            # Generate the percentage of correctness
            percentage_correct = similarity * 100
            percentage_correct = round(percentage_correct)

            total_question_marks += int(answers_db[question_index].question_marks)

            student_marks = (int(percentage_correct) / 100) * int(answers_db[question_index].question_marks)

            student_marks = round(student_marks)

            marks_scored += student_marks

            # print("compare - ",answer_1," with - ", answer_2," marks scored - ",marks_scored," percetnage correct - ", percentage_correct)
            question_index += 1
        print("total makrs scored - ",marks_scored)


        # Insert data into the database
        student = Student(roll=roll_number, marks=marks_scored,total_marks=total_question_marks)
        db.session.add(student)
        db.session.commit()
        


        percentage_student = round((marks_scored/ total_question_marks) * 100)

        # Generate a pie chart
        labels = ['Correct', 'Incorrect']
        sizes = [int(percentage_student), 100 - int(percentage_student)]
        explode = (0.1, 0)
        fig, ax = plt.subplots()
        ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
        ax.axis('equal')
        chart_path = 'static/images/chart.png'
        plt.savefig(chart_path)

        # Clear the plot to avoid issues with overlapping images
        plt.clf()

     
        # Render the HTML template with the uploaded image file, textarea, and pie chart
        return render_template('result.html', image_path=uploaded_files, student_marks=marks_scored, chart_path=chart_path,total_marks=total_question_marks,student_percentage=percentage_student,roll_number=roll_number)
    student_count = db.session.query(Student).count()
    questions_count = db.session.query(QuestionAnswers).count()
    questions = QuestionAnswers.query.all()
        

    return render_template('upload.html',questions_count=questions_count,student_count=student_count,questions=questions)


# Define a route to handle form submission
@app.route("/submit_questionpaper",methods=['GET', 'POST'])
def submit_questionpaper():
    if request.method == 'POST':
        input_number = int(request.form['input-number'])
        inputs = []
        textareas = []
        marks = []
        for i in range(input_number):
            inputs.append(request.form[f'input-{i}'])
            textareas.append(request.form[f'textarea-{i}'])
            marks.append(request.form[f'marks-{i}'])
        # Do something with the inputs and textareas
        # Insert data into the database
        for i in range(len(inputs)):
            student = QuestionAnswers(question=inputs[i], answer=textareas[i],question_marks=marks[i])
            db.session.add(student)
            db.session.commit()
    questions = QuestionAnswers.query.all()
        
    return render_template("addQuestions.html",questions=questions)


@app.route('/allresults')
def download_results():
    students = Student.query.all()
    return render_template("allresults.html",students=students)

if __name__ == '__main__':
    # Create the images directory if it doesn't exist
    image_dir = 'static/images'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
