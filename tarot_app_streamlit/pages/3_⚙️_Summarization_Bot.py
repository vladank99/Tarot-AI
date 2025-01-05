import streamlit as st
from openai import OpenAI
import random
import pandas as pd

st.set_page_config(
    page_title="summarization_based",
    page_icon="🔮",
)

# Get a list of all tarot cards
data = pd.read_csv('final_df.csv')
list_tarot = data['card'].unique().tolist()

# Get summaries
summaries = pd.read_csv('summary_df_tarot.csv')

# Edit topic values
summaries['topic'] = summaries['topic'].replace({
    'general': 'Other',
    'career': 'Career',
    'finance': 'Finances',
    'love': 'Love'
})

# Extract summaries
def get_card_summaries(summaries_df, cards, topic):
    card_summaries = {}
    for card in cards:
        # Filter summaries by card and topic
        filtered_summaries= summaries_df[
            (summaries_df['card'] == card) & (summaries_df['topic'] == topic)
        ]['summary'].tolist()
        card_summaries[card] = filtered_summaries
    return card_summaries

# GPT call
api_key_stream = st.secrets["api_key"]
client = OpenAI(api_key=api_key_stream)

def get_model_response(messages, model="gpt-4o"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

# Generate predictions 
def generate_prediction(user_input):

    # Filter summaries for the selected cards and topic
    card_summaries = get_card_summaries(summaries, 
                                       [user_input['card_1'], user_input['card_2'], user_input['card_3']], 
                                       user_input['topic'])
    
    # First meta-prompt: role and general rules
    meta_prompt_1 = """
    
    You are an expert in Tarot card reading.

    Your task is to predict the future answering to a query from the user.

    **Rules for writing predictions:**
    1. Do not insult or demean the user.
    2. Predictions (answers to the user's query) can be both positive and negative.
    3. It's important for the user to develop self-love and inner strength.
    4. If appropriate, offer actionable recommendations that can help users with their queries.
    5. Show empathy in the communication with the user.
    6. If the query is unethical, gently explain why it's not acceptable and offer an alternative.

    Remember: you are not only an interpreter of the cards but also a guide who helps people find meaning in their queries.
    """

    # Validation prompt 
    validation_prompt = f"""
    Before making a prediction, ensure the user's query is clear and makes sense.
    
    User input:
    - Story: {user_input['story']}
    - Topic: {user_input['topic']}
    - Question: {user_input['question']}

    Response logic:
    - If any of the following issues are present:
    1. The query is unclear.
    2. The story is too generic.
    3. The question does not align with the story theme 
    Respond with: "I cannot make a prediction based on your query. Please revise your question, story or topic."

    - Otherwise, respond with: "The query is clear."
    """

    validation_response = get_model_response([
        {"role": "system", "content": meta_prompt_1},
        {"role": "user", "content": validation_prompt}
    ])

    if "cannot make a prediction" in validation_response:
        return validation_response


    # Second prompt: create interpretations, based on summaries
    meta_prompt_2 = f"""
    You are provided with the following inputs:
    - Three Tarot cards: Each card includes its name and corresponding summaries of their interpretations
    - Overall theme: A central topic that guides the interpretation
    - User input: The user’s story and their specific question

    **Your task**:
    Use the summaries for each card as a foundational points to craft a cohesive story based on the overall theme and user’s story & question 

    Tarot cards input data:
    Name – Card 1: {user_input['card_1']}
    Keywords – Card 1: {', '.join(card_summaries[user_input['card_1']])}

    Name - Card 2: {user_input['card_2']}
    Keywords – Card 2: {', '.join(card_summaries[user_input['card_2']])}

    Name – Card 3: {user_input['card_3']}
    Keywords – Card 3: {', '.join(card_summaries[user_input['card_3']])}

    Prediction theme: {user_input['topic']}

    User's input data:
    - Story: {user_input['story']}
    - Question: {user_input['question']}

    Writing format:
    Card 1: (interpretation of the first card)
    Card 2: (interpretation of the second card)
    Card 3: (interpretation of the third card)
    """

    preliminary_prediction = get_model_response([
        {"role": "system", "content": meta_prompt_1},
        {"role": "user", "content": meta_prompt_2}
    ])

    # Third prompt: refining structure
    meta_prompt_3 = f"""
    You will be provided with a preliminary prediction for 3 Tarot cards and several rules for writing it.

    **Your task**:
    - Edit the *preliminary prediction* according to the structure, format, and style
    - Use the input data to edit the *preliminary prediction* (if necessary)
    
    Preliminary prediction:
    {preliminary_prediction}

    Input data:
    - Theme: {user_input['topic']}
    - Story: {user_input['story']}
    - Question: {user_input['question']}
    - Card 1: {user_input['card_1']}
    - Card 2: {user_input['card_2']}
    - Card 3: {user_input['card_3']}

    Structure of the prediction: 
    - Beginning: feedback on the user's question/story (this can include a greeting, reaction to the story/question, reflecting key points of the query).
    - Card №1: On the first line – '**Card №1: card name**'. On the next line: interpretation of the first card.
    - Card №2: On the first line – '**Card №2: card name**'. On the next line: interpretation of the second card.
    - Card №3: On the first line – '**Card №3: card name**'. On the next line: interpretation of the third card.
    - End: a general conclusion for the prediction (this can include general advice for the situation, closing remarks, or feedback on the prediction).

    Prediction format:
    - Use details and metaphors to create an atmosphere.
    - The text should be engaging, vivid, and immersive.
    - It should not be a poem, fairy tale, or fable.

    Prediction text style:
    - Divide the prediction into paragraphs based on meaning.
    - Avoid spelling or grammar mistakes.    
    """

    # Get the final prediction
    final_prediction = get_model_response([
        {"role": "system", "content": meta_prompt_1},
        {"role": "system", "content": meta_prompt_2},
        {"role": "user", "content": meta_prompt_3}
    ])

    return final_prediction

# Function to draw random Tarot cards
def draw_tarot_cards(list_tarot, num_cards=3):
    drawn_cards = random.sample(list_tarot, num_cards)
    return drawn_cards

# Streamlit application
st.title("⚙️ Summarization Bot")

# Initialize session state for storing user input & prediction
if "last_input" not in st.session_state:
    st.session_state.last_input = None  # previous input
if "last_prediction" not in st.session_state:
    st.session_state.last_prediction = None  # previous prediction
if "drawn_cards" not in st.session_state:
    st.session_state.drawn_cards = None  # drawn cards

st.divider()
st.subheader("✍️ Description")
st.markdown('''
This is the third version of a tarot card prediction bot, based on prompts & summaries, extracted from various parsed tarot interpretations \n
The summaries were validated using following **methods** – self-consistency & expert assessment     
            
**Techniques used**: 
- meta-prompting
- prompt-chaining 
- summary generation
- self-consistency
- expert assessment      
            
**Version**: Summarization-based 
''')

st.divider()

st.subheader("🧙 Prediction")

# Step 1: Select a topic
topic = st.selectbox("Select a topic", ["Career", "Finances", "Love", "Other"])

# Step 2: Provide a story
story = st.text_area('Your story:', placeholder="Tell us more about your situation here")

# Step 3: Ask a question
question = st.text_area('Your question:',placeholder="Ask your main question here")

st.text("")

# Prediction button
if st.button("✨ Get Prediction"):
    # Gather input data
    current_input_no_cards = {
        "topic": topic,
        "story": story,
        "question": question
    }

    # First card draw case:
    if "last_input_no_cards" not in st.session_state:
        st.session_state.last_input_no_cards = current_input_no_cards
        st.session_state.drawn_cards = draw_tarot_cards(list_tarot)

        full_input_for_prediction = {
            **current_input_no_cards,
            "card_1": st.session_state.drawn_cards[0],
            "card_2": st.session_state.drawn_cards[1],
            "card_3": st.session_state.drawn_cards[2]
        }

        with st.spinner("Generating your prediction..."):
            st.session_state.last_prediction = generate_prediction(full_input_for_prediction)

        st.chat_message("assistant").write(st.session_state.last_prediction)

    else:

        # 2nd ... N-th attempts to draw a card with different input:
        if current_input_no_cards != st.session_state.last_input_no_cards:
            st.session_state.last_input_no_cards = current_input_no_cards
            st.session_state.drawn_cards = draw_tarot_cards(list_tarot)

            full_input_for_prediction = {
                **current_input_no_cards,
                "card_1": st.session_state.drawn_cards[0],
                "card_2": st.session_state.drawn_cards[1],
                "card_3": st.session_state.drawn_cards[2]
            }

            with st.spinner("Generating your prediction..."):
                st.session_state.last_prediction = generate_prediction(full_input_for_prediction)

            st.chat_message("assistant").write(st.session_state.last_prediction)
        else:

            # 2nd ... N-th attempts to draw a card with the same input:
            st.chat_message("assistant").write("Please update the topic, story, or question.")
            st.chat_message("assistant").write(st.session_state.last_prediction)