import os,io
from google.cloud import vision_v1
import string
import nltk
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import matplotlib.pyplot as plt



# Function to get the image path using a file dialog
def get_image_path():
    path = filedialog.askopenfilename()
    image_path_entry.delete(0, tk.END)
    image_path_entry.insert(0, path)

# Function to submit the form and display the pie chart
def submit_form():
    image_path = image_path_entry.get()
    standard_answer = standard_answer_entry.get('1.0', tk.END)
    # Do some processing with the image and standard answer here
    # ...

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'Google_Key.json'
    client = vision_v1.ImageAnnotatorClient()

    FILE_NAME = 'Text.jpg'
    FOLDER_PATH = r'D:\FInal_Project\Subjective_Analysis\Images'

    with io.open(os.path.join(image_path),'rb') as image_file:
        content = image_file.read()

    image = vision_v1.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    # Concatenate only the first item in the texts list
    all_text = texts[0].description if len(texts) > 0 else ''

    all_text = all_text.replace('\n', ' ')

    print(all_text)
    # Define two sample answers
    answer_1 = str(all_text)
    answer_2 = standard_answer

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
    
    # Create a pie chart
    labels = ['Correct', 'Incorrect']
    sizes = [percentage_correct, 100-percentage_correct]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.savefig('piechart.png')
    # Display the results in the output text area
    output_text.delete('1.0', tk.END)
    # output_text.insert(tk.END, f'Image Path: {image_path}\n')
    # output_text.insert(tk.END, f'Standard Answer: {standard_answer}\n')
    output_text.insert(tk.END, f'Accuracy: {percentage_correct}% (Correct)\n')
    # Display the pie chart image
    image = Image.open('piechart.png')
    photo = ImageTk.PhotoImage(image)
    piechart_label.configure(image=photo)
    piechart_label.image = photo

# Create the tkinter window
root = tk.Tk()
root.title('Image Analysis')

# Set the color theme
root.configure(bg='#F0F0F0')  # Set a light gray background color

# Create a frame for input section
input_frame = tk.Frame(root, bg=root['bg'])
input_frame.grid(row=0, column=0, padx=20, pady=20, sticky='n')

# Create a frame for output section
output_frame = tk.Frame(root, bg=root['bg'])
output_frame.grid(row=0, column=1, padx=20, pady=20, sticky='n')

# Create the widgets with a unified color theme
label_color = '#333333'  # Dark gray color for labels
entry_bg = '#FFFFFF'  # White background color for entry fields
text_bg = '#FFFFFF'  # White background color for text areas
button_bg = '#4CAF50'  # Green background color for buttons
button_fg = '#FFFFFF'  # White foreground color for buttons

# Input Screen
input_label = tk.Label(input_frame, text='Input Screen', bg=root['bg'], fg=label_color, font=('Arial', 18, 'bold'))
input_label.pack(side='top', pady=(0, 20))

image_path_label = tk.Label(input_frame, text='Image Path:', bg=input_frame['bg'], fg=label_color, font=('Arial', 14))
image_path_entry = tk.Entry(input_frame, width=50, bg=entry_bg, font=('Arial', 12))
browse_button = tk.Button(input_frame, text='Browse', command=get_image_path, bg=button_bg, fg=button_fg, font=('Arial', 12))
standard_answer_label = tk.Label(input_frame, text='Standard Answer:', bg=input_frame['bg'], fg=label_color, font=('Arial', 14))
standard_answer_entry = tk.Text(input_frame, height=10, width=50, bg=text_bg, font=('Arial', 12))
submit_button = tk.Button(input_frame, text='Submit', command=submit_form, bg=button_bg, fg=button_fg, font=('Arial', 14))

image_path_label.pack(side='top', anchor='w')
image_path_entry.pack(side='top', padx=10, pady=10)
browse_button.pack(side='top', pady=(0, 10))
standard_answer_label.pack(side='top', anchor='w')
standard_answer_entry.pack(side='top', padx=10, pady=10)
submit_button.pack(side='top', pady=(20, 0))

# Output Screen
output_label = tk.Label(output_frame, text='Output Screen', bg=root['bg'], fg=label_color, font=('Arial', 18, 'bold'))
output_label.pack(side='top', pady=(0, 20))

output_text = tk.Text(output_frame, height=15, width=50, bg=text_bg, font=('Arial', 12))
output_text.pack(side='top', padx=10, pady=10)

piechart_label = tk.Label(output_frame, bg=text_bg)
piechart_label.pack(side='top', pady=10)

# Set the size of the window
root.geometry('1200x800')

# Run the tkinter event loop
root.mainloop()





