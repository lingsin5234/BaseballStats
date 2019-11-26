# extracting the data

# libraries
import numpy as np
import pandas as pd
import re

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
df1.insert(12, '1B_before', None)
df1.insert(13, '2B_before', None)
df1.insert(14, '3B_before', None)
df1.insert(15, '1B_after', None)
df1.insert(16, '2B_after', None)
df1.insert(17, '3B_after', None)
df1.insert(18, 'runs_scored', 0)
df1.insert(19, 'total_runs', 0)

# insert half innings
df1.insert(3, 'half_innings', None)
df1.half_innings = df1.inning + '_' + df1.half


# batch play processor
def play_processor(the_play):

    # determine if out(s)
    out_plays = tuple(''.join(map(str, list(range(1, 10))))) + ('K',)

    # determine hits/walks
    b1_plays = tuple(''.join('SW'))
    b2_plays = tuple('D')
    b3_plays = tuple('T')
    hr_plays = tuple('H')

    # put out(s)
    if the_play['play'].startswith(out_plays):
        if the_play['play'].endswith('DP'):
            the_play.at['outs'] += 2
        elif the_play['play'].endswith('TP'):
            the_play.at['outs'] += 3
        else:
            the_play.at['outs'] += 1

    # process batter ONLY
    if the_play['play'].startswith(b1_plays):
        the_play.at['1B_after'] = the_play['playerID']
    elif the_play['play'].startswith(b2_plays):
        the_play.at['2B_after'] = the_play['playerID']
    elif the_play['play'].startswith(b3_plays):
        the_play.at['3B_after'] = the_play['playerID']
    # process HR runs_scored ONLY
    elif the_play['play'].startswith(hr_plays):
        the_play.at['runs_scored'] += 1

    # return
    return the_play


# process the baserunners
def baserunner_processor(the_df):
    # get all half innings in the game
    all_half = the_df.half_innings.unique()
    full_df = pd.DataFrame()

    # process by half innings at a time
    for half in all_half:
        # each half inning
        half_df = the_df[the_df.half_innings == half]
        prev_row = half_df.loc[0]
        print("x: ", half)
        for i, d in half_df.iterrows():

            # carry-over runners from previous line
            if i > 0:
                print("i: ", i)
                if prev_row['1B_after'] is not None:
                    half_df.at[i, '1B_before'] = prev_row['1B_after']
                if prev_row['2B_after'] is not None:
                    half_df.at[i, '2B_before'] = prev_row['1B_after']
                if prev_row['3B_after'] is not None:
                    half_df.at[i, '3B_before'] = prev_row['1B_after']

            # move the runners
            if d['play'] is not None:
                if re.search(r"\.", d['play']):
                    print(d['play'])

            # save as previous row
            prev_row = half_df.loc[i]

        # append half inning to full game
        # print(half_df, '\nNext\n')
        full_df = full_df.append(half_df)
    return full_df


# function to process all half innings in a game
def half_inning_process(the_df):
    # get all half innings in the game
    all_half = the_df.half_innings.unique()
    full_df = pd.DataFrame()

    # process by half innings at a time
    for half in all_half:
        # print(half)
        total_outs = 0
        half_df = the_df[the_df.half_innings == half]
        for i, d in half_df.iterrows():

            # process outs
            if d['outs'] == 1:
                total_outs += 1
                half_df.at[i, 'outs'] = total_outs

            # process DP and TP
            elif d['outs'] == 2:
                total_outs += 2
                half_df.at[i, 'outs'] = total_outs

            elif d['outs'] == 3:
                total_outs += 3
                half_df.at[i, 'outs'] = total_outs

        # append half inning to full game
        # print(half_df, '\nNext\n')
        full_df = full_df.append(half_df)
    return full_df


# run the functions
for i, d in df1.iterrows():
    # print(type(d))
    if d['type'] == 'play':
        d = play_processor(d)
        df1.loc[i] = d
df1 = baserunner_processor(df1)
output_df = half_inning_process(df1)

# print(df1[df1.type == 'sub'])
# print(df1[df1.inning == '1'])

# print(output_df)
# print(df1)

# write to file
output_df.to_csv('OUTPUT.csv', sep=',', index=False)

