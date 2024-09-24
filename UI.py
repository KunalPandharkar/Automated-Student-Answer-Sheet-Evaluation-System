def character_at(input1, input2):
    decrypted = ""
    i = 0

    while i < len(input1):
        char = input1[i]
        frequency = int(input1[i+1])

        decrypted += char * frequency
        i += 2

    if n <= len(decrypted):
        return decrypted[input2-1]
    else:
        return -1

# Example usage
input1 = "a1b1c3"
n = 5
result = character_at(input1, n)
print(f"The {n}th character in the decrypted string is: {result}")
