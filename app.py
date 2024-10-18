from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import matplotlib.pyplot as plt
import os, io
from google.cloud import vision_v1
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from flask_sqlalchemy import SQLAlchemy
import signal
import sys
import matplotlib
import boto3
import nltk


matplotlib.use('Agg')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost:3306/subjective_analysis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect here if user tries to access a protected route

def signal_handler(sig, frame):
    print('Shutting down...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
# Initialize database object
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll = db.Column(db.String(30))
    marks = db.Column(db.Integer)
    total_marks = db.Column(db.Integer)
       # Add test_id as a foreign key referencing the ClassesTests table
    test_id = db.Column(db.Integer, db.ForeignKey('classes_tests.id'), nullable=True)  # Adjust the table name as needed
    marks_details = db.Column(db.JSON)  # Store detailed marks for each question as a JSON object
    # Relationship to access the related test information
    class_test = db.relationship('ClassesTests', back_populates='students')  # This will point to 'students' in ClassesTests

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    mobile_number = db.Column(db.String(15))
    password = db.Column(db.String(128))
    @property
    def is_active(self):
        # Return True if the teacher is active (implement your own logic if necessary)
        return True  # or add your logic here

    @property
    def is_authenticated(self):
        return True  # This will be handled by Flask-Login

    @property
    def is_anonymous(self):
        return False  # This will also be handled by Flask-Login

    def get_id(self):
        return str(self.id)  # Return the unique ID of the teacher
    
      # Relationship with TeachersClasses
    teacher_classes = db.relationship('TeachersClasses', back_populates='teacher')

    # Relationship with ClassesTests
    teacher_test_classes = db.relationship('ClassesTests', back_populates='teacher_classtests')


class TeachersClasses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    subject = db.Column(db.String(100))
    studentcount = db.Column(db.Integer, nullable=False)
    
    # Foreign key referencing the teachers table
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    
      # Relationship to access the teacher's information from this table
    teacher = db.relationship('Teacher', back_populates='teacher_classes')

    # Relationship with ClassesTests
    class_tests = db.relationship('ClassesTests', back_populates='teachers_classes')

    
class ClassesTests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # New fields for test information
    test_name = db.Column(db.String(100), nullable=False)   # Test name
    test_date = db.Column(db.Date, nullable=False)          # Test date
    total_marks = db.Column(db.Integer, nullable=False)     # Total marks for the test
    test_subject = db.Column(db.String(100))


    # Foreign key referencing the TeachersClasses table
    class_id = db.Column(db.Integer, db.ForeignKey('teachers_classes.id'), nullable=False)

    # Relationship to access the class information from this table
    teachers_classes = db.relationship('TeachersClasses', back_populates='class_tests')

    # Foreign key referencing the teachers table
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    # Relationship to access the teacher's information from this table
    teacher_classtests = db.relationship('Teacher', back_populates='teacher_test_classes')

    # Relationship to access all students who took this test
    students = db.relationship('Student', back_populates='class_test')  # Allows accessing students who took this test

class QuestionAnswers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(100))
    answer = db.Column(db.String(600))
    question_marks = db.Column(db.Integer)
     # Foreign key referencing the teachers table
    classtest_id = db.Column(db.Integer, db.ForeignKey('classes_tests.id'), nullable=False)
    # Relationship to access the teacher's information from this table
    teacher = db.relationship('ClassesTests', backref=db.backref('classes', lazy=True))


@login_manager.user_loader
def load_user(user_id):
    return Teacher.query.get(int(user_id))  # Adjust based on your user model

