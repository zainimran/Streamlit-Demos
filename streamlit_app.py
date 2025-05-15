import streamlit as st

st.title("My First Streamlit App")
st.write("Hello, Streamlit World!")
name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}!")

if st.button("Click me!", icon=":material/thumb_up:"):
    st.write("I was clicked!")
else:
    st.write("waiting to be clicked")

st.checkbox("Check me")