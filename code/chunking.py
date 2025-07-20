import pandas as pd

print("Initiated Chunking process.......")

df = pd.read_csv('cleaned_voxcinemas_showtimes.csv')

# Group by all key metadata including genres and cast
grouped = df.groupby([
    'moviename', 'rating', 'languages', 'duration', 'genres', 'cast', 'cinema', 'format'
])

chunks = []

for group_keys, group_df in grouped:
    moviename, rating, language, duration, genres, cast, cinema, format_ = group_keys
    showtime_links = [
        f"{row['showtime']} → {row['booking_link']}" for _, row in group_df.iterrows()
    ]
    showtime_links_str = ", ".join(showtime_links)

    chunk = (
        f"{moviename} ({rating}, {language}, {duration}) "
        f"is a {genres} film starring {cast}. "
        f"It is currently showing at {cinema} in {format_} format. "
        f"Showtimes and bookings: [{showtime_links_str}]"
    )

    chunks.append(chunk)

# Save the chunks
pd.DataFrame({'chunk': chunks}).to_csv('voxcinemas_chunks.csv', index=False)

print("Chunking complete. Output saved to voxcinemas_chunks.csv ✅")
