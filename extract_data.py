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
game_play = []
for line_item in f1:
    if line_item[:2] == "id":
        if len(game_play) > 0:
            games.append(game_play.copy())
        game_play.clear()
        game_play.append(line_item)
    else:
        game_play.append(line_item)

print(games[0])
print(games[10])
print(games[79])