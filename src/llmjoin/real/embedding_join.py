'''
Created on Oct 16, 2024

@author: immanueltrummer
'''
import numpy as np
import time


def cosine_similarity(embedding_1, embedding_2):
    """ Calculate cosine similarity between embedding vectors.
    
    Args:
        embedding_1: first embedding vector.
        embedding_2: second embedding vector.
    
    Returns:
        similarity metric.
    """
    return np.dot(embedding_1, embedding_2) / (
        np.linalg.norm(embedding_1) * np.linalg.norm(embedding_2))


def embed(client, row):
    """ Generate embedding for input row.
    
    Args:
        client: OpenAI client.
        row: table row to embed.
    
    Returns:
        embedding vector, tokens read
    """
    text = row['text']
    text = text.replace('\n', ' ')
    response = client.embeddings.create(
        input=[text], model='text-embedding-3-small')
    embedding = response.data[0].embedding
    tokens_read = response.usage.prompt_tokens
    return embedding, tokens_read

    
def embedding_join(client, df1, df2, predicate, model):
    """ Perform tuple join.
    
    Args:
        client: OpenAI client.
        df1: first input table.
        df2: second input table.
        predicate: join predicate.
        model: name of OpenAI model.
    
    Returns:
        Tuple: statistics, join result.
    """
    results = []
    stats = []    

    embedding_row = []
    for _, row2 in df2.iterrows():
        start_s = time.time()
        embedding, tokens_read = embed(client, row2)
        embedding_row.append((embedding, row2))
        total_s = time.time() - start_s
        stats += [
            {'tokens_read':tokens_read, 
            'tokens_written':0,
            'seconds':total_s}]

    for _, row1 in df1.iterrows():
        embedding_1, tokens_read = embed(client, row1)
        start_s = time.time()
        embedding_row.sort(
            key=lambda embedding_2_tuple:cosine_similarity(
                embedding_1, embedding_2_tuple[0]), 
            reverse=True)
        
        row2 = embedding_row[0][1]
        tuple_1 = row1['text']
        tuple_2 = row2['text']
        results += [{'tuple1':tuple_1, 'tuple2':tuple_2}]
        
        total_s = time.time() - start_s
        stats += [
            {'tokens_read':tokens_read, 
            'tokens_written':0,
            'seconds':total_s}]

    return stats, results