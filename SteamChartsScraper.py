import time
from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup


# Preserving your dependent connection wrapper placeholder
def connection_check(wait=False):
    return True


def scrape_steam_charts_launch_metrics(app_id="730", attempts=3, timeout=1, log_path="scraper_log.txt"):
    """
    Scrapes a specific AppID from steamcharts.com, extracts the player history table,
    and returns the calculated average and peak player metrics for the launch window (last 3 rows).
    """
    steam_charts_url = f"https://steamcharts.com/app/{app_id}"
    success = False
    steam_charts_tables = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    for j in range(attempts):
        try:
            response = requests.get(steam_charts_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            tables = soup.find_all("table")

            steam_charts_tables = [pd.read_html(str(t))[0] for t in tables]
            success = True

        except Exception as cond:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_msg = f"{app_id} {timestamp} Error - steam charts: {str(cond)}\n"
            with open(log_path, "a") as log_file:
                log_file.write(log_msg)

        if success and len(steam_charts_tables) > 0:
            break

        if connection_check():
            time.sleep(timeout)
        else:
            connection_check(wait=True)

    if not success or len(steam_charts_tables) == 0:
        raise RuntimeError(f"Failed to load data from steamcharts.com for AppID: {app_id}")

    # Grab the largest table based on row length
    steam_charts_data = max(steam_charts_tables, key=len)

    # Extract last 3 rows (chronological launch rows on SteamCharts)
    last_three_row = steam_charts_data.tail(3)

    # Calculate means rounded to 2 decimal points
    launch_avarage_players = float(round(last_three_row['Avg. Players'].mean(), 2))
    launch_peak_players = float(round(last_three_row['Peak Players'].mean(), 2))

    # Returns the calculated metrics along with the prepared dataframe slice
    return launch_avarage_players, launch_peak_players