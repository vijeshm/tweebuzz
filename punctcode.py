import re
import string

f = open("Punctuation.txt", "r")
l = f.read()
LSet = []
for letter in l:
	LSet.append(letter)

LSet = list(set(LSet))
LSet.remove(' ')
LSet.remove('\n')
LSet.remove('@')
LSet.remove('#')

alpha = [letter for letter in string.letters]
for char in alpha:
	if char in LSet:
		LSet.remove(char)

print LSet