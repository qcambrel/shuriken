# Shuriken

Shuriken aims to become a playground for exploratory analysis of anime. Currently, the primary purpose of the Streamlit app is to automate a considerable portion of the data collection process. The project is currently undergoing some major refactoring, which will be followed by some new features.


## Dependencies

This should be all that is needed for the stable branch.

- ***streamlit***
- ***pandas***
- ***requests***
- ***google-api-python-client***


## Credentials

Shuriken is supported by the YouTube Data API (v3) and the MyAnimeList API (beta v2). In order to run the application, you must acquire access keys for both. You can get an API key for the YouTube Data API through the Google Cloud Console. The Shuriken application provides functionality for generation of access tokens for the MyAnimeList API, but you still need to create a client ID through your MyAnimeList account. You will also need to maintain a local SQLite database (for now).

## Getting Started

Please only attempt to run the stable branch to get a feel for the project. The refactor is incomplete is will break in a multitude of ways.

I use Poetry, but if you want to use a different package manager, that is fine.

```sh
poetry shell
poetry install
export YOUTUBE_API_KEY=secret
export MAL_CLIENT_ID=secret
export MAL_CLIENT_SECRET=secret
streamlit run main.py
```

Remember to retrieve an authentication code first then copy and paste it in order to generate an access token.
