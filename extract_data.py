# extracting the data

# libraries


# open and read data
f = open("retrodata/2010TOR.EVA","r")
f1 = f.readlines()

# test print
# for i in range(100):
#    print(f1[i])

# test print first two characters, and everything after comma
# print(f1[0][:2])
# print(f1[0][3:])

# collect id and group the games
games = []
id = 0
i = -1
j = 0
while i < len(f1):
    print(f1[i])
    if f1[i][:2] == 'id':
        ++j
        games[j] = f1[i][3:]
    else:
        print(j)

    ++i

print(games[0])