# Load environment variables
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_cohere import CohereEmbeddings, ChatCohere
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List
load_dotenv()
# Define Pydantic model for skills
class ResumeSkills(BaseModel):
    skills: List[str] = Field(description="List of skills extracted from the resume")
    
    def __str__(self):
        return ", ".join(self.skills)
    
    @classmethod
    def from_string(cls, skills_str: str):
        """Create a ResumeSkills instance from a comma-separated string"""
        skills = [skill.strip() for skill in skills_str.split(",") if skill.strip()]
        return cls(skills=skills)



def process_resume_file(resume):
    # Load and process the PDF
    loader = PyPDFLoader(resume)
    docs = loader.load()
    print(f"Loaded {len(docs)} pages from resume.pdf")

    # Split the document into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=10,
    )
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks")

    # Create embeddings and vector store
    embeddings = CohereEmbeddings(
        model="embed-english-v3.0",
    )
    vector_store = FAISS.from_documents(
        chunks,
        embeddings,
    )

    # Set up retriever
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

    # Define prompt template
    prompt = PromptTemplate(
        template="""
        You are a helpful assistant.
        You are given a question and a context.
        - If the context is not related to the question, reply exactly "I don't know".
        - If the context contains skills, extract **only** the skill names and output them as a comma-separated list.
        - Do **not** include any other words, explanations, or punctuation.

        Context:
        {context}
        """,
        input_variables=["context"],
    )

    # Extract skills function
    def extract_skills(question="what are the skills") -> ResumeSkills:
        # Retrieve relevant documents
        retrieved_docs = retriever.invoke(question)
        
        # Combine context from retrieved documents
        context_text = "\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Create prompt with context
        final_prompt = prompt.invoke({"context": context_text})
        
        # Get LLM response
        llm = ChatCohere(temperature=0)
        answer = llm.invoke(final_prompt)
        
        # Process the skills and return as Pydantic model
        return ResumeSkills.from_string(answer.content)

    # Run the extraction
    result = extract_skills()
    print("\nExtracted Skills:")
    print(result.skills)
    return result.skills
