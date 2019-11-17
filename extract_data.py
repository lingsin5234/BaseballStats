# extracting the data

# libraries
import numpy as np
import pandas as pd

# open and read data
f = open("retrodata/2015TOR.EVA","r")
f1 = f.readlines()

# test print
# for i in range(100):
#    print(f1[i])

# test print first two characters, and everything after comma
# print(f1[0][:2])
# print(f1[0][3:])

# collect id and group the games
games = []
game_info = []
game_play = []
for line_item in f1:
    if line_item[:2] == "id":
        if len(game_info) > 0:
            game_info.append(game_play.copy())
            games.append(game_info.copy())
        game_info.clear()
        game_info.append(line_item)
    elif line_item[:4] == "play" or line_item[:3] == "sub":
        game_play.append(line_item)
    else:
        game_info.append(line_item)

# get last item in list, which is the entire game_play
# print(games[0][-1])

# loop through 1 game
# for line_item in games[0][-1]:
#    print(line_item)

# use pandas library to convert play-by-play to table
df = pd.DataFrame(games[0][-1])
df1 = pd.concat([df[0].str.split(',', expand=True)], axis=1)

# remove line break in last column
df1[6] = df1[6].str.replace('\n', '')

# add some column names with some extra ones too
df1.columns = ['type', 'inning', 'half', 'playerID', 'count', 'pitches', 'play']

# add newer columns
df1.insert(7, 'name', None)
df1.insert(8, 'team', None)
df1.insert(9, 'batting', None)
df1.insert(10, 'fielding', None)

# shift the substitutions into newer columns
df1.loc[df1.type == 'sub', 'name'] = df1.loc[df1.type == 'sub', 'half'].tolist()
df1.loc[df1.type == 'sub', 'team'] = df1.loc[df1.type == 'sub', 'playerID'].tolist()
df1.loc[df1.type == 'sub', 'batting'] = df1.loc[df1.type == 'sub', 'count'].tolist()
df1.loc[df1.type == 'sub', 'fielding'] = df1.loc[df1.type == 'sub', 'pitches'].tolist()

# correct the remaining columns
df1.loc[df1.type == 'sub', 'playerID'] = df1.loc[df1.type == 'sub', 'inning']
df1.loc[df1.type == 'sub', 'count'] = None
df1.loc[df1.type == 'sub', 'pitches'] = None

# using current index to retrieve and replace with -1 index with inning and half inning values
previous_index = df1[df1.type == 'sub'].index.values - 1
df1.loc[df1.type == 'sub', 'inning'] = df1.loc[previous_index, 'inning'].tolist()
df1.loc[df1.type == 'sub', 'half'] = df1.loc[previous_index, 'half'].tolist()

# remove line break in last column for subs
df1.loc[df1.type=='sub', 'fielding'] = df1.loc[df1.type=='sub', 'fielding'].str.replace('\n', '').tolist()

# add outs and baserunners columns
df1.insert(11, 'outs', 0)
df1.insert(12, '1B', None)
df1.insert(13, '2B', None)
df1.insert(14, '3B', None)

# determine outs
i = tuple(''.join(map(str, list(range(1, 10)))))
# cond1 = (df1.inning == '1')
# print(type(df1.loc[df1.inning == '1', 'play']))
# print('test\n')
# cond2 = df1.play.str.startswith('8', na=False)
# print(type(df1.loc[df1.play.str.startswith('8', na=False), 'play']))
# print('test2\n')
# print(cond1 & cond2)
print(i, '\n')
print(df1.loc[(df1.inning == '1') & df1.play.str.startswith(i, na=False), 'play'])
# print(df1.loc[df1.inning == '1' & df1.play[:1].tolist().isdigit(), 'play'])

# print(df1[df1.type == 'sub'])
# print(df1[df1.inning == '1'])

# print(df1)

