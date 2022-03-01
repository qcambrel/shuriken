from shuriken_tools import mal, mal_access, youtube, pipeline, api_keys
import streamlit as st
import time


def search_by_season(season)


if __name__ == '__main__':
	db = pipeline.DBConnection('anime.db')
	cur, conn = db.setup()
	
	st.title('Shuriken')
	
	season = st.selectbox('Season', ('spring', 'summer', 'fall', 'winter'))
	years = reversed(range(1972, int(time.ctime().split(' ')[-1]) + 1))
	year = st.selectbox('Year', tuple(years))
	limit = int(st.text_input('Title Limit (default: 1 | max: 20)', '1'))
	if st.button('Search Season'):
		season_list = mal.AnimeList(season, year)
		season_list.run()

	anime = st.text_input('Title')
	if st.button('Search Title'):
		search_by_title(anime, cur, conn)
	
	# if st.button('Analyze'):
	# 	analyze_data(cur, conn)

	if st.button('Generate Log File'):
		pass
