# this script runs the batting stats thru calculations to produce
# the calculated stats, e.g. BAA
import pandas as pd


def calculate_bat_stats(batting):

    # calculate sums
    df_sum = batting.agg(['sum'])

    # calculations
    batting_avg = hits / batting['at_bats']
    on_base_per = (hits + walks + hbp) / (at_bats + walks + hbp + sac_flies)
    total_outs = (at_bats - hits) + gdp + sac_flies + sac_hits + caught_stealing
    singles = hits - doubles - triples - home_runs
    total_bases = singles + doubles x 2 + triples x 3 + home_runs x 4
    slugging = total_bases / at_bats
    obp_slug = on_base_per + slugging
    obp_slug_plus = 100 * ( (on_base_per / league_on_base_per) + ( slugging / league_slugging ) - 1)
    batting_avg_bip = ( hits - home_runs ) / ( at_bats - strikeouts - home_runs + sac_flies )
    on_base = hits + walks + hbp - caught_stealing - gdp
    bases_adv = total_bases + .26 (walks + hbp - ibb) + .52 (sac_hits + sac_flies + stolen_bases)
    opportunities = at_bats + walks + hbp + sac_hits + sac_flies
    runs_created = on_base * bases_adv / opportunities
    runs_created_per = runs_created / ( total_outs / 27 )

    return True
