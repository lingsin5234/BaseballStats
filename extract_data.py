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


# re-write the processor based on re.search/re.findall grep searching
def play_processor2(the_df):

    # process would go line by line.
    for i, ln in the_df.iterrows():

        # for plays
        if ln['type'] == 'play':

            # Case 1: regular single out plays
            if re.search(r'^[1-9]([1-9]+)?/(G|F|L|P)', ln['play']):
                print('Routine Put Out: ', ln['play'])

            # Case 2: irregular put-outs, runner is specified
            elif re.search(r'^[1-9]([1-9]+)?\([B123]\)/BG', ln['play']):
                print('Irregular Put Out: ', ln['play'])

            # Case 3: explicit force out plays
            elif re.search(r'^[1-9]([1-9]+)?\([B123]\)/FO', ln['play']):
                print('Force Out: ', ln['play'])

            # Case 4: sacrifice hit / fly
            elif re.search(r'^[1-9]([1-9]+)?/(SH|SF)', ln['play']):
                print('Sac Hit/Fly: ', ln['play'])

            # Case 5: fielders' choice
            elif re.search(r'FC[1-9]', ln['play']):
                print('Fielders\' Choice: ', ln['play'])

            # Case 6: strike out
            elif re.search(r'^K([1-9]+)?', ln['play']):
                print('STRIKEOUT: ', ln['play'])

            # Case 7: strike out + event
            elif re.search(r'^K\+', ln['play']):
                print('Strikeout + Event: ', ln['play'])

            # Case 8: routine double plays
            elif re.search(r'.*DP', ln['play']):
                print('DOUBLE PLAY: ', ln['play'])

            # Case 9: triple plays
            elif re.search(r'.*TP', ln['play']):
                print('TRIPLE PLAY: ', ln['play'])

            # Case 10: catcher interference or pitcher/1B interference
            elif re.search(r'^C/E[1-9]', ln['play']):
                print('Catcher Int.: ', ln['play'])

            # Case 11: Hit!
            elif re.search(r'^((S|D|T)[1-9]|H/|HR|DGR)', ln['play']):
                print('A Hit!: ', ln['play'])

            # Case 12: Walk / HP
            elif re.search(r'^(HP|IW|W)(?!\+)', ln['play']):
                print('Walk / Hit By Pitch: ', ln['play'])

            # Case 13: Walk + event
            elif re.search(r'^(IW|W)\+', ln['play']):
                print('Walk + Event: ', ln['play'])

            # Case 14: fly ball error
            elif re.search(r'^FLE[1-9]', ln['play']):
                print('Fly ball Error: ', ln['play'])

            # Case 15: error
            elif re.search(r'^E[1-9]', ln['play']):
                print('Error: ', ln['play'])

            # Case 16: wild pitch or balk
            elif re.search(r'^(WP|BK)', ln['play']):
                print('Wild Pitch: ', ln['play'])

            # Case 17: no pitch
            elif re.search(r'^NP$', ln['play']):
                pass

            # Case 18: stolen base
            elif re.search(r'^SB', ln['play']):
                print('Stolen Base: ', ln['play'])

            # Case 19: caught stealing
            elif re.search(r'^CS', ln['play']):
                print('Caught Stealing: ', ln['play'])

            # Case 20: defensive indifference
            elif re.search(r'^DI', ln['play']):
                print('Defensive Indiff.: ', ln['play'])

            # Case 20: ELSE
            else:
                print('CASE NEEDED: ', ln['play'])

    return the_df


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
        # except WP - wild pitch
        if re.search(r'^WP|SB', the_play['play']):
            pass
        else:
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
        half_df = half_df.reset_index(drop=True)  # index needs to be reset to ref 0
        prev_row = half_df.loc[0]
        for i, d in half_df.iterrows():

            # carry-over runners from previous line
            if i > 0:
                if prev_row['1B_after'] is not None:
                    half_df.at[i, '1B_before'] = prev_row['1B_after']
                if prev_row['2B_after'] is not None:
                    half_df.at[i, '2B_before'] = prev_row['2B_after']
                if prev_row['3B_after'] is not None:
                    half_df.at[i, '3B_before'] = prev_row['3B_after']

            # move the runners
            if d['play'] is not None:
                if re.search(r'\.', d['play']):
                    if re.search(r'1-2', d['play']):
                        half_df.at[i, '2B_after'] = half_df.loc[i, '1B_before']
                    if re.search(r'1-3', d['play']):
                        half_df.at[i, '3B_after'] = half_df.loc[i, '1B_before']
                    if re.search(r'1-H', d['play']):
                        half_df.at[i, 'runs_scored'] += 1
                    if re.search(r'2-3', d['play']):
                        half_df.at[i, '3B_after'] = half_df.loc[i, '2B_before']
                    if re.search(r'2-H', d['play']):
                        half_df.at[i, 'runs_scored'] += 1
                    if re.search(r'3-H', d['play']):
                        half_df.at[i, 'runs_scored'] += 1

                    # check for non-moving runners that did not get out
                    if half_df.loc[i, '1B_before'] is not None and not re.search(r'1-|1X', d['play']):
                        half_df.at[i, '1B_after'] = half_df.loc[i, '1B_before']
                    if half_df.loc[i, '2B_before'] is not None and not re.search(r'2-|2X', d['play']):
                        half_df.at[i, '2B_after'] = half_df.loc[i, '2B_before']
                    if half_df.loc[i, '3B_before'] is not None and not re.search(r'3-|3X', d['play']):
                        half_df.at[i, '3B_after'] = half_df.loc[i, '3B_before']

                elif re.search(r'^SB', d['play']):

                    # stealing 2nd
                    if re.search(r'^SB2', d['play']):
                        half_df.at[i, '2B_after'] = half_df.loc[i, '1B_before']
                        if re.search(r'\.', d['play']):
                            if re.search(r'2-3', d['play']):
                                half_df.at[i, '3B_after'] = half_df.loc[i, '2B_before']
                            if re.search(r'2-H', d['play']):
                                half_df.at[i, 'runs_scored'] += 1
                            if re.search(r'3-H', d['play']):
                                half_df.at[i, 'runs_scored'] += 1
                        else:
                            if half_df.loc[i, '3B_before'] is not None:
                                half_df.at[i, '3B_after'] = half_df.loc[i, '3B_before']

                    # stealing 3rd
                    if re.search(r'^SB3', d['play']):
                        half_df.at[i, '3B_after'] = half_df.loc[i, '2B_before']
                        if re.search(r'\.', d['play']):
                            if re.search(r'3-H', d['play']):
                                half_df.at[i, 'runs_scored'] += 1
                            if re.search(r'1-2', d['play']):
                                half_df.at[i, '2B_after'] = half_df.loc[i, '1B_before']
                            if re.search(r'1-3', d['play']):
                                half_df.at[i, '3B_after'] = half_df.loc[i, '1B_before']
                            if re.search(r'1-H', d['play']):
                                half_df.at[i, 'runs_scored'] += 1
                        else:
                            if half_df.loc[i, '1B_before'] is not None:
                                half_df.at[i, '1B_after'] = half_df.loc[i, '1B_before']

                    # stealing home
                    if re.search(r'^SBH', d['play']):
                        half_df.at[i, 'runs_scored'] += 1
                        if re.search(r'\.', d['play']):
                            if re.search(r'1-2', d['play']):
                                half_df.at[i, '2B_after'] = half_df.loc[i, '1B_before']
                            if re.search(r'1-3', d['play']):
                                half_df.at[i, '3B_after'] = half_df.loc[i, '1B_before']
                            if re.search(r'1-H', d['play']):
                                half_df.at[i, 'runs_scored'] += 1
                            if re.search(r'2-3', d['play']):
                                half_df.at[i, '3B_after'] = half_df.loc[i, '2B_before']
                            if re.search(r'2-H', d['play']):
                                half_df.at[i, 'runs_scored'] += 1
                        else:
                            if half_df.loc[i, '1B_before'] is not None:
                                half_df.at[i, '1B_after'] = half_df.loc[i, '1B_before']
                            if half_df.loc[i, '2B_before'] is not None:
                                half_df.at[i, '2B_after'] = half_df.loc[i, '2B_before']

                else:
                    # if not 3 outs yet, and some runners did not move, find and keep them.
                    if i > 0 and half_df.loc[i, 'outs'] < 3:
                        if half_df.loc[i, '1B_before'] is not None:
                            half_df.at[i, '1B_after'] = half_df.loc[i, '1B_before']
                        if half_df.loc[i, '2B_before'] is not None:
                            half_df.at[i, '2B_after'] = half_df.loc[i, '2B_before']
                        if half_df.loc[i, '3B_before'] is not None:
                            half_df.at[i, '3B_after'] = half_df.loc[i, '3B_before']

            # for sub lines, copy all baserunners
            elif d['type'] == 'sub':
                half_df.at[i, '1B_after'] = half_df.loc[i, '1B_before']
                half_df.at[i, '2B_after'] = half_df.loc[i, '2B_before']
                half_df.at[i, '3B_after'] = half_df.loc[i, '3B_before']

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


# test the play_processor2 function
new_output = play_processor2(df1)

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
