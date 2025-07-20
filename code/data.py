from bs4 import BeautifulSoup
import requests
import csv
import time

TMDB_API_KEY = "a83a6075623c21b2af29d3e7924dd90f"

# TMDB API helpers
def get_tmdb_movie_data(title):
    try:
        # Step 1: Search movie by title
        search_url = f"https://api.themoviedb.org/3/search/movie"
        search_params = {
            "api_key": TMDB_API_KEY,
            "query": title,
        }
        search_resp = requests.get(search_url, params=search_params)
        search_data = search_resp.json()
        results = search_data.get("results")
        if not results:
            return "", ""

        movie_id = results[0]["id"]

        # Step 2: Get movie details for genres
        details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        details_resp = requests.get(details_url, params={"api_key": TMDB_API_KEY})
        details_data = details_resp.json()
        genres = [genre["name"] for genre in details_data.get("genres", [])]
        genres_str = ", ".join(genres)

        # Step 3: Get cast info
        credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits"
        credits_resp = requests.get(credits_url, params={"api_key": TMDB_API_KEY})
        credits_data = credits_resp.json()
        cast = [actor["name"] for actor in credits_data.get("cast", [])[:3]]
        cast_str = ", ".join(cast)

        return genres_str, cast_str
    except Exception as e:
        print(f"TMDB API Error for '{title}': {e}")
        return "", ""

# --- Start scraping VOX ---
print("Obtaining dataset from site......")

url = "https://uae.voxcinemas.com/showtimes?c=abu-dhabi-mall-abu-dhabi&c=al-hamra-mall-ras-al-khaimah&c=al-jimi-mall&c=burjuman&c=city-centre-ajman&c=city-centre-al-zahia&c=city-centre-deira&c=city-centre-fujairah&c=city-centre-mirdif&c=city-centre-sharjah&c=city-centre-shindagha&c=dubai-festival-city-mall&c=megaplex-cineplex-grand-hyatt&c=mall-of-the-emirates&c=mercato&c=nakheel-mall&c=nation-towers-abu-dhabi&c=reem-mall-abu-dhabi&c=the-galleria-al-maryah-island&c=wafi-mall-at-wafi-city&c=yas-mall-abu-dhabi"
response = requests.get(url)

if response.status_code == 200:
    with open("page.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("Page saved to page.html")
else:
    print(f"Failed to retrieve page: Status code {response.status_code}")
    exit()

with open("page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

output_rows = []
tmdb_cache = {}  # Cache to avoid duplicate API calls

movie_divs = soup.find_all("div")
for movie_div in movie_divs:
    title_tag = movie_div.find("h2")
    if not title_tag:
        continue

    movie_name = title_tag.text.strip()
    rating_tag = movie_div.find("span", class_="classification")
    rating = rating_tag.text.strip() if rating_tag else ""

    lang_tags = movie_div.find_all("span", class_="tag")
    duration = ""
    languages = []
    for tag in lang_tags:
        txt = tag.text.strip()
        if "min" in txt:
            duration = txt
        else:
            languages.append(txt)
    languages_str = ", ".join(languages)

    dates_div = movie_div.find_next("div", class_="dates")
    if not dates_div:
        continue

    # Get genres and cast via TMDB API
    if movie_name not in tmdb_cache:
        genres, cast = get_tmdb_movie_data(movie_name)
        tmdb_cache[movie_name] = (genres, cast)
        time.sleep(0.25)  # polite delay to avoid rate limiting
    else:
        genres, cast = tmdb_cache[movie_name]

    cinema_headers = dates_div.find_all("h3", class_="highlight")
    for cinema_header in cinema_headers:
        cinema_name = cinema_header.text.strip()

        showtimes_ol = cinema_header.find_next_sibling("ol", class_="showtimes")
        if not showtimes_ol:
            continue

        for fmt_li in showtimes_ol.find_all("li", recursive=False):
            fmt_tag = fmt_li.find("strong")
            if not fmt_tag:
                continue
            screen_format = fmt_tag.text.strip()

            times_ol = fmt_li.find("ol")
            if not times_ol:
                continue

            for show_li in times_ol.find_all("li"):
                a_tag = show_li.find("a", class_="action showtime")
                if not a_tag:
                    continue

                showtime = a_tag.text.strip()
                booking_link = a_tag.get("href", "")
                if booking_link and not booking_link.startswith("http"):
                    booking_link = "https://uae.voxcinemas.com" + booking_link

                output_rows.append([
                    movie_name, rating, languages_str, duration,
                    genres, cast, cinema_name, screen_format,
                    showtime, booking_link
                ])

# Save to CSV
with open("voxcinemas_showtimes.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "Movie Name", "Rating", "Languages", "Duration",
        "Genres", "Cast", "Cinema", "Format",
        "Showtime", "Booking Link"
    ])
    writer.writerows(output_rows)

print("✅ Data saved to voxcinemas_showtimes.csv with genres and cast")
