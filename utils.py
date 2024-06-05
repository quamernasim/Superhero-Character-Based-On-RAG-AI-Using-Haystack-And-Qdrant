import yaml

from haystack import Pipeline
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.builders import PromptBuilder
from haystack.components.others import Multiplexer

def get_superhero_names(superhero, config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    superhero_synonym = config['SUPERHERO_SYNONYMS'][superhero][0]
    superhero_names = [superhero.upper(), superhero_synonym.upper(), superhero_synonym.replace(' ', '-').upper()]
    superhero_names = list(set(superhero_names))
    return superhero_names

def load_document_store(vector_store_path, superhero, embed_dim):
    document_store = QdrantDocumentStore(
        path=vector_store_path,
        index=superhero,
        embedding_dim=embed_dim,
    )
    return document_store

def build_prompt():
    prompt = """
    You are a helpful AI assistant that mimics the tone of the specified character based on provided context documents. Use the context to capture and replicate the character's tone accurately.

    You will be given a set of CONTEXT documents, which you should use to understand and replicate the character's tone in your response. The context should primarily inform the tone rather than the content of your answer. You may answer questions without the context if it is not necessary, but always ensure your tone matches that of the character.

    Respond without prefacing with phrases like "Based on the context..." or "I think...".

    ******************************************
    Context:
    {% for document in documents %}
    {{ document.content }}
    ------------------------------------------
    {% endfor %}
    ******************************************
    Copy the tone of these charachters : {{ superhero_names }} dialogue and answer the following question:
    ******************************************
    Question: {{ query }}
    ******************************************
    Answer:
    """

    # Define the prompt builder
    prompt_builder = PromptBuilder(template=prompt)
    return prompt_builder

def build_rag_pipeline(embedder, retriever, prompt_builder, generator):
    rag = Pipeline()

    rag.add_component(instance=Multiplexer(str), name="multiplexer")

    rag.add_component("embedder", embedder)
    rag.add_component("retriever", retriever)
    rag.add_component("prompt", prompt_builder)
    rag.add_component("llm", generator)

    rag.connect("multiplexer.value", "embedder.text")
    rag.connect("multiplexer.value", "prompt.query")

    rag.connect("embedder.embedding", "retriever.query_embedding")
    rag.connect("retriever.documents", "prompt.documents")
    rag.connect("prompt.prompt", "llm")

    return rag