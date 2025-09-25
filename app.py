from fastapi import FastAPI, Query
from typing import List
import uvicorn

# import your scraping functions
from bs4 import BeautifulSoup
import requests

app = FastAPI(title="FPL Scraper API")

# ====== Your scraping logic ======
def scrape_fpl_table(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    rows = soup.find_all('details', class_='row')
    players_data = []

    for row in rows:
        try:
            team_name_elem = row.find('div', class_='team-name')
            team_name = team_name_elem.text.strip() if team_name_elem else ""

            manager_elem = row.find('div', class_='manager')
            manager_name = manager_elem.text.strip() if manager_elem else ""

            name = f"{team_name}({manager_name})" if team_name and manager_name else team_name or manager_name

            or_elem = row.find('span', class_='kpi')
            overall_ranking = or_elem.text.replace('OR', '').strip() if (or_elem and 'OR' in or_elem.text) else ""

            yet_to_play = row.get('data-played_rem', '0')
            captain_elem = row.find('div', class_='captain')
            captain = captain_elem.text.strip() if captain_elem else ""
            gameweek_points = row.get('data-gw', '0')
            total_points = row.get('data-total', '0')

            player_data = {
                'name': name,
                'overall_ranking': overall_ranking,
                'yet_to_play': yet_to_play,
                'captain': captain,
                'gameweek_points': gameweek_points,
                'total_points': total_points
            }
            players_data.append(player_data)
        except Exception:
            continue
    return players_data


def fetch_fpl_data(url: str, full_table: bool = True):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        players_data = scrape_fpl_table(response.text)
        return players_data if full_table else players_data[:10]
    except Exception as e:
        return {"error": str(e)}

# ====== FastAPI endpoints ======
@app.get("/league")
def get_league(
    full_table: bool = Query(True, description="True = full table, False = top 10")
):
    url = "https://plan.livefpl.net/leagues/2099876"  # hard-coded league URL
    data = fetch_fpl_data(url, full_table=full_table)
    return {"count": len(data) if isinstance(data, list) else 0, "results": data}


# Run locally (useful for testing)
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
