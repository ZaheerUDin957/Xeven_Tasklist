with open('textfile.txt', 'r') as text:
    contant = text.read()
frequency = {}

for char in contant:
    frequency[char] = frequency.get(char, 0) + 1
print(frequency)