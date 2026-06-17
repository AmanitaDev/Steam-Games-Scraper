import requests
import pandas as pd


def get_full_review_histogram_df(app_id):
    """Fetches the complete historical day-by-day review chart data

    and returns it as a fully structured Pandas DataFrame.
    """
    url = f"https://store.steampowered.com/appreviewhistogram/{app_id}"
    params = {"json": 1}

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Failed to connect. Status code: {response.status_code}")
            return None

        data = response.json()
        if data.get("success") != 1 or "results" not in data:
            print("Steam returned success=0 or missing results arrays.")
            return None

        rollups = data["results"].get("rollups", [])
        if not rollups:
            print("No daily tracking entries available.")
            return None

        # 1. Parse the raw JSON array into a clean Pandas dataframe
        df_histogram = pd.DataFrame(rollups)

        # 2. Clean column headers to make them readable
        df_histogram = df_histogram.rename(
            columns={
                "date": "Unix_Timestamp",
                "recommendations_up": "Launch_Positive_Reviews",
                "recommendations_down": "Launch_Negative_Reviews",
            }
        )

        # 3. Convert the raw Unix epoch timestamp into actual standard dates
        df_histogram["Date"] = pd.to_datetime(
            df_histogram["Unix_Timestamp"], unit="s"
        ).dt.date

        # 4. Calculate total daily submissions and rolling tracking totals
        df_histogram["Total_Launch_Reviews"] = (
            df_histogram["Launch_Positive_Reviews"] + df_histogram["Launch_Negative_Reviews"]
        )

        # Reorder columns for a clean workspace look
        final_columns = [
            "Date",
            "Launch_Positive_Reviews",
            "Launch_Negative_Reviews",
            "Total_Launch_Reviews"
        ]

        return df_histogram[final_columns]

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def GetLaunchMetrics(target_appid):
    print(f"Downloading full historical review timeline for AppID {target_appid}...")
    full_chart_df = get_full_review_histogram_df(target_appid)

    if full_chart_df is not None:
        print(f"\nSuccessfully built a {full_chart_df.shape[0]}-month history map.")
        # Slices the dataframe to keep up to index 3
        full_chart_df = full_chart_df.iloc[:3]
        # display(full_chart_df)

        # Sum all numeric columns and format it as a clean single-row DataFrame
        single_row_df = full_chart_df.sum(numeric_only=True).to_frame().T

        # 1. Define your industry-standard Boxleiter multiplier
        # (You can adjust this number, e.g., 30, 40, or 50 depending on your thesis baseline)
        boxleiter_multiplier = 40

        # 2. Calculate the estimated owner count based strictly on launch window reviews
        single_row_df["Boxleiter_Launch_Owners"] = (
                single_row_df["Total_Launch_Reviews"] * boxleiter_multiplier
        )

        # 3. Format the number with commas so it's clean and easy to read in your notebook
        pd.options.display.float_format = "{:,.0f}".format

        return single_row_df['Launch_Positive_Reviews'], single_row_df['Launch_Negative_Reviews'], single_row_df['Total_Launch_Reviews']