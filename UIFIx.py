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
    # Create a pie chart
    labels = ['Correct', 'Incorrect']
    sizes = [83, 17]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    plt.savefig('piechart.png')
    # Display the results in the output text area
    output_text.delete('1.0', tk.END)
    output_text.insert(tk.END, f'Image Path: {image_path}\n')
    output_text.insert(tk.END, f'Standard Answer: {standard_answer}\n')
    output_text.insert(tk.END, 'Accuracy: 83% (Correct)\n')
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





