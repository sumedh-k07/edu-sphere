import streamlit as st
import io
from nlp_logic import scrape_data, clean_text, create_keywords_from_text, generate_summary, get_mindmap

def run():
    st.title("🧠 NLP-Based Mind Map Generator")
    st.markdown("This application generates a mind map based on your input text. You can either upload a text file or provide a URL.")

    input_method = st.radio("Select Input Method:", ["Upload Text File", "Enter URL"])

    text = ""
    if input_method == "Upload Text File":
        uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
        if uploaded_file is not None:
            text = uploaded_file.read().decode("utf-8")
    elif input_method == "Enter URL":
        url_input = st.text_input("Enter a URL")
        if url_input:
            with st.spinner("Scraping text from URL..."):
                text = scrape_data(url_input)

    if text:
        st.session_state["input_text"] = text

    if "input_text" in st.session_state:
        st.markdown("### Original Text Preview")
        st.write(st.session_state["input_text"][:1000] + "..." if len(st.session_state["input_text"]) > 1000 else st.session_state["input_text"])

        if st.button("Generate Mind Map"):
            with st.spinner("Processing text and generating mind map..."):
                cleaned_text = clean_text(st.session_state["input_text"])
                summary = generate_summary(cleaned_text, top_n=40)
                keywords, topics = create_keywords_from_text(cleaned_text, max_nodes=5, sentence_group=4)
                fig = get_mindmap(keywords, topics)

            st.markdown("### Summary")
            st.write(summary)

            st.markdown("### Mind Map")
            st.pyplot(fig)

            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format="png")
            img_buffer.seek(0)

            st.download_button(label="Download Mind Map", data=img_buffer, file_name="mind_map.png", mime="image/png")

if __name__ == "__main__":
    run()
