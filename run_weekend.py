from dotenv import load_dotenv
load_dotenv()

import argparse
import os
import json
from datetime import date
from downloader import get_car_submission_pdf
from processor import parse_fia_car_presentation
from summarizer import generate_summaries
import fastf1

from rapidfuzz import process, fuzz

# Known FIA website URL naming quirks that fuzzy matching might struggle with
FIA_GP_NAME_MAP = {
    "são paulo grand prix": "sao_paulo_grand_prix",
    "brazilian grand prix": "sao_paulo_grand_prix",
    "emilia romagna grand prix": "emilia_romagna_grand_prix",
    "imola grand prix": "emilia_romagna_grand_prix",
    "mexico city grand prix": "mexico_grand_prix",
    "mexican grand prix": "mexico_grand_prix",
    "united states grand prix": "us_grand_prix",
    "abu dhabi grand prix": "abu_dhabi_grand_prix",
    "barcelona grand prix": "barcelona-catalunya_grand_prix"
}

# Standard list of FIA grand prix URL slugs
FIA_STANDARD_SLUGS = [
    "bahrain_grand_prix",
    "saudi_arabian_grand_prix",
    "australian_grand_prix",
    "japanese_grand_prix",
    "chinese_grand_prix",
    "miami_grand_prix",
    "emilia_romagna_grand_prix",
    "monaco_grand_prix",
    "canadian_grand_prix",
    "spanish_grand_prix",
    "austrian_grand_prix",
    "british_grand_prix",
    "hungarian_grand_prix",
    "belgian_grand_prix",
    "dutch_grand_prix",
    "italian_grand_prix",
    "azerbaijan_grand_prix",
    "singapore_grand_prix",
    "us_grand_prix",
    "mexico_grand_prix",
    "sao_paulo_grand_prix",
    "las_vegas_grand_prix",
    "qatar_grand_prix",
    "abu_dhabi_grand_prix",
    "barcelona_catalunya_grand_prix"
]

def format_gp_name(fastf1_event_name: str) -> str:
    cleaned = fastf1_event_name.lower().strip()
    
    slug_guess = cleaned.replace(" ", "_")

    if cleaned in FIA_GP_NAME_MAP:
        return FIA_GP_NAME_MAP[cleaned]
    
    match, score, _ = process.extractOne(
        slug_guess, 
        FIA_STANDARD_SLUGS, 
        scorer=fuzz.WRatio
    )
    
    # If the match quality is above 80%, trust the fuzzy match
    print('Score is ',score)
    if score >= 80:
        return match
        
    # Fallback to the raw formatted string
    return slug_guess  

def get_current_event():
    year = date.today().year
    schedule = fastf1.get_event_schedule(year)

    today = date.today()
    for _, event in schedule.iterrows():
        weekend_start = event['Session1Date'].date()
        weekend_end = event['EventDate'].date()
        if weekend_start <= today <= weekend_end:
            return year, event['RoundNumber'], event['EventName']

    return None, None, None


def process_race_weekend(year: int, gp_name: str):
    pdf_path = get_car_submission_pdf(year, gp_name)              # downloader.py

    df = parse_fia_car_presentation(pdf_path)             # processor.py
    race_slug = f"{year}_{gp_name}"
    os.makedirs(f"data/{race_slug}", exist_ok=True)
    df.to_csv(f"data/{race_slug}/fia_updates.csv", index=False)

    os.remove(pdf_path) 

    summaries = generate_summaries(df)                    # summarizer.py
    with open(f"data/{race_slug}/team_summaries.json", "w") as f:
        json.dump(summaries, f, indent=2)

    return race_slug

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch, process and summarize F1 component updates in a GP weekend.")
    parser.add_argument("--year", type=int, help="Season year (e.g., 2024)")
    parser.add_argument("--round", type=int, help="Round number (e.g., 8)")

    args = parser.parse_args()

    if args.year and args.round:
        year = args.year
        round_num = args.round
        event_name = fastf1.get_event(args.year, args.round)['EventName']
    elif args.year or args.round:
        print("Error: Please provide both --year and --round arguments together.")
        exit(1)
    else:
        year, round_num, event_name = get_current_event()

    if not event_name:
        print("No race found for the specified parameters or current weekend, skipping.")
        exit()

    gp_name = format_gp_name(event_name)
    print(f"Processing Round {round_num}: {gp_name} ({year})...")
    # gp_name = event_name.lower().replace(" grand prix", "").replace(" ", "_") + "_grand_prix"
    process_race_weekend(year, gp_name)