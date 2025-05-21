import streamlit as st
import gzip
import pickle
import requests
from io import BytesIO

# --- Page Setup ---
st.set_page_config(
    page_title="ChibiChoice",
    page_icon="assets/cloud.png",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Function to load compressed pickle from URL
@st.cache_resource
def load_pickle_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
        return pickle.load(f)

# --- Get Cover Image from Jikan API ---
@st.cache_data(show_spinner=False)
def get_manga_image_url(title):
    try:
        response = requests.get('https://api.jikan.moe/v4/manga', params={'q': title, 'limit': 1}, timeout=5)
        response.raise_for_status()
        data = response.json()
        image_url = data['data'][0]['images']['jpg']['large_image_url']
        return image_url
    except (requests.exceptions.RequestException, IndexError, KeyError):
        return None


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
    for i in distances[1:21]:  # Top 20 recommendations
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
mangas = load_pickle_from_url(manga_url)
similarity = load_pickle_from_url(similarity_url)

# --- Streamlit UI Setup ---
col1, col2 = st.columns([1, 6])
with col1:
    st.image("assets/ramen-bowl.png", width=64)
with col2:
    st.markdown("## ChibiChoice")
    st.caption("Smart, fun manga picks — tailored to your taste.")


st.image('assets/banner-page.jpg', use_container_width=True)

manga_list = mangas['title'].values

# Add a placeholder option to the beginning of the list
manga_options = ["Choose an option"] + list(mangas['title'].values)

selected_manga = st.selectbox(
    "Type or Select a manga to get recommendations",
    manga_options
)

# Only show button if an actual manga is selected
if selected_manga != "Choose an option":
    if st.button("Show Recommendations"):
        st.session_state.recommendations = recommend(selected_manga)
        st.session_state.current_index = 0
else:
    st.info("Please select a manga title to get recommendations.")

# Session state for index and recommendations
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = []


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
        st.image('assets/banner-page.jpg', width=300)


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

