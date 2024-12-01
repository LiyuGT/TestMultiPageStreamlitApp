import streamlit as st
from openai import OpenAI
from PIL import Image
import io

# Define the classify_comment function before calling it
def classify_comment(comment, category, client):
    if not client:
        return "No client initialized", False, False
    
    prompt = (
        f"As a TikTok comment classifier, classify the comment as 'good' or 'bad' "
        f"specifically in relation to '{category}'. "
        f"Comment: '{comment}'\n\n"
        "Classification and Reason:\n"
        "Is this comment related to the category? (Yes/No):"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    classification_and_reason = response.choices[0].message.content.strip()
    is_bad = "bad" in classification_and_reason.lower()
    related_to_category = "yes" in classification_and_reason.lower().split("is this comment related to the category?")[-1].strip()
    
    return classification_and_reason, is_bad, related_to_category

# Initialize session state variables
if "archive_mode" not in st.session_state:
    st.session_state["archive_mode"] = "Archive ALL bad comments"

if "custom_category" not in st.session_state:
    st.session_state["custom_category"] = "body"

if "uploaded_image" not in st.session_state:
    st.session_state["uploaded_image"] = None

def main_page(client):
    st.title("📸 Social Media Post")
    
    uploaded_image = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])

    if uploaded_image:
        st.session_state["uploaded_image"] = uploaded_image
    
    if st.session_state["uploaded_image"]:
        image_bytes = st.session_state["uploaded_image"].getvalue()
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, caption="Uploaded Social Media Post")
        
    st.write(f"Current Archiving Mode: {st.session_state['archive_mode']}")

    # Initialize comments if not done already
    if "comments" not in st.session_state:
        st.session_state["comments"] = [
            "Great post!", 
            "Your makeup looks terrible.", 
            "Amazing style!", 
            "Not your best look."
        ]

    # Initialize the input if not set
    if "new_comment" not in st.session_state:
        st.session_state["new_comment"] = ""

    custom_comment = st.text_input("Add your own comment to classify:", key="new_comment")
    
    if st.button("Post Comment"):
        if custom_comment.strip():  # Ensure non-empty comment
            st.session_state["comments"].append(custom_comment.strip())
            st.session_state["new_comment"] = ""  # Clear input
            st.experimental_rerun()  # Rerun the script to clear the input
    
    for comment in st.session_state["comments"]:
        if client:
            classification, is_bad, _ = classify_comment(comment, "general", client)
            if is_bad:
                st.error(f"🚫 Comment Archived: {comment}")
            else:
                st.success(f"✅ Comment Kept: {comment}")
        else:
            st.warning("No OpenAI client available.")


def settings_page():
    st.title("⚙️ Settings")
    st.write("Modify your app settings here.")
    
    archive_mode = st.radio(
        "Select your archiving preference:",
        ["Archive ALL bad comments", "Keep ALL Comments", "Customize"],
        index=["Archive ALL bad comments", "Keep ALL Comments", "Customize"].index(st.session_state["archive_mode"]),
    )
    
    st.session_state["archive_mode"] = archive_mode
    
    if archive_mode == "Customize":
        category = st.selectbox(
            "Select the type of comments to archive:",
            options=["Body", "Makeup", "Personality", "Fashion", "Performance"],
        ).lower()
        st.session_state["custom_category"] = category
    
    st.write(f"Current selection: {st.session_state['archive_mode']}")
    if archive_mode == "Customize":
        st.write(f"Custom Category: {st.session_state['custom_category']}")
    st.info("Return to the main page to see how settings are applied.")

# Page navigation using sidebar
page = st.sidebar.selectbox("Navigate", ["Home", "Settings"])

# OpenAI API Key Section
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
client = None
if openai_api_key:
    try:
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        st.sidebar.error(f"Error initializing OpenAI client: {e}")

if page == "Home":
    main_page(client)
elif page == "Settings":
    settings_page()
