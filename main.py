import os

os.environ['LANGCHAIN_TRACING_V2'] = ''
os.environ['LANGCHAIN_ENDPOINT'] = ''
os.environ['LANGCHAIN_API_KEY'] = ''

# API keys for LLM providers
os.environ['GEMINI_API_KEY'] = ''
os.environ['GEMINI_API_NAME'] = ''
os.environ['GEMINI_API_PROJECT_NAME'] = ''
os.environ['GEMINI_API_PROJECT_NUMBER'] = ''
os.environ['OPENAI_API_KEY'] = ''

print(1)