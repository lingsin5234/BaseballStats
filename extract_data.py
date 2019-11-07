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
i = -1
j = 0
game_play = []
while i < 10:
    if f1[i][:2] == 'id':
        j += 1
        game_play.append(f1[i][3:])
    
    i += 1


print(game_play[0])