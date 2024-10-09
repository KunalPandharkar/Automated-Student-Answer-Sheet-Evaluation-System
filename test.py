# import string
# import nltk
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
# from sklearn.metrics import jaccard_score

# # Download NLTK data if not already downloaded
# nltk.download('punkt')
# nltk.download('stopwords')

# # Preprocess the text by removing punctuation and converting to lowercase
# def preprocess(text):
#     translator = str.maketrans('', '', string.punctuation)
#     return text.translate(translator).lower()

# # Remove stopwords
# def remove_stopwords(tokens):
#     stop_words = set(stopwords.words('english'))
#     return [word for word in tokens if word not in stop_words]

# # Calculate Jaccard similarity
# def jaccard_similarity(set1, set2):
#     intersection = len(set1.intersection(set2))
#     union = len(set1.union(set2))
#     return intersection / union if union != 0 else 0

# # Main comparison function
# def compare_answers(answer_1, answer_2):
#     # Preprocess the answers
#     answer_1 = preprocess(answer_1)
#     answer_2 = preprocess(answer_2)

#     # Tokenize the answers and remove stopwords
#     tokens_1 = remove_stopwords(word_tokenize(answer_1))
#     tokens_2 = remove_stopwords(word_tokenize(answer_2))

#     # Calculate Jaccard similarity
#     set1 = set(tokens_1)
#     set2 = set(tokens_2)
#     similarity = jaccard_similarity(set1, set2)

#     # Generate the percentage of correctness
#     percentage_correct = similarity * 100
#     return round(percentage_correct)

# # Example usage
# answer_1 = " dbms is known a database management system"
# answer_2 = "dbms is known as the database management system"

# percentage_correct = compare_answers(answer_1, answer_2)
# print(f'Percentage Correct: {percentage_correct}%')


import re

def extract_prn_number(input_string):
    # Define the regex pattern to match the PRN number
    # The pattern matches a number starting with 2021 followed by any 11 digits
    pattern = r'\b2021[\s]*(\d{5})[\s]*(\d{4})|202\s*\d{3}\s*\d{4}\b'
    
    # Search for the PRN number in the input string
    match = re.search(pattern, input_string)

    if match:
        if match.group(1) and match.group(2):
            # Concatenate the captured groups and remove spaces
            prn_number = f"2021{match.group(1)}{match.group(2)}"
        else:
            # For the alternative matching case (202XXXYYYY)
            prn_number = match.group(0).replace(' ', '')
        return prn_number
    else:
        return None  # Return None if no match is found

# Test cases
test_cases = [
    "The student with PRN number 2021 01103 0003qererdafd has successfully completed the exam.",
    "Student ID is 2021011030003, well done!",
    "Invalid ID: 202 101 103 0003",
    "Congratulations 2021 01103 0003!",
    "2021011030003 is your PRN number."
]

# Running test cases
for test in test_cases:
    prn_number = extract_prn_number(test)
    if prn_number:
        print(f"Input: \"{test}\" -> Extracted PRN Number: {prn_number}")
    else:
        print(f"Input: \"{test}\" -> No PRN number found.")
