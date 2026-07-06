import sys
import os
import json
import argparse
import csv


def ProgressBar(count, total):
    """Displays a simple progress bar in the console."""
    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '█' * filled_len + '░' * (bar_len - filled_len)
    sys.stdout.write(f'\r{bar} {percents}%')
    sys.stdout.flush()


def get_string(app, key, default=''):
    """Safely extracts strings and strips newlines."""
    if key in app and app[key] not in (None, ''):
        return str(app[key]).replace('\n', ' ').replace('\r', ' ').strip()
    return default


def get_string_array(app, key):
    """Safely extracts arrays and joins them into a single comma-separated string."""
    if key in app and isinstance(app[key], list):
        values = [str(v).replace('\n', ' ').replace('\r', ' ').strip() for v in app[key] if v is not None]
        return ','.join(values)
    return ""


def get_key(app, key, default='0'):
    """Safely extracts numeric or boolean keys."""
    return str(app[key]) if key in app and app[key] is not None else default


def get_tags(app):
    """Extracts just the tag names from the tags dictionary, ignoring the weights."""
    if 'tags' in app and isinstance(app['tags'], dict):
        return ','.join(app['tags'].keys())
    return ""


def get_packages(app):
    """Extracts only the titles from the nested packages list."""
    if 'packages' in app and isinstance(app['packages'], list):
        titles = []
        for pkg in app['packages']:
            if isinstance(pkg, dict) and 'title' in pkg:
                titles.append(str(pkg['title']).replace('\n', ' ').strip())
        return ','.join(titles)
    return ""


def main():
    print('Convert JSON to CSV.')
    parser = argparse.ArgumentParser(description='Convert JSON to CSV.')
    parser.add_argument('-f', '--file', type=str, default='games.json', help='Dataset file name')
    args = parser.parse_args()

    filename = args.file
    if not os.path.exists(filename):
        print(f'Dataset file \'{filename}\' not found.')
        sys.exit()

    print('Loading dataset...')
    with open(filename, 'r', encoding='utf-8') as fin:
        dataset = json.load(fin)

    print(f'Dataset with {len(dataset)} games loaded. Starting conversion...')

    header = [
        'AppID', 'Name', 'Release date', 'Required age', 'Price',
        'Detailed description', 'About the game', 'Short description',
        'Header image', 'Capsule image', 'Website', 'Support url',
        'Support email', 'Windows', 'Mac', 'Linux', 'Metacritic score',
        'Metacritic url', 'Achievements', 'Supported languages',
        'Full audio languages', 'Packages', 'Developers', 'Publishers',
        'Categories', 'Genres', 'Screenshots', 'Movie count',
        'Estimated owners', 'Tags', 'Launch positive reviews',
        'Launch negative reviews', 'Total launch reviews',
        'Launch average players', 'Launch peak players'
    ]

    with open('games.csv', 'w', encoding="utf-8", newline='') as fout:
        # csv.QUOTE_MINIMAL ensures that any fields containing commas (like our joined arrays)
        # are wrapped in quotes so they don't break the column structure.
        writer = csv.writer(fout, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)

        total = len(dataset)
        for count, (appID, app) in enumerate(dataset.items(), 1):
            row = [
                appID,
                get_string(app, 'name'),
                get_string(app, 'release_date'),
                get_key(app, 'required_age'),
                get_key(app, 'price', '0.0'),
                get_string(app, 'detailed_description'),
                get_string(app, 'about_the_game'),
                get_string(app, 'short_description'),
                get_string(app, 'header_image'),
                get_string(app, 'capsule_image'),
                get_string(app, 'website'),
                get_string(app, 'support_url'),
                get_string(app, 'support_email'),
                get_key(app, 'windows', 'False'),
                get_key(app, 'mac', 'False'),
                get_key(app, 'linux', 'False'),
                get_key(app, 'metacritic_score'),
                get_string(app, 'metacritic_url'),
                get_key(app, 'achievements'),
                get_string_array(app, 'supported_languages'),
                get_string_array(app, 'full_audio_languages'),
                get_packages(app),
                get_string_array(app, 'developers'),
                get_string_array(app, 'publishers'),
                get_string_array(app, 'categories'),
                get_string_array(app, 'genres'),
                get_string_array(app, 'screenshots'),
                get_key(app, 'movie_count'),
                get_string(app, 'estimated_owners'),
                get_tags(app),
                get_key(app, 'Launch_Positive_Reviews'),
                get_key(app, 'Launch_Negative_Reviews'),
                get_key(app, 'Total_Launch_Reviews'),
                get_key(app, 'Launch_Avg_Players'),
                get_key(app, 'Launch_Peak_Players')
            ]

            writer.writerow(row)
            ProgressBar(count, total)

    print('\nDone.')


if __name__ == "__main__":
    main()