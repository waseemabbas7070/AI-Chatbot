from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def pdf_loader(file_path):
    loader = PyPDFLoader(file_path)
    extracted_text = loader.load()
    return extracted_text
def splitter(extracted_text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500,chunk_overlap  = 150)
    text_chunks = text_splitter.split_documents(extracted_text)
    return text_chunks