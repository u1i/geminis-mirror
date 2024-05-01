import random
import requests
import os

import gradio as gr
from bs4 import BeautifulSoup
import google.generativeai as genai


def extract_text(url):
    # Fetch the content from URL
    response = requests.get(url)
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # Extract and keep h1, h2, h3 tags but remove other tags while keeping their content
    for tag in soup.find_all(True):
        if tag.name not in ['h1', 'h2', 'h3']:
            tag.unwrap()

    # Return the modified HTML as a string
    return str(soup)


def summarize_and_score_content(text):
    
    # Set up the model
    generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    ]

    system_instruction = f"""You are helping to make a piece of software smarter by summarizing and analyzing content.
    
    You are not directly engaging with a user, so there is no need to add greetings, apologies, or these things.
    Your specific task is to analyze text snippets gathered from a hackathon proposal, provide a summary and analysis in
    a structured format in HTML along with initial scoring.
    
    Scoring criteria:
    
    1: Freshness (How original/fresh is the idea) (from 1 to 10)
    2: Creativity (How much creativity does it display?) (from 1 to 10)
    3: Complexity (How complex is it, is it a Low code app?) (from 1 to 10)
    4: Details (How detailed is the description?) (from 1 to 10)
    5: Overall assessment: Your overall impression of the project where you include the details and reasoning behind your scoring.
    6: Improvements: Suggest a couple of improvements (elevator pitch, needs more details, the idea is too simple,
    not feasible, anything)
    
    The format of what you produce should be:
    Title of the app: try to find out what the title of the app is that was submitted to the hackathon.
    It could be near an HTML tag with id="app-title" but it does not have to necessarily.
    What does the app do: try to be as detailed as possible in the summary
    Elevator pitch: if you can find one, otherwise create a quick snappy elevator pitch and add (suggested) at the end
    Inspiration: try to find information about what inspired the app and provide a summary
    How was it built: provide details if you can find.
    Scoring: your assessment with scoring. Write the name of the criteria along with the score
    
    Important guidelines:
    o) You produce simple HTML output with <h2> <h3> tags and bullet points where needed.
    o) Do not add anything else.
    o) If you cannot find the information do not invent it just add <not_found> or <unable_to_assess>
    o) DO NOT say things like "Here is the summary in the requested format:" etc
    o) Your output will be read by a machine."""

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                generation_config=generation_config,
                                system_instruction=system_instruction,
                                safety_settings=safety_settings)

    prompt_parts = [text]

    response = model.generate_content(prompt_parts)
    return(response.text)

def chat_with_bot2(user_input, history):
    return "Dummy response :)"

def process_input(description, url):
    extracted_content = extract_text(url)
    assessment = summarize_and_score_content(extracted_content)
    return f"{assessment}"


api_key = os.getenv('GENAI_API_KEY')
genai.configure(api_key=api_key)

css="<style>footer {visibility: hidden}</style>"

with gr.Blocks(title="Gemini's Mirror", theme="gradio/monochrome") as app:
    gr.HTML(value=css)

    with gr.Tab("Hackathon Project"):
        gr.Markdown("### Input your scoring instructions and URL of the project")
        description = gr.Textbox(label="Scoring Criteria", value="""

    1: Freshness (How original/fresh is the idea) (from 1 to 10)
    2: Creativity (How much creativity does it display?) (from 1 to 10)
    3: Complexity (How complex is it, is it a Low code app?) (from 1 to 10)
    4: Details (How detailed is the description?) (from 1 to 10)
    5: Overall assessment: Your overall impression of the project where you include the details and reasoning behind your scoring.
    6: Improvements: Suggest a couple of improvements (elevator pitch, needs more details, the idea is too simple,
    not feasible, anything)                                 
            """, lines=4)
        url = gr.Textbox(label="Project URL")
        button = gr.Button("Submit")
        #output = gr.Textbox(label="Assessment", lines=4, interactive=False)
        output2 = gr.HTML(label="Assessment")


        #button.click(process_input, inputs=[description, url], outputs=output)
        button.click(process_input, inputs=[description, url], outputs=[output2])
    with gr.Tab("Chat"):
        # gr.ChatInterface(random_response,title="Let's talk about your proposal!")
        gr.ChatInterface(chat_with_bot2,title="Let's talk about your proposal!",
            description="",
            examples=["Ok let's start!"], retry_btn=None, undo_btn=None, clear_btn=None)
    
app.launch()

