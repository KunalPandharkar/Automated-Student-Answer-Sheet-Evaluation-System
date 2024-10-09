import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.metrics import jaccard_score

# Download NLTK data if not already downloaded
nltk.download('punkt')
nltk.download('stopwords')

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

# Example usage
answer_1 = " dbms is known a database management system"
answer_2 = "dbms is known as the database management system"

percentage_correct = compare_answers(answer_1, answer_2)
print(f'Percentage Correct: {percentage_correct}%')
