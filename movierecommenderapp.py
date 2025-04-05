import pandas as pd
import streamlit as st
import requests
import re

def fetch_poster(movie_title):
    api_key = "70a61a1ec6ccf4d26ae5aabfa7f1990f"
    
    clean_title = re.sub(r"\s\(\d{4}\)", "", movie_title)
    
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={clean_title}"
    response = requests.get(url)
    data = response.json()
    
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    
    return None
  
ratings = pd.read_csv("ratings.csv", sep="::", engine="python", names=["user_id", "movie_id", "rating", "timestamp"])
movies = pd.read_csv("movies.csv", sep="::", engine="python", names=["movie_id", "title", "genres"], encoding="latin1")
df = ratings.merge(movies, on="movie_id")
user_movie_matrix = df.pivot_table(index="user_id", columns="title", values="rating")


st.title("Movie Recommender System")

movie_list = list(user_movie_matrix.columns)
target_movie = st.selectbox("Choose a movie you like:", [""] + movie_list, index=0)

if target_movie:
    if user_movie_matrix[target_movie].isnull().all():
        st.warning("Not enough data for this movie to make recommendations. Please choose another.")
        st.stop()


    similarity = user_movie_matrix.corrwith(user_movie_matrix[target_movie])
    similarity_df = similarity.dropna().to_frame(name='correlation')
    movie_stats = df.groupby('title')['rating'].agg(['count', 'mean'])
    similarity_df = similarity_df.join(movie_stats)
    recommended = similarity_df[similarity_df['count'] > 50].sort_values('correlation', ascending=False).head(10)


    st.subheader("Top 10 Recommendations:")
    for index, row in recommended.iterrows():
        st.markdown(f"**{row.name}**")
        poster_url = fetch_poster(row.name)
        if poster_url and "placeholder" not in poster_url:
            st.image(poster_url, width=150)
        else:
            st.write("Poster not available.")

        st.write(f"⭐ Correlation: {row['correlation']:.2f} | 👥 Count: {int(row['count'])} | 🌟 Mean Rating: {row['mean']:.2f}")
else:
    st.info("Pick a movie from the list above to get recommendations.")
