import pickle
import streamlit as st

def recommend(manga):
    index = mangas[mangas['title'] == manga].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    
    recommended_mangas_name = []
    recommended_mangas_rating = []
    recommended_mangas_tags = []

    for i in distances[1:9]:
        recommended_mangas_name.append(mangas.iloc[i[0]].title)
        recommended_mangas_rating.append(mangas.iloc[i[0]].rating)
        recommended_mangas_tags.append(mangas.iloc[i[0]].tags)
        
    return recommended_mangas_name, recommended_mangas_tags, recommended_mangas_rating

#--- STREAMLIT UI ---

st.title("Manga Recommender")
st.subheader("Get manga recommendations based on your favorite mangas!")

st.image('artifacts/banner.jpg', use_container_width=True)

mangas = pickle.load(open('artifacts/manga_list.pkl', 'rb'))
similarity = pickle.load(open('artifacts/similarity.pkl', 'rb'))

manga_list = mangas['title'].values

selected_manga = st.selectbox(
    'Type or Select a manga to get recommendation',
    manga_list
)

if st.button('Show Recommendation'):
    recommended_mangas_name, recommended_mangas_tags, recommended_mangas_rating = recommend(selected_manga)

    st.markdown("<br>", unsafe_allow_html=True)
    num_recommendations = len(recommended_mangas_name)
    columns = st.columns(4) 
    
    for i in range(num_recommendations):
        col = columns[i % 4]
        with col:
            st.markdown(f"### {recommended_mangas_name[i]}")
            st.markdown(f"**Tags:** {recommended_mangas_tags[i]}")
            st.markdown(f"**Rating:** {recommended_mangas_rating[i]}")
    st.markdown("<br><br>", unsafe_allow_html=True)
