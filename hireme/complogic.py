from django.shortcuts import render
import fitz
import ast
import google.generativeai as genai
from sklearn.metrics.pairwise import cosine_similarity
import string
import gensim.downloader as api
import numpy as np
# Create your views here.
word2vec_model = api.load("word2vec-google-news-300")
def pdfkey(pdf_path):
    doc = fitz.open(pdf_path)
    extracted_text = ""
    for page in doc:
        text = page.get_text()
        extracted_text += text
    doc.close()
    text = extracted_text
    api_key ="AIzaSyDyQJxvf9W3UBFVrueIBORd6wwFkwVyFGQ"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"FIND ALL THE  SKILLS , KEYWORDS IN ABOVE RESUME TEXT  {text} , THE OUTPUT SHOULD CONTAIN ONLY THE LIST OF SKILLS WITHOUT ANY OTHER WORDS THIS LIST  WILL BE STORING IN PYTHON LIST,LAST ELEMENT OF LIST  MUST CONTAIN THE TOTAL SUMMATION OF THE EXPIRIENCE GIVEN IN RESUME , JUST LIST NO OTHER CALCULATION JUST LIST AND VALES INSIDE IT(dont inlcude python code ''' or python name(python can be included in list if python in input text but ''' stricly never included)) ")
    #for chunk in response:
        #print(chunk)
    #text = response._result.candidates[0].content.parts[0].text
    
    r = (response.text.strip())
    #print(type(r))
    #print(r)
    r = ast.literal_eval(r)
    #print(type(r))
    #print(r[0])
    #print(r)
    return r

def jd_skills(text):
    #text = "We are seeking an experienced and detail-oriented Test Engineer to join our team. The ideal candidate will bring expertise in hydraulic and electrical testing, test stand fabrication, and data acquisition systems like LabVIEW and DasyLab. You will play a key role in conducting rigorous testing of mechanical and hydraulic components, ensuring adherence to FAA and military regulations, and driving high-quality standards in aerospace and defense projects."
    api_key ="AIzaSyDyQJxvf9W3UBFVrueIBORd6wwFkwVyFGQ"
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(f"FIND ALL THE  SKILLS , KEYWORDS IN ABOVE Job description TEXT  {text} , THE OUTPUT SHOULD BE LIST OF SKILLS WITHOUT ANY OTHER WORDS THIS LIST WILL BE STORING IN PYTHON LIST, STRICLTY NOTHING ELSE NO PYTHON CODE ''' or python name(python can be included in list if python in input text but ''' stricly never included)")
    #for chunk in response:
        #print(chunk)
    #text = response._result.candidates[0].content.parts[0].text
    r = (response.text.strip())
    #print(r) 
    r = ast.literal_eval(r)
    #print(type(r))
    #print(r[0])
    return r

def preprocess_text(text):
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.lower()
    tokens = text.split()
    return tokens

def get_word2vec_vector(tokens):
    # Get the word vectors for each token and calculate the average vector
    vectors = []
    for token in tokens:
        try:
            vectors.append(word2vec_model[token])  # Get the vector for each word
        except KeyError:
            # If word is not in the vocabulary, use a zero-vector
            vectors.append(np.zeros(word2vec_model.vector_size))
    
    # Average the vectors
    if len(vectors) == 0:
        return np.zeros(word2vec_model.vector_size)  # If no valid words, return zero vector
    return np.mean(vectors, axis=0)

def get_vec_res(pdf):
#skills_cand = pdfkey('./10030015.pdf')
#skills_jd = jd_skills()

    skills_cand = pdfkey(pdf)
#print(skills_cand, skills_jd)
    exp_year = skills_cand[-1]
    skills_cand.pop()

    skills_cand_tokens = preprocess_text(' '.join(skills_cand))
    skills_cand_vector = get_word2vec_vector(skills_cand_tokens)
    return skills_cand_vector


def get_vec_job(text):
    skills_jd = jd_skills(text)
    skills_jd_tokens = preprocess_text(' '.join(skills_jd))
# Convert the tokenized skills into word2vec vectors
    skills_jd_vector = get_word2vec_vector(skills_jd_tokens)
    return skills_jd_vector
#print(skills_cand_vector,skills_jd_vector)
# Compute the cosine similarity between the two skill vectors
#cosine_sim =  cosine_similarity([skills_cand_vector], [skills_jd_vector])

# Output the cosine similarity
#print("Cosine Similarity:", cosine_sim[0][0])


