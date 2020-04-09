Baseball Stats Website
=================

The purpose of this project is to handle baseball stats from its raw event file format and convert
it into a usable format. One of my personal goals for this project is to understand and develop
an ETL process for handling this data. This process includes:

*  extracting the file from the [Retrosheet](https://www.retrosheet.org) website
*  transforming its contents into raw player statistics
*  loading the statistics into a database
*  generating readable player statistics
*  displaying the statistics onto the website

My GitLab repo is: [Baseball Stats](https://gitlab.com/lingsin5234/MLB-Stats-Website)

## Layout
There are two main pages for this website: **Run Jobs** and **View Stats**.

**Jobs Dashboard** page allows users to view the latest ETL processes performed in the backend.
Users can see jobs that *Import* a particular year of baseball event files, *Process* of data for
a particular team in a specific year, and *Generate* the readable player statistics.

**View Stats** page allows users to view player statistics by selecting a specific year and team.
Using this as a base, more enhancements will be done to allow further analysis in the future.

## Transform Process
The transforming process is the most intriguing of this project. All lines of an event file are
sorted by games, as each game has its own game id - for example, The below ID indicates an
Atlanta home game on April 8, 1983:

    id,ATL198304080

Each play-by-play line is assigned the corresponding game id for tracking of games, along with
baserunners, how many outs so far, how many outs record in a particular play, how many runs scored
in a particular play, which pitcher was pitching, etc. Then the process goes through each play-by-play
line is then further sorted in the following format:

*  substitution
*  play
    *  plate-appearance play
    *  non-plate-appearance play

Substitutions will handle any fielding or pitching changes, pinch hitters and pinch runners. The plays
are sorted into two main categories, a plate-appearance play and a non-plate appearance play. Plate-
appearance plays are plays that count towards the batter's plate appearance, for example:

*  any hit
*  strikeout
*  walk / intentional walk
*  hit by pitch

Non-plate appearance plays are plays that do not count towards the batter's plate appearance, for
example:

*  stolen base
*  caught stealing
*  defensive indifference
*  no pitch - which is often used prior to a substitution line
*  wild pitch
*  balk

After each type of play is processed respectively, any baserunner movement is then accounted for.
Furthermore, all raw player statistics are recorded whilst any play-by-play line is be parsed.

At this time, only batter, runner and pitching statistics are recorded, fielding statistics will be
added in the future.

## Sources
The main source is the aforementioned [Retrosheet](https://www.retrosheet.org) website.
This website contains event files that are in a play-by-play recording format that indicates,
in a very short form format, what specifically happened in any particular play.

All event files follow the format listed on the [Retrosheet: Event File](https://www.retrosheet.org/eventfile.htm)
webpage. For example:

    play,5,1,ramir001,00,,S8.3-H;1-2

This indicates that a play within a particular game, during the 5th inning with the away team batting,
ramir001 - the batter, hit a single to center field on a 0-0 count. This play scored the runner from 3rd
and moved the runner from 1st to 2nd.
