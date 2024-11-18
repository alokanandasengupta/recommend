import streamlit as st
import pandas as pd
import os

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
    file_path = "Updated_Movie_Data_with_Keywords4.csv"
    
    try:
        # Try to read the CSV file
        df = pd.read_csv(file_path)
        
        # Verify the dataframe is not empty
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
    # Normalize column names by stripping whitespace
    dataset.columns = [col.strip() for col in dataset.columns]
    
    # Check column names to handle potential variations
    rating_column = next((col for col in dataset.columns if 'rating' in col.lower()), None)
    name_column = next((col for col in dataset.columns if 'name' in col.lower()), 'Name')
    genre_column = next((col for col in dataset.columns if 'genre ' in col.lower()), 'Primary Genre')
    director_column = next((col for col in dataset.columns if 'director' in col.lower()), 'Director')
    year_column = next((col for col in dataset.columns if 'year' in col.lower()), 'Theatrical Release Year')
    synopsis_column = next((col for col in dataset.columns if 'synopsis' in col.lower()), 'Synopsis')
    keywords_column = next((col for col in dataset.columns if 'keyword' in col.lower()), 'keywords4')
    cast_column = next((col for col in dataset.columns if 'cast' in col.lower()), 'Cast')
    age_rating_column = next((col for col in dataset.columns if 'age' in col.lower()), 'Age Rating')

    selected_movie = dataset[dataset[name_column] == movie_title]
    
    if selected_movie.empty:
        st.error(f"Movie '{movie_title}' not found in dataset.")
        return []

    selected_movie = selected_movie.iloc[0]
    similarity_scores = []

    for _, movie in dataset.iterrows():
        if movie[name_column] == movie_title:
            continue

        genre_sim = calculate_genre_similarity(selected_movie[genre_column], movie[genre_column])
        director_sim = calculate_director_similarity(selected_movie[director_column], movie[director_column])
        
        # Added safety checks for optional columns
        keyword_sim = calculate_keyword_similarity(
            selected_movie.get(keywords_column, ''), 
            movie.get(keywords_column, '')
        )
        
        rating_sim = calculate_rating_similarity(
            selected_movie.get(rating_column, 0), 
            movie.get(rating_column, 0)
        )
        
        cast_sim = calculate_cast_similarity(
            selected_movie.get(cast_column, ''), 
            movie.get(cast_column, '')
        )
        
        year_sim = calculate_year_similarity(
            selected_movie.get(year_column, 0), 
            movie.get(year_column, 0)
        )

        overall_similarity = genre_sim + director_sim + keyword_sim + cast_sim + rating_sim + year_sim

        similarity_scores.append({
            'Name': movie[name_column],
            'Primary Genre': movie[genre_column],
            'Synopsis': movie.get(synopsis_column, 'No synopsis available'),
            'Age Rating': movie.get(age_rating_column, 'N/A'),
            'Director': movie[director_column],
            'Theatrical Release Year': movie.get(year_column, 'N/A'),
            'Cast': movie.get(cast_column, 'N/A'),
            'Overall Similarity': overall_similarity
        })

    similarity_scores = sorted(similarity_scores, key=lambda x: x['Overall Similarity'], reverse=True)
    return similarity_scores[:num_recommendations]

def main():
    st.set_page_config(
        page_title="Movie Recommendation System",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    add_custom_css()

    # Sidebar
    with st.sidebar:
        st.title("About")
        st.info(
            "This movie recommendation system uses machine learning to suggest movies "
            "based on various factors including genre, director, cast, and more. "
            "Simply select a movie you like, and the system will recommend similar movies!"
        )
        
        st.title("How it works")
        st.write("""
        The recommendation system considers:
        - Genre (23% weight)
        - Cast (18.5% weight)
        - Director (16% weight)
        - Keywords (15.5% weight)
        - Release Year (14% weight)
        - Rating Score (12.5% weight)
        """)

    # Main content
    st.title("🎬 Movie Recommendation System")
    st.write("Discover your next favorite movie!")

    # Load data
    dataset = load_data()
    
    if dataset is not None:
        # Create a selectbox with all movie titles
        movie_titles = sorted(dataset['Name'].unique())
        selected_movie = st.selectbox("Select a movie you like:", movie_titles)
        
        col1, col2 = st.columns([2,  1])
        with col1:
            num_recommendations = st.slider("Number of recommendations:", 1, 10, 5)
        with col2:
            st.write("")
            st.write("")
            if st.button("🔍 Get Recommendations", key="recommend_button"):
                with st.spinner("Finding recommendations..."):
                    recommendations = recommend_movies(selected_movie, dataset, num_recommendations)
                
                if recommendations:
                    # Display selected movie details
                    st.markdown("### 🎥 Selected Movie")
                    selected_movie_details = dataset[dataset['Name'] == selected_movie].iloc[0]
                    st.write(f"**Title:** {selected_movie_details['Name']}")
                    st.write(f"**Genre:** {selected_movie_details ['Primary Genre']}")
                    st.write(f"**Director:** {selected_movie_details['Director']}")
                    st.write(f"**Release Year:** {selected_movie_details['Theatrical Release Year']}")
                    st.write(f"**Rating:** {selected_movie_details.get('Rating Score', 'N/A')}")
                    st.write(f"**Synopsis:** {selected_movie_details['Synopsis']}")

                    # Display recommendations
                    st.markdown("### 📽️ Recommendations")
                    for rec in recommendations:
                        st.markdown(f"**Title:** {rec['Name']}")
                        st.write(f"**Genre:** {rec['Primary Genre']}")
                        st.write(f"**Director:** {rec['Director']}")
                        st.write(f"**Release Year:** {rec['Theatrical Release Year']}")
                        st.write(f"**Rating:** {rec.get('Age Rating', 'N/A')}")
                        st.write(f"**Synopsis:** {rec['Synopsis']}")
                        st.markdown("---")

       

        # Feedback section
        st.markdown("### 📝 Feedback")
        st.write("Please take a moment to share your thoughts—they’ll guide me in creating an even better experience for everyone.")
        st.write("P.S: Its the first trial model so if you notice anything incorrect that i dont then drop that feedback by too!")
        st.markdown("[Click here to provide feedback](https://forms.gle/n5SR52xR7MrmMt9k7)")

if __name__ == "__main__":
    main()
