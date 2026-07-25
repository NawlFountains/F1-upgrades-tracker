import pandas as pd
import os
from groq import Groq

client = Groq()

 
def summarize_team_updates(team: str, team_rows: list[dict]) -> str:
    # teams with no updates get a fixed string, no LLM call needed
    if len(team_rows) == 1 and team_rows[0]["component"] == "None":
        return f"{team} did not submit any updates for this event."
 
    updates_text = "\n".join(
        f"- {row['component']}: {row['reason']} — {row['differences']}"
        for row in team_rows
    )
 
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""Summarize these car updates for {team} in 2-3 sentences,
        written for F1 fans (not engineers). Focus on what's changed and why it matters
        for this race weekend, not technical jargon.
        
        Updates:
        {updates_text}"""
            }
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content
 
def generate_summaries(df: pd.DataFrame) -> dict:
    """
    Given the parsed updates DataFrame for a race weekend (all teams),
    return {team_name: summary_string} for every team present.
    """
    summaries = {}
    for team in df["team"].unique():
        team_rows = df[df["team"] == team].to_dict("records")
        summaries[team] = summarize_team_updates(team, team_rows)
    return summaries
 