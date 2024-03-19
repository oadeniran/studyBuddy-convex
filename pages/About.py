import streamlit as st

st.header("Study Buddy streamlit demo")

st.info("Refreshing pages clear the cache which implies a restart of authentication process. Please try not to refresh")

st.subheader("Study Buddy, as the name suggests, is a companion designed to aid in studying. Its key features include:" + 
             '''
- Chat Interface: Enables interaction with uploaded PDF study materials.
- Self-Evaluation: Offers objective and theoretical questions based on the material for self-assessment.
- Automatic Restoration: Restores previous conversations for seamless continuation of learning.
- Flashcards: Assists in retaining and recalling key concepts.''')