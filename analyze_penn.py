import sys, math, random, threading, time, functools, pandas as pd
import urllib.request, json

remaining_ratio = float(input("Let's predict that Biden will get the remaining votes in Pennsylvania at a percentage equal to the percent of people registered as democrat in each county.\n"
                              "All remaining ballots in Pennsylvania are mail-in ballots, which sway even heavier toward democrats.\n"
                              "We can expect Biden to outperform the democrat voter registration percent because the votes are all mail-in.\n\n"
                              "What ratio of other votes will Biden get? Input the ratio as a decimal.\n\n"
                              "As an example with input of \".1\", if County A has 60% of registered voters as democrats, then 40% of registered voters are not democrats.\n"
                              "I'm assuming that 60% of votes will go to Biden due to 60% of voters registered as democrats.\n"
                              "I want to take a portion of that other 40% and give it to Biden, to adjust for the mail-in sway that goes to democrats.\n"
                              "Designate a ratio of that remaining 40% to go to Biden. If you give input of \".1\", that means that 1/10 of the other 40% of votes will go to Biden.\n"
                              "So Biden would get the 60% from democrat voter registration, plus 4% from the other pool of votes, accounting for mail-in sway.\n"))

def series_strtoa(series):
    return pd.Series([float(x) for x in series])


with urllib.request.urlopen("https://data.pa.gov/resource/4xnz-vz4w.json") as url:
    registration_data = pd.DataFrame(json.loads(url.read().decode()))

with urllib.request.urlopen("https://data.pa.gov/resource/pg3c-9a9m.json") as url:
    ballot_data = pd.DataFrame(json.loads(url.read().decode()))

for col in registration_data.columns.drop("county"):
    registration_data[col] = series_strtoa(registration_data[col])

for col in ballot_data.columns.drop("county"):
    ballot_data[col] = series_strtoa(ballot_data[col])

full_data = pd.merge(registration_data, ballot_data, on="county")

# votes remaining for Biden
remaining_sum = 0
total_ballots_remaining = 0
total_ballots_counted = 0

for i, county_data in full_data.iterrows():
    dem_voters = county_data["democratic_voters"]
    repub_voters = county_data["republican_voters"]
    tot_voters = county_data["total_voters"]
    dem_percent = dem_voters / tot_voters
    repub_percent = repub_voters / tot_voters

    other_percent = (1 - dem_percent) * remaining_ratio
    # add other percent to dem percent and subtract it from repub percent
    dem_percent += other_percent
    repub_percent -= other_percent

    biden_lead_projected = dem_percent - repub_percent


    projected_votes = county_data["ballots_remaining"] * biden_lead_projected
    print(county_data["county"], county_data["ballots_remaining"], " ballots remaining with a ", biden_lead_projected * 100, " percent lead. Projected votes: ", projected_votes)

    remaining_sum += projected_votes

    print("Biden lead total: ", remaining_sum)
    print()

remaining_ballots = full_data["ballots_remaining"].sum()
print("total Pennsylvania remaining ballots: ", remaining_ballots)
print("with our assumptions and your inputted ratio, biden would get ", (remaining_ballots + remaining_sum) * 100 / (2 * remaining_ballots), "percent of remaining votes in this case.")