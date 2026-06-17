import sys
import argparse
import os

# 1. Import the original script as a module
import SteamGamesScraper

if __name__ == "__main__":
    # Define a single target AppID to test (e.g., "413150" for Stardew Valley, 526870 for Satisfactory)
    test_appid = "413150"

    # 2. Redirect the output files to temporary test targets
    # This prevents your real 'games.json' from being altered.
    test_infile = "test_games.json"  # Read from your real games if you want to check states
    test_outfile = "test_run_output.json"  # DUMP OUTPUT HERE INSTEAD OF OVERWRITING

    # Temporarily redirect the global file variables in the module to target dummy files
    SteamGamesScraper.DISCARDED_FILE = "test_discarded.json"
    SteamGamesScraper.NOTRELEASED_FILE = "test_notreleased.json"
    SteamGamesScraper.APPLIST_FILE = "test_applist.json"

    # 3. Mock the command-line arguments using our safe test output file
    sys.argv = [
        "SteamGamesScraper.py",
        "--infile", test_infile,
        "--outfile", test_outfile,
        "--sleep", "1.0",
        "--retries", "4"
    ]

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', type=str, default='games.json')
    parser.add_argument('-o', '--outfile', type=str, default='games.json')
    parser.add_argument('-s', '--sleep', type=float, default=1.5)
    parser.add_argument('-r', '--retries', type=int, default=4)
    parser.add_argument('-a', '--autosave', type=int, default=100)
    parser.add_argument('-d', '--released', type=bool, default=True)
    parser.add_argument('-c', '--currency', type=str, default='us')
    parser.add_argument('-l', '--language', type=str, default='en')
    parser.add_argument('-p', '--steamspy', type=str, default=True)
    parser.add_argument('-u', '--update', type=str, default='')
    parser.add_argument('-oa', '--only-applist', action='store_true')
    args = parser.parse_args()

    # 4. Grab the Steam API Key
    STEAM_API_KEY = None
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('STEAM_API_KEY='):
                    STEAM_API_KEY = line.split('=')[1].strip()
                    break

    if not STEAM_API_KEY:
        print("[E] STEAM_API_KEY not found in .env file.")
        sys.exit(1)

    # 5. Load the current data, or start completely fresh for the test
    dataset = SteamGamesScraper.LoadJSON(args.infile) or {}
    discarded = SteamGamesScraper.LoadJSON(SteamGamesScraper.DISCARDED_FILE) or {}
    notreleased = SteamGamesScraper.LoadJSON(SteamGamesScraper.NOTRELEASED_FILE) or []

    # Clear target out of memory so it runs clean
    if test_appid in dataset: del dataset[test_appid]
    if test_appid in discarded: del discarded[test_appid]
    if test_appid in notreleased: notreleased.remove(test_appid)

    print(f"[i] Running isolated test for AppID: {test_appid}")
    print(f"[i] Real database files will NOT be overwritten.")

    # 6. Execute
    added, not_released, discarded_count = SteamGamesScraper.Scraper(
        dataset=dataset,
        notreleased=notreleased,
        discarded=discarded,
        args=args,
        steam_api_key=STEAM_API_KEY,
        appIDs=[test_appid]
    )

    # 7. Print out results instantly to console
    if test_appid in dataset:
        print("\n" + "=" * 40 + "\n[i] PARSED DATA RESULT:")
        print(f"{dataset[test_appid]}")

    # 8. Clean up the newly created test files automatically if you don't want them left behind
    for f in [test_outfile, SteamGamesScraper.DISCARDED_FILE, SteamGamesScraper.NOTRELEASED_FILE]:
        if os.path.exists(f):
            os.remove(f)

    print("\n[i] Test completed. All temporary test files cleaned up successfully.")