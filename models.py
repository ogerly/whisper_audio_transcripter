MODELS = {
    "Mistral-Nemo": {
        "api": "huggingface",
        "model_id": "mistralai/Mistral-Nemo-Instruct-2407"
    },
    "gemma-2-2b-it": {
        "api": "huggingface",
        "model_id": "google/gemma-2-2b-it"
    },
    "Phi-3-mini": {
        "api": "huggingface",
        "model_id": "microsoft/Phi-3-mini-4k-instruct"
    },
    "Qwen2.5-7B": {
        "api": "huggingface",
        "model_id": "Qwen/Qwen2.5-7B-Instruct"
    },
    "Llama-3.1-Nemotron": {
        "api": "huggingface",
        "model_id": "nvidia/Llama-3.1-Nemotron-70B-Instruct"
    },
    "flan-t5": {
        "api": "huggingface",
        "model_id": "google/flan-t5-large"
    },
    "gpt-3.5-turbo": {
        "api": "openai",
        "model_id": "gpt-3.5-turbo"
    },
    # Fügen Sie weitere Modelle nach Bedarf hinzu
}


PROMPT_TEMPLATE = '''
Fasse das folgende Meeting-Transkript in einem strukturierten Protokoll zusammen. Verwende dabei klare Überschriften und Aufzählungspunkte zur Strukturierung. 
erfasse alle:
- getroffenen aufgaben. 
- erfasse alle aufgetretenen problemen. 
- erfasse alle getroffenen entscheidungen. 
- erfasse alle getroffenen lösungen zu problemen.  
- erfasse alle termine. 
- erfasse alle anwesenden. 

Transkript:
{transcript}
'''

