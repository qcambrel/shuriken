# Shuriken

Anime reception analysis: Comparing early attention to the success of a season

## Streamlit App

I made a Streamlit app to create an environment that would make testing, experimentation, data collection, and data visualization easier.

## Requirements

Shuriken depends on the YouTube Data API (v3) and the MyAnimeList API (beta v2). In order to run the application, you must acquire access keys for both. You can get an API key for the YouTube Data API through the Google Cloud Console. The Shuriken application provides functionality for generation of access tokens for the MyAnimeList API, but you still need to create
a client ID through your MyAnimeList account. you will also need to maintain a local SQLite database.

## TODO

The core functionality of the application is mostly complete. The next steps entail further data collection followed by data analysis and visualization.