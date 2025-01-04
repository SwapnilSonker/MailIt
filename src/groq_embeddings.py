from groq import Groq
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv() #loading the env variable 

client = Groq(
    api_key = os.environ.get("GROQ_API_KEY")
)

def generate_vectors_from_resume(resume_pdf):
    data = PyPDFLoader(resume_pdf);
    dataloader = data.load()
    
    data_split = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap=200)
    split = data_split.split_documents(dataloader)

    embeddings = OllamaEmbeddings(
        model = "llama3.2",
    )
    
    store = Chroma.from_documents(documents=split, embedding=embeddings)
    retriever = store.as_retriever()
    
    return retriever

def formatted_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def groq_llm(question, context):
    formatted_prompt = f"Question: {question}\n\nContext: {context}"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": formatted_prompt}
        ],
        model="llama-3.2-1b-preview"  # Replace with the appropriate model name
    )
    
    response_content = chat_completion.choices[0].message.content
    return response_content

def generate_embeddings(resume_pdf,question):
    retriever = generate_vectors_from_resume(resume_pdf)
    retrieve_docs = retriever.invoke(question)
    formatted_context = formatted_docs(retrieve_docs)
    return groq_llm(question, formatted_context)



# if __name__ == "__main__":
#     result = generate_embeddings("swapnil_resume.pdf", "only skills in concise manner")
#     print("result ->",result)

    