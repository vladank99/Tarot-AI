import streamlit as st

st.set_page_config(
    page_title="welcome",
    page_icon="🔮",
)

st.write("# Welcome to Tarot AI project! 👋")

st.write('''
**Author:** Vladislav Ankushev   
''')

st.divider()

st.markdown(
    """
#### Main Idea
Create a bot for daily tarot card readings

#### Overview
The website includes three types of tarot bots:
""")

st.write()
st.page_link("pages/1_🤖_Prompt-based_Bot.py", label="Prompt-based Bot", icon="🤖")
st.write("This bot uses various prompting techniques to generate predictions: meta-prompting & prompt-chaining")

st.write()
st.page_link("pages/2_👾_Keyword-based_Bot.py", label="Keyword-based Bot", icon="👾")
st.write("This bot focuses on keywords taken from parsed tarot card meanings. It creates predictions based on the most common themes linked to each card")

st.write()
st.page_link("pages/3_⚙️_Summarization_Bot.py", label="Summarization Bot", icon="⚙️")
st.write("This bot generates summaries from parsed tarot card meanings. It combines various summaries for a single cart, creating a single & general interpretation")


st.markdown(
    """

#### Goal
The goal of the project is to offer a fun and unique experience for tarot fans

#### About
The page shows the process of creating the bot and highlights the differences between versions. It is not the final product for use

#### Winning Bot
Prompt-based or Summarization-based

#### Future Developments

- Create Hybrid version of Bot (Keyword & Summarization)

- Creating training and test datasets for keyword extraction and summarization tasks

- Building a larger database of parsed tarot card interpretations, categorized by different theme

- Create a back-end & deploy it as a Telegram App

- Make an API-calls cheaper
""")