# Route for teacher signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        mobile_number = request.form['mobile_number']
        password = request.form['password']

        # Check if the mobile number already exists
        teacher = Teacher.query.filter_by(mobile_number=mobile_number).first()
        if teacher:
            flash('Mobile number already registered. Please login.', 'error')
            return redirect(url_for('login'))

        # Hash the password for security
        password_teacher = password

        # Add the new teacher to the database
        new_teacher = Teacher(name=name, mobile_number=mobile_number, password=password_teacher)
        db.session.add(new_teacher)
        db.session.commit()

        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Route for teacher login
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()  # Clears all session data

    # Check if the teacher is already logged in
    if 'teacher_id' in session:
        flash('You are already logged in.', 'info')
        return redirect(url_for('create_test'))  # Redirect to home page
    
    if request.method == 'POST':
        mobile_number = request.form['mobile_number']
        password = request.form['password']

        # Find the teacher by mobile number
        teacher = Teacher.query.filter_by(mobile_number=mobile_number).first()

        print('here',teacher.password)


        

        if teacher and (teacher.password == password):
            # Store teacher ID in session to track login
            session['teacher_id'] = teacher.id
            session['teacher_name'] = teacher.name
            print('here',teacher.name)
            flash(f'Welcome, {teacher.name}!', 'success')
            flash('You have been logged out.', 'success')
            login_user(teacher)
            return redirect(url_for('create_test'))
        else:
            flash('Invalid login credentials. Please try again.', 'error')

    return render_template('login.html')
