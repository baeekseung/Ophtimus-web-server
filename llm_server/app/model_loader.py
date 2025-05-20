from transformers import AutoTokenizer
from langchain_teddynote.prompts import load_prompt
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFacePipeline
from langchain_huggingface import ChatHuggingFace
from langchain_openai import ChatOpenAI

def load_model(task: str):
    if task == "Ophtimus Diagnosis":
        prompt = load_prompt("app/prompts/Ophtimus_diagnosis.yaml", encoding="utf-8")
        
        model = ChatOpenAI(model_name="gpt-4o", temperature= 0.9)

    elif task == "Ophtimus Q&A":
        prompt = load_prompt("app/prompts/Ophtimus_diagnosis.yaml", encoding="utf-8")
        
        model = ChatOpenAI(model_name="gpt-4o", temperature= 0.9)

    return prompt | model | StrOutputParser()
