from os.path import join as pjoin
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever
from haystack.components.generators import HuggingFaceTGIGenerator
from haystack_integrations.components.embedders.fastembed import FastembedTextEmbedder

from utils import get_superhero_names, load_document_store, build_prompt, build_rag_pipeline


root = '.'
data_folder = 'data'
script_folder = 'scripts'
dialogue_folder = 'dialogues'
config_file = 'config.yaml'
embed_dim = 384
vector_store_name = 'QDRANT_VECTOR_DATABASE'
vector_store_path = pjoin(root, vector_store_name)
embedding_model = 'BAAI/bge-small-en-v1.5'
embedding_model = 'BAAI/bge-small-en-v1.5'
llm_model = "meta-llama/Meta-Llama-3-8B-Instruct"
max_new_tokens = 250
number_of_documents_to_retrieve = 5

config_path = pjoin(root, config_file)

def get_response(question, superhero):
    superhero_names = get_superhero_names(superhero, config_path)
    document_store = load_document_store(vector_store_path, superhero, embed_dim)
    prompt_builder = build_prompt()

    generator = HuggingFaceTGIGenerator(model=llm_model, generation_kwargs={"max_new_tokens": max_new_tokens})
    retriever = QdrantEmbeddingRetriever(document_store=document_store, top_k=number_of_documents_to_retrieve)
    embedder = FastembedTextEmbedder(model = embedding_model)

    rag = build_rag_pipeline(embedder, retriever, prompt_builder, generator)

    pipeline_input = {
        "multiplexer": {
            "value": question,
        },
        "prompt": {
            "superhero_names": superhero_names
        }
    }

    result = rag.run(pipeline_input)
    response = result['llm']['replies'][0]

    return response