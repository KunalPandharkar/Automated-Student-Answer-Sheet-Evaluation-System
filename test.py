import re

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
        return None  # Return None if no match is found

# Test cases
test_cases = [
    "The student with PRN number 2021 0113 0003 has successfully completed the exam.",
    "Student ID is 2021 0113 0003, well done!",
    "Congratulations 2021 01103 000!",
    "2021 0110 3003 is your PRN number.",
    "PRN 20210 110               3005Name - Avani PathakQ1)Datascience is a branchof computer science.",
    "PRN 2021 0110 2003",
    "PRN2021 01103 000!"
]

# Test the function with the test cases
for test in test_cases:
    print(f"Input: {test}")
    print(f"Extracted PRN: {extract_prn_number(test)}\n")
