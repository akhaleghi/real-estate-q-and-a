import pandas as pd
import tiktoken
import openai
import numpy as np
from openai.embeddings_utils import distances_from_embeddings, cosine_similarity
from ast import literal_eval

max_tokens = 500


# Function to split the text into chunks of a maximum number of tokens
def split_into_many(text, max_tokens=max_tokens):
    # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
    tokenizer = tiktoken.get_encoding("cl100k_base")

    # Split the text into sentences
    sentences = text.split('. ')

    # Get the number of tokens for each sentence
    n_tokens = [len(tokenizer.encode(" " + sentence)) for sentence in sentences]

    chunks = []
    tokens_so_far = 0
    chunk = []

    # Loop through the sentences and tokens joined together in a tuple
    for sentence, token in zip(sentences, n_tokens):

        # If the number of tokens so far plus the number of tokens in the current sentence is greater
        # than the max number of tokens, then add the chunk to the list of chunks and reset
        # the chunk and tokens so far
        if tokens_so_far + token > max_tokens:
            chunks.append(". ".join(chunk) + ".")
            chunk = []
            tokens_so_far = 0

        # If the number of tokens in the current sentence is greater than the max number of
        # tokens, go to the next sentence
        if token > max_tokens:
            continue

        # Otherwise, add the sentence to the chunk and add the number of tokens to the total
        chunk.append(sentence)
        tokens_so_far += token + 1

    # Add the last chunk to the list of chunks
    if chunk:
        chunks.append(". ".join(chunk) + ".")

    return chunks


def tokenizer():
    # Load the cl100k_base tokenizer which is designed to work with the ada-002 model
    tokenizer = tiktoken.get_encoding("cl100k_base")

    df = pd.read_csv('processed/scraped.csv', index_col=0)

    # Assuming the 'text' column might have non-string values, convert them to strings
    df['text'] = df['text'].astype(str)
    df.columns = ['title', 'text']

    # Tokenize the text and save the number of tokens to a new column
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))

    print(df.head())
    print(df.shape[0])

    # Visualize the distribution of the number of tokens per row using a histogram
    # df.n_tokens.hist()

    shortened = []

    # Loop through the dataframe
    for row in df.iterrows():

        # If the text is None, go to the next row
        if row[1]['text'] is None:
            continue

        # If the number of tokens is greater than the max number of tokens, split the text into chunks
        if row[1]['n_tokens'] > max_tokens:
            shortened += split_into_many(row[1]['text'])

        # Otherwise, add the text to the list of shortened texts
        else:
            shortened.append(row[1]['text'])

    df = pd.DataFrame(shortened, columns=['text'])
    df['n_tokens'] = df.text.apply(lambda x: len(tokenizer.encode(x)))
    print(df.head())
    print(df.shape[0]*df['n_tokens'].sum())



    # Note that you may run into rate limit issues depending on how many files you try to embed
    # Please check out rate limit guidelines to learn more on how to handle this: https://platform.openai.com/docs/guides/rate-limits
    # You can set your API key in code using 'openai.api_key = <API-KEY>', or you can set the environment variable OPENAI_API_KEY=<API-KEY>).
    # If your API key is stored in a file, you can point the openai module at it with 'openai.api_key_path = <PATH>'.
    # You can generate API keys in the OpenAI web interface. See https://platform.openai.com/account/api-keys for details.
    # Embedding this data would cost ~$365

    df['embeddings'] = df.text.apply(
        lambda x: openai.Embedding.create(input=x, engine='text-embedding-ada-002')['data'][0]['embedding'])
    df.to_csv('processed/embeddings.csv')

    df = pd.read_csv('processed/embeddings.csv', index_col=0)
    df['embeddings'] = df['embeddings'].apply(literal_eval).apply(np.array)

    return df