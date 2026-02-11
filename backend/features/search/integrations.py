from functools import lru_cache,cache

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from .models import SearchResult, CypherQuery
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
load_dotenv()


async def text_to_cypher(text: str) -> str:
    """Convert a text query to a Cypher query.

    You should use an LangChain LLM using 'with_structured_output' to generate the Cypher query.
    Reference the docs here: https://docs.langchain.com/oss/python/langchain/structured-output#:~:text=LangChain%20automatically%20uses%20ProviderStrategy%20when%20you%20pass%20a%20schema%20type%20directly%20to%20create_agent.response_format%20and%20the%20model%20supports%20native%20structured%20output%3A

    Assume the knowledge graph has the following ontology:
    - Entities:
     - Disease
     - Symptom
     - Drug
     - Patient
    - Relationships:
     - TREATS
     - CAUSES
     - EXPERIENCING
     - SUFFERING_FROM

    You should have the model construct a Cypher query via a structured output (using JSON schema or
    Pydantic BaseModels) that can be used to query the system. If you have an API key, you may use it -
    otherwise, simply construct the LLM & assume that the the API key will be populated later.
    """
    # TODO - Convert text to Cypher query
    llm_text = ChatOpenAI(
            openai_api_key=os.getenv('API_KEY'),#"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",
            base_url="https://openrouter.ai/api/v1",
            model="arcee-ai/trinity-large-preview:free",
        )
        
    #question = "What is the capital of France?"
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system","""You are an expert at converting natural language queries into Cypher queries for a medical knowledge graph.
            The knowledge graph has the following ontology:
                - Entities (nodes):
                - Disease: represents medical conditions
                - Symptom: represents symptoms or signs
                - Drug: represents medications
                - Patient: represents patients
  
            - Relationships:
                - (Drug)-[:TREATS]->(Disease): a drug treats a disease
                - (Disease)-[:CAUSES]->(Symptom): a disease causes a symptom
                - (Patient)-[:EXPERIENCING]->(Symptom): a patient is experiencing a symptom
                - (Patient)-[:SUFFERING_FROM]->(Disease): a patient has a disease

            Convert the user's natural language query into a structured Cypher query.

            Examples:
                - "What drugs treat diabetes?" → MATCH (d:Drug)-[:TREATS]->(disease:Disease) WHERE disease.name = 'diabetes' RETURN d.name
                - "What are symptoms of flu?" → MATCH (disease:Disease)-[:CAUSES]->(s:Symptom) WHERE disease.name = 'flu' RETURN s.name
                - "Patients with headache" → MATCH (p:Patient)-[:EXPERIENCING]->(s:Symptom) WHERE s.name = 'headache' RETURN p.name
             """),
        ("human", f"Convert this to a Cypher query: {text}")
    ]
    )

    try:
        structured_llm = llm_text.with_structured_output(CypherQuery)
        
        cypher_query: CypherQuery = structured_llm.invoke(prompt.format(question=text))
        
        return str(cypher_query)
    except Exception as e:
        print(f"Error generating Cypher query: {str(e)}")
        return "MATCH (n) RETURN n LIMIT 5"



def search_knowledgegraph(cypher_query: str) -> list[SearchResult]:
    """This is a mock function that will search the knowledge graph using a cypher query."""
    return [
        SearchResult(
            document=Document(page_content=cypher_query,
                                metadata={"id": "mock_id","title": "Mock Cypher Query"}), score=0.9, reason="test"
        )
    ]

@lru_cache
def load_FAISS(doc_contents: tuple[str, ...]) -> FAISS:
    """Create and return a FAISS vector store from the DOCUMENTS list."""
    # TODO
    documents = [Document(page_content=content) for content in doc_contents]
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store



async def search_documents(query: str, documents: list[Document]) -> list[SearchResult]:
    """Using the FAISS vector store, search for the query and return a list of SearchResults.

    After searching FAISS, you should rerank all the remaining results using your custom 'rerank_result'
    function, and removing bad results. You may add args/kwargs as needed.
    """
    #document_tuple = tuple(documents)
    # - TODO
    # 1) load the FAISS store
    #vector_store = load_FAISS.__wrapped__(documents)
    doc_contents = tuple(doc.page_content for doc in documents)
    
    vector_store = load_FAISS(doc_contents)
    
    for i, doc in enumerate(documents):
        if i < len(vector_store.docstore._dict):
            doc_id = list(vector_store.docstore._dict.keys())[i]
            vector_store.docstore._dict[doc_id] = doc
    
    # 2) convert the query to Cypher
    cypher_query = await text_to_cypher(query)
    
    # 3) Search for the query on the FAISS store
    faiss_results = vector_store.similarity_search_with_score(query, k=10)
    
    # Convert to SearchResult objects
    sim_search_results = [
        SearchResult(document=doc, score=1/(1+score), reason="vector similarity")  # FAISS returns distance, convert to similarity
        for doc, score in faiss_results
    ]

    # 4) Search for the cypher query on the knowledgebase
    kg_results = search_knowledgegraph(cypher_query)
    
    # Combine results
    combined_results = sim_search_results + kg_results
    
    # Sort by score (highest first)
    combined_results.sort(key=lambda x: x.score, reverse=True)
    
    return combined_results
    
