import pandas as pd

print("Cleaning dataset......")

# Load the dataset
df = pd.read_csv('voxcinemas_showtimes.csv')

# Normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Group the data
grouped = df.groupby([
    'movie_name', 'rating', 'languages', 'duration', 'genres', 'cast', 'cinema', 'format'
]).agg({
    'showtime': lambda x: list(x),
    'booking_link': lambda x: list(x)
}).reset_index()

# Add movie ID
grouped.insert(0, 'movieid', range(1001, 1001 + len(grouped)))

# Rename columns if needed
grouped.rename(columns={
    'movie_name': 'moviename'
}, inplace=True)

# Save cleaned dataset
grouped.to_csv('cleaned_voxcinemas_showtimes.csv', index=False)
print("Dataset Cleaned ✅")
