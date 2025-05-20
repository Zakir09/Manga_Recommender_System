import streamlit as st
import gzip
import pickle
import requests
from io import BytesIO

# Function to load compressed pickle from URL
def load_pickle_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
        return pickle.load(f)

# --- Get Cover Image from Jikan API ---
def get_manga_image_url(title):
    response = requests.get('https://api.jikan.moe/v4/manga', params={'q': title, 'limit': 1})
    try:
        data = response.json()
        image_url = data['data'][0]['images']['jpg']['large_image_url']
        return image_url
    except (IndexError, KeyError):
        return None

# Define handlers
# Define handlers with looping
def go_previous():
    st.session_state.current_index = (
        st.session_state.current_index - 1
    ) % len(st.session_state.recommendations)

def go_next():
    st.session_state.current_index = (
        st.session_state.current_index + 1
    ) % len(st.session_state.recommendations)

# --- Recommendation Logic ---
def recommend(manga):
    index = mangas[mangas['title'] == manga].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended = []
    for i in distances[1:11]:  # Top 10 recommendations
        entry = {
            "title": mangas.iloc[i[0]].title,
            "description": mangas.iloc[i[0]].description,
            "rating": mangas.iloc[i[0]].rating,
            "tags": mangas.iloc[i[0]].tags
        }
        recommended.append(entry)
    return recommended

# Remote file URLs
manga_url = 'https://huggingface.co/datasets/Zakir09/manga-artifacts/resolve/main/manga_list.pkl.gz'
similarity_url = 'https://huggingface.co/datasets/Zakir09/manga-artifacts/resolve/main/similarity.pkl.gz'

# --- Load Data from Hugging Face ---
with gzip.open('artifacts/manga_list.pkl.gz', 'rb') as f:
    mangas = pickle.load(f)

with gzip.open('artifacts/similarity.pkl.gz', 'rb') as f:
    similarity = pickle.load(f)

# --- Streamlit UI Setup ---
st.set_page_config(layout="centered")
st.title("📚 Manga Recommender")
st.subheader("Get manga recommendations based on your favorite mangas!")

st.image('artifacts/banner.jpg', use_container_width=True)

manga_list = mangas['title'].values
selected_manga = st.selectbox("Type or Select a manga to get recommendations", manga_list)

# Session state for index and recommendations
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []

# Generate recommendations
if st.button("Show Recommendations"):
    st.session_state.recommendations = recommend(selected_manga)
    st.session_state.current_index = 0  # reset view

# Display recommendation
if st.session_state.recommendations:
    recs = st.session_state.recommendations
    current = recs[st.session_state.current_index]

    # Fetch image live
    image_url = get_manga_image_url(current['title'])

    # Show image
    if image_url:
        st.image(image_url, width=300)
    else:
        st.image('artifacts/banner.jpg', width=300)


    # Show info
    st.markdown("### " + current['title'])
    st.write(f"**Tags:** {current['tags']}")
    st.write(f"**Description:** {current['description']}")
    st.write(f"**Rating:** ⭐ {current['rating']}")

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.button("⬅️ Previous", on_click=go_previous)
    with col3:
        st.button("Next ➡️", on_click=go_next)


    st.markdown(f"Viewing recommendation {(st.session_state.current_index % len(recs)) + 1} of {len(recs)}")