# Route for teacher logout
@app.route('/logout')
def logout():
    session.pop('teacher_id', None)
    session.pop('teacher_name', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/teacher_profile', methods=['GET', 'POST'])
def teacher_profile():
    if 'teacher_id' not in session:
        flash('Please log in to access your profile.')
        return redirect(url_for('login'))

    # Fetch the logged-in teacher from the database
    teacher = Teacher.query.filter_by(id=session['teacher_id']).first()

       # Calculating totals
    total_classes = TeachersClasses.query.filter_by(teacher_id=teacher.id).count()
    total_students = sum([cls.studentcount for cls in teacher.teacher_classes])
    total_tests = ClassesTests.query.filter_by(teacher_id=teacher.id).count()

    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        mobile_number = request.form['mobile_number']

        # Update teacher information
        if name and mobile_number:
            teacher.name = name
            teacher.mobile_number = mobile_number

            # Commit the changes to the database
            db.session.commit()
            flash('Profile updated successfully!')
        else:
            flash('All fields are required.')

    return render_template('teacher_profile.html', teacher=teacher,total_classes=total_classes, total_students=total_students, total_tests=total_tests)

@app.route('/create_class', methods=['GET', 'POST'])
@login_required
def create_class():
    if request.method == 'POST':
        class_name = request.form['class_name']
        subject = request.form['subject']
        student_count = request.form['student_count']

        # Create a new class entry in the database
        new_class = TeachersClasses(
            teacher_id=session['teacher_id'],
            name=class_name,
            subject=subject,
            studentcount=student_count
        )
        db.session.add(new_class)
        db.session.commit()

        flash('Class created successfully!')
        return redirect(url_for('create_class'))
     # Get classes created by the logged-in teacher
    classes = TeachersClasses.query.filter_by(teacher_id=current_user.id).all()
    return render_template('create_class.html', classes=classes)

@app.route('/create_test/', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
@login_required  # Ensure the teacher is logged in
def create_test():
    # class_info = TeachersClasses.query.get(class_id)
    
    if request.method == 'POST':
        test_name = request.form['exam_name']
        test_date = request.form['exam_date']
        total_marks = request.form['total_marks']
        test_subject = request.form['subject_name']
        class_id = request.form['class_id']
        
        # Create a new test entry
        new_test = ClassesTests(test_name=test_name, test_date=test_date, total_marks=total_marks,test_subject=test_subject,class_id=class_id, teacher_id=current_user.id)
        db.session.add(new_test)
        db.session.commit()

        flash('Test created successfully!', 'success')
        return redirect(url_for('create_test'))  # Redirect to the classes page
      # Get classes created by the logged-in teacher
        # Fetch classes for the dropdown
    classes = TeachersClasses.query.filter_by(teacher_id=current_user.id).all()
    class_tests = ClassesTests.query.filter_by(teacher_id=current_user.id).all()

    return render_template('create_test.html',exams=class_tests,classes=classes)  # Render the test creation form

@app.route('/delete_test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    # Find the class by ID
    test_to_delete = ClassesTests.query.get(test_id)
    if test_to_delete:
        db.session.delete(test_to_delete)
        db.session.commit()
        flash('Test deleted successfully!', 'success')
    else:
        flash('Test not found!', 'danger')
    
    return redirect(url_for('create_test'))  # Redirect back to the create class page

@app.route('/update_test/<int:test_id>', methods=['GET', 'POST'])
def update_test(test_id):
    test_to_update = ClassesTests.query.get_or_404(test_id)

    if request.method == 'POST':
        test_to_update.test_name = request.form['exam_name']
        test_to_update.test_date = request.form['exam_date']
        test_to_update.total_marks = request.form['total_marks']
        test_to_update.test_subject = request.form['subject_name']
        
        db.session.commit()
        return redirect(url_for('create_test'))

    return render_template('update_test.html', test_name=test_to_update)

@app.route('/update_class/<int:class_id>', methods=['GET', 'POST'])
def update_class(class_id):
    class_to_update = TeachersClasses.query.get_or_404(class_id)

    if request.method == 'POST':
        class_to_update.name = request.form['class_name']
        class_to_update.subject = request.form['subject']
        class_to_update.studentcount = request.form['student_count']
        
        db.session.commit()
        return redirect(url_for('create_class'))

    return render_template('update_class.html', class_name=class_to_update)

@app.route('/delete_class/<int:class_id>', methods=['POST'])
def delete_class(class_id):
    # Find the class by ID
    class_to_delete = TeachersClasses.query.get(class_id)
    if class_to_delete:
        db.session.delete(class_to_delete)
        db.session.commit()
        flash('Class deleted successfully!', 'success')
    else:
        flash('Class not found!', 'danger')
    
    return redirect(url_for('create_class'))  # Redirect back to the create class page

# Preprocess the text by removing punctuation and converting to lowercase
def preprocess(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator).lower()

# Remove stopwords
def remove_stopwords(tokens):
    stop_words = set(stopwords.words('english'))
    return [word for word in tokens if word not in stop_words]

# Calculate Jaccard similarity
def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0


# Main comparison function
def compare_answers(answer_1, answer_2):
    # Preprocess the answers
    answer_1 = preprocess(answer_1)
    answer_2 = preprocess(answer_2)

    # Tokenize the answers and remove stopwords
    tokens_1 = remove_stopwords(word_tokenize(answer_1))
    tokens_2 = remove_stopwords(word_tokenize(answer_2))

    # Calculate Jaccard similarity
    set1 = set(tokens_1)
    set2 = set(tokens_2)
    similarity = jaccard_similarity(set1, set2)

    # Generate the percentage of correctness
    percentage_correct = similarity * 100
    return round(percentage_correct)

@app.route('/generate_result/<int:test_id>', methods=['GET', 'POST'])
def generate_result(test_id):
    # Check if the teacher is logged in
    if 'teacher_id' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
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
              # Initialize Textract client
              # Initialize Textract client
            textract_client  = boto3.client(
            'textract',
            aws_access_key_id='AKIASFUIRR42GZPBWOSB',
            aws_secret_access_key='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',
            region_name='us-east-1')
           

             #Process Image
            with io.open(os.path.join(image_path),'rb') as image_file:
                image_bytes = image_file.read()

            # Call Amazon Textract to extract text from the image
            response = textract_client.detect_document_text(
                Document={'Bytes': image_bytes}
            )
            # Check if 'Blocks' exists in response
            if 'Blocks' not in response:
                print("Error: No 'Blocks' found in response.")
                return ""
              # Extract the detected text
            extracted_text = ""
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE':
                    extracted_text += block['Text'] + '\n'
            
            ans_text = ans_text + extracted_text


        print(ans_text)

        # ans_text = 'Roll - 2021 01103 0003qererdafd Q1) dbms is known a  managementt '

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
        # roll_pattern = r"\bBE\d+\w*"
        # roll_match = re.search(roll_pattern, output_str)
        
        # roll_number = 0

        # if roll_match:
        #     roll_number = roll_match.group(0)
        # else:
        #     print("No roll number found in the input string.")

        roll_number = extract_prn_number(output_str)

        answers_db = QuestionAnswers.query.filter_by(classtest_id=test_id).all()

        question_index = 0

        marks_scored = 0

        total_question_marks = 0

        student_marks_details = {}  # Dictionary to store question marks details

        
        print("======================================")
        
        for key,value in questions.items():
            # print('here-' ,value)
            # Define two sample answers
            answer_1 = str(value)
            answer_2 = answers_db[question_index].answer

        
            percentage_correct = compare_answers(answer_1,answer_2)

            total_question_marks += int(answers_db[question_index].question_marks)

            student_marks = (int(percentage_correct) / 100) * int(answers_db[question_index].question_marks)

            print("Question index - ",question_index, "Student Marks - ", student_marks, "/",answers_db[question_index].question_marks  )
            # Store marks for the current question in the dictionary with 'qX' as key
           

            student_marks = round(student_marks)

              # Store both student marks and total question marks in the dictionary
            student_marks_details[f'Q{question_index + 1}'] = {
                'student_marks': student_marks,
                'total_marks': int(answers_db[question_index].question_marks)
            }

            marks_scored += student_marks

            # print("compare - ",answer_1," with - ", answer_2," marks scored - ",marks_scored," percetnage correct - ", percentage_correct)
            question_index += 1
        print("total makrs scored - ",marks_scored)

        print("======================================")



        # Insert data into the database
        student = Student(roll=roll_number, marks=marks_scored,total_marks=total_question_marks,test_id=test_id,marks_details=student_marks_details)
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
        
    
        chart_path = url_for('static', filename='images/chart.png')
        #  Close all open figures
        plt.close('all')
        print('test id = ',test_id)
        test_record = ClassesTests.query.get(test_id)
        
     
        # Render the HTML template with the uploaded image file, textarea, and pie chart
        return render_template('result.html',test_id=test_record,image_path=uploaded_files, student_marks=marks_scored, chart_path=chart_path,total_marks=total_question_marks,student_percentage=percentage_student,roll_number=roll_number,student=student)
   
        

    return render_template('generate_result.html',test_id=test_id)

def extract_prn_number(input_string):
    # Define the regex pattern to match exactly 12-digit PRN numbers (starting with 2021) with optional spaces between digits
    pattern = r'2021\s*(\d\s*\d\s*\d\s*\d)\s*(\d\s*\d\s*\d\s*\d)'
    
    # Search for the PRN number in the input string
    match = re.search(pattern, input_string)

    if match:
        # Remove all spaces from the matched groups and return the full PRN number
        prn_number = '2021' + match.group(1).replace(' ', '') + match.group(2).replace(' ', '')
        return prn_number
    else:
        return None  # Return None if no match is found


# Define a route to handle form submission
@app.route("/submit_questionpaper/<int:test_id>",methods=['GET', 'POST'])
def submit_questionpaper(test_id):
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
            student = QuestionAnswers(question=inputs[i], answer=textareas[i],question_marks=marks[i],classtest_id=test_id)
            db.session.add(student)
            db.session.commit()
        return redirect(url_for('submit_questionpaper',test_id=test_id))
    questions = QuestionAnswers.query.filter_by(classtest_id=test_id).all()
        
    return render_template("addQuestions.html",questions=questions,test_id=test_id)
    
@app.route('/delete_question/<int:test_id>/<int:question_id>', methods=['POST'])
def delete_question(test_id,question_id):
    # Find the class by ID
    question_to_delete = QuestionAnswers.query.get(question_id)
    if question_to_delete:
        db.session.delete(question_to_delete)
        db.session.commit()
        flash('Question deleted successfully!', 'success')
    else:
        flash('Question not found!', 'danger')
    
    return redirect(url_for('submit_questionpaper',test_id=test_id))  # Redirect back to the create class page

@app.route('/result/<int:test_id>/<int:student_id>')
def result_route():
    # Retrieve the data from query parameters
    uploaded_files = request.args.get('image_path')
    marks_scored = request.args.get('student_marks')
    total_question_marks = request.args.get('total_marks')
    percentage_student = request.args.get('student_percentage')
    roll_number = request.args.get('roll_number')
    chart_path = request.args.get('chart_path')  # Get the chart path directly

    # Render the HTML template with the retrieved variables
    return render_template('result.html', 
                           image_path=uploaded_files, 
                           student_marks=marks_scored, 
                           chart_path=chart_path, 
                           total_marks=total_question_marks, 
                           student_percentage=percentage_student, 
                           roll_number=roll_number)

@app.route('/allresults/<int:test_id>')
def download_results(test_id):
    # Assuming there's a relationship in the Student model that references the test.
    students = Student.query.filter(Student.test_id == test_id).all()
    test_record = ClassesTests.query.get(test_id)

    return render_template("allresults.html",students=students,test_record=test_record)

if __name__ == '__main__':
    # Create the images directory if it doesn't exist
    image_dir = 'static/images'
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
