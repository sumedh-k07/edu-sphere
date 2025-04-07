import streamlit as st

# Custom CSS for a brown & beige theme
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #F5F5DC; /* Warm Beige */
        }
        .title-container {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #E0C9A6, #D7B899); /* Beige Blend */
            color: #5D4037; /* Deep Brown */
            border-radius: 12px;
            margin-bottom: 20px;
        }
        .title-container h1 {
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .tagline {
            font-size: 18px;
            font-style: italic;
            color: #795548; /* Medium Brown */
        }
        .description {
            font-size: 16px;
            color: #5D4037;
            margin-top: 10px;
        }
        .selection-container {
            display: flex;
            justify-content: center;
            gap: 50px;
            margin-top: 30px;
        }
        .option-card {
            text-align: center;
            padding: 20px;
            width: 320px;
            background: #FAF3E0; /* Off-white for warmth */
            border: 2px solid #8D6E63; /* Chocolate Brown */
            border-radius: 12px;
            box-shadow: 2px 2px 15px rgba(0, 0, 0, 0.1);
            transition: 0.3s;
            cursor: pointer;
        }
        .option-card:hover {
            box-shadow: 2px 2px 20px rgba(0, 0, 0, 0.2);
            transform: scale(1.05);
        }
        .btn {
            padding: 12px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            width: 90%;
            font-weight: bold;
            transition: 0.3s;
        }
        .btn-mindmap {
            background-color: #8D6E63; /* Chocolate Brown */
            color: white;
        }
        .btn-qna {
            background-color: #A1887F; /* Dark Beige */
            color: white;
        }
        .btn:hover {
            opacity: 0.85;
        }
    </style>
""", unsafe_allow_html=True)

# Set session state for navigation
if "page" not in st.session_state:
    st.session_state.page = "home"

# Function to switch pages
def navigate_to(page):
    st.session_state.page = page

# Title & Tagline
st.markdown("""
    <div class='title-container'>
        <h1>📜 EDU-SPHERE</h1>
        <p class='tagline'>Your One-Stop Solution for Exam Preparation</p>
        <p class='description'>Convert your study materials into structured mind maps and AI-generated Q&As. 
        Study smarter, revise faster, and excel in your exams!</p>
    </div>
""", unsafe_allow_html=True)

# Selection Section
st.markdown("<div class='selection-container'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    if st.button("🧠 Generate Mind Map", key="mindmap_btn", help="Create a structured mind map from your notes"):
        navigate_to("mindmap")

with col2:
    if st.button("❓ Generate Q&A", key="qna_btn", help="Generate exam questions & answers from documents"):
        navigate_to("qna")

st.markdown("</div>", unsafe_allow_html=True)

# Navigate to selected page
if st.session_state.page == "mindmap":
    import app_mindmap
    app_mindmap.run()

elif st.session_state.page == "qna":
    import app_qna
    app_qna.run()
