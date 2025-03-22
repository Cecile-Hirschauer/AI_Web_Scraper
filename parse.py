"""Module for parsing content using Ollama LLM with LangChain."""

from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

TEMPLATE = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

prompt = ChatPromptTemplate.from_template(TEMPLATE)

model = OllamaLLM(model="llama3")

def parse_with_ollama(dom_chunks, parse_description):
    """Parse content using Ollama LLM to extract specific information based on description."""
    chain_prompt = ChatPromptTemplate.from_template(TEMPLATE)
    chain = chain_prompt | model

    parsed_results = []

    for chunk_index, chunk in enumerate(dom_chunks, start=1):
        response = chain.invoke({"dom_content": chunk, "parse_description": parse_description})
        parsed_results.append(response)
        print(f"Parsed batch {chunk_index} of {len(dom_chunks)}")

    return "\n".join(parsed_results)
