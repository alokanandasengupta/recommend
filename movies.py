import streamlit as st
import pandas as pd

# Custom CSS for better UI
def add_custom_css():
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .movie-card {
            background-color: #f0f2f6;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .similarity-score {
            color: #0068c9;
            font-weight: bold;
            font-size: 1.1em;
        }
        .movie-title {
            color: #262730;
            font-size: 24px;
            font-weight: bold;
        }
        .section-divider {
            margin: 20px 0;
            border-bottom: 2px solid #f0f2f6;
        }
        .stButton>button {
            width: 100%;
            background-color: #0068c9;
            color: white;
        }
        .stButton>button:hover {
            background-color: #004d99;
        }
        </style>
    """, unsafe_allow_html=True)

# Cache the data loading
@st.cache_data
def load_data():
    file_path = "Updated_Movie_Data_with_Keywords4.csv"  # Ensure this is a string
    
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            st.error("The loaded dataset is empty.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        return None

# Helper functions for similarity calculations
def calculate_genre_similarity(primary_genre1, primary_genre2):
    weight = 0.23
    return weight if primary_genre1 == primary_genre2 else 0

def calculate_director_similarity(director1, director2):
    weight = 0.16
    return weight if director1 == director2 else 0

def calculate_keyword_similarity(keywords1, keywords2):
    weight = 0.155
    keywords1_set = set(str(keywords1).split(', '))
    keywords2_set = set(str(keywords2).split(', '))
    intersection = keywords1_set & keywords2_set
    return (len(intersection) / len(keywords1_set | keywords2_set) if keywords1_set and keywords2_set else 0) * weight

def calculate_cast_similarity(cast1, cast2):
    weight = 0.185
    cast1_set = set(str(cast1).split(', '))
    cast2_set = set(str(cast2).split(', '))
    intersection = cast1_set & cast2_set
    return (len(intersection) / len(cast1_set | cast2_set) if cast1_set and cast2_set else 0) * weight

def calculate_year_similarity(year1, year2):
    weight = 0.14
    try:
        year1 = int(year1)
        year2 = int(year2)
        return (1 - (abs(year1 - year2) / 10)) * weight if abs(year1 - year2) <= 10 else 0
    except ValueError:
        return 0

def calculate_rating_similarity(rating1, rating2):
    weight = 0.125
    try:
        rating1 = float(rating1)
        rating2 = float(rating2)
        return (1 - abs(rating1 - rating2) / 10) * weight if abs(rating1 - rating2) <= 10 else 0
    except ValueError:
        return 0

def recommend_movies(movie_title, dataset, num_recommendations=5):
    dataset.columns = [col.strip() for col in dataset.columns]
    
    rating_column = next((col for col in dataset.columns if 'rating' in col.lower()), None)
    name_column = next((col for col in dataset.columns if 'name' in col.lower()), 'Name')
    genre_column = next((col for col in dataset.columns if 'genre ' in col.lower()), 'Primary Genre')
    director_column = next((col for col in dataset.columns if 'director' in col.lower()), 'Director')
    year_column = next((col for col in dataset.columns if 'year' in col.lower()), 'Theatrical Release Year')
    synopsis_column = next((col for col in dataset.columns if 'synopsis' in col.lower()), 'Synopsis')

    if movie_title not in dataset[name_column].values:
        st.warning("Movie title not found in the dataset.")
        return []

    movie_data = dataset[dataset[name_column] == movie_title].iloc[0]
    similarities = []

    for index, row in dataset.iterrows():
        if row[name_column] == movie_title:
            continue

        genre_sim = calculate_genre_similarity(movie_data[genre_column], row[genre_column])
        director_sim = calculate_director_similarity(movie_data[director_column], row[director_column])
        keyword_sim = calculate_keyword_similarity(movie_data['Keywords'], row['Keywords'])
        cast_sim = calculate_cast_similarity(movie_data['Cast'], row['Cast'])
        year_sim = calculate_year_similarity(movie_data[year_column], row[year_column])
        rating_sim = calculate_rating_similarity(movie_data[rating_column], row[rating_column])

        total_similarity = genre_sim + director_sim + keyword_sim + cast_sim + year_sim + rating_sim
        similarities.append((row[name_column], total_similarity))

    # Sort by similarity score
    similarities.sort(key=lambda x: x[1], reverse=True)

    # Get top N recommendations
    recommendations = similarities[:num_recommendations]
    return recommendations

def main():
    add_custom_css()
    st.title("Movie Recommendation System")
    
    dataset = load_data()
    if dataset is None:
        return

    movie_title = st.text_input("Enter a movie title:")
    if st.button("Get Recommendations"):
        if movie_title:
            recommendations = recommend_movies(movie_title, dataset)
            if recommendations:
                for title, score in recommendations:
                    st.markdown(f"**{title}** - Similarity Score: {score:.2f}")
            else:
                st.warning("No recommendations found.")
        else:
            st.warning("Please enter a movie title.")

if __name__ == "__main__":
    main()
