import os
import json 
import numpy as np 
import pandas as pd 

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain,SimpleSequentialChain
from langchain.callbacks import get_openai_callback
#---------------------------------------------------------------------------
import traceback
from dotenv import load_dotenv
import PyPDF2
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.agents import AgentType
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.memory import ConversationBufferMemory

import config


llm = ChatOpenAI(api_key=config.OPENAI_API_KEY,  model="gpt-3.5-turbo", temperature=1.2)


TEMPLATE = """
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions for {subject} students in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Ensure to make {number} MCQs
### Multiple Choice Questions : {subject}
"""


quiz_generation_prompt = PromptTemplate(
    input_variables=['text', 'number', 'subject', 'tone'],
    template= TEMPLATE
)
# input_variables - those are taken from users

quiz_chain = LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)


TEMPLATE2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz for {subject} students.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""



quiz_evaluation_prompt = PromptTemplate(
    input_variables=['subject', 'quiz'],
    template= TEMPLATE2
)
# input_variables - those are taken from users


review_chain = LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)



generate_evaluation_chain = SequentialChain(chains=[quiz_chain,review_chain],
                input_variables=['text', 'number', 'subject', 'tone'],
                output_variables=['quiz','review']
                )


#---------------------------------------FLASK APP---------------------------------------------------------
from flask import Flask, render_template, jsonify, request
import PyPDF2
app = Flask(__name__)

@app.route("/")
def Home_Page():
    return render_template("index.html")

@app.route("/mcq_generator", methods=['POST'])
def mcq_generator():
    if request.method=='POST':
        file = request.files['file']
        NUMBERS = int(request.form['NUMBERS'])
        SUBJECT = request.form['SUBJECT']
        TONE = request.form['TONE']

        if file.filename.endswith(".txt"):
            TEXT = file.read().decode('utf-8')

            with get_openai_callback() as cb:
                response = generate_evaluation_chain({
                    'text': TEXT,
                    'number': NUMBERS,
                    'subject': SUBJECT,
                    'tone': TONE ,
                })
        elif file.filename.endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(file)
            TEXT = ""
            for page in pdf_reader.pages: # 26 pages
                TEXT+= page.extract_text()

            with get_openai_callback() as cb:
                response = generate_evaluation_chain({
                    'text': TEXT,
                    'number': NUMBERS,
                    'subject': SUBJECT,
                    'tone': TONE ,
                })
            
        response = response['quiz'].split('\n')
    return render_template("result.html" ,result=response)


if __name__=="__main__":
    app.run(debug=True, port=config.PORT, host=config.HOST)


