import time

from AI import get_openai_client
from pinecone import Pinecone
from pinecone import ServerlessSpec
from tqdm.auto import tqdm

MODEL = "text-embedding-3-small"
index_name = 'semantic-search-openai'
spec = ServerlessSpec(cloud="aws", region="us-east-1")
INDEX_POPULATED = False


def get_pinecone_client():
    # Read PineCone API key from file
    with open("PINECONE_ACCESS_TOKEN", "r") as file:
        api_key = file.read().strip()

    client = Pinecone(api_key=api_key)
    return client


pinecone_client = get_pinecone_client()
openai_client = get_openai_client()


def get_embeds_len():
    res = openai_client.embeddings.create(
        input=[
            "Sample document text goes here",
            "there will be several phrases in each batch"
        ], model=MODEL
    )

    # we can extract embeddings to a list
    embeds = [record.embedding for record in res.data]

    return embeds[0]


def get_index():
    # check if index already exists (if shouldn't if this is your first run)
    if index_name not in pinecone_client.list_indexes().names():
        # if does not exist, create index
        pinecone_client.create_index(
            index_name,
            dimension=len(get_embeds_len()),  # dimensionality of text-embed-3-small
            metric='dotproduct',
            spec=spec
        )
        # wait for index to be initialized
        while not pinecone_client.describe_index(index_name).status['ready']:
            time.sleep(1)

    # connect to index
    index = pinecone_client.Index(index_name)
    time.sleep(1)
    # view index stats
    # index.describe_index_stats()

    return index


def populate_index(input_texts, index):
    if INDEX_POPULATED:
        print("index is already populated. If you wish to populate it anyway change INDEX_POPULATED to False and run "
              "again. Note that it will not empty the existing index!")
        return

    print('Populating the index')
    batch_size = 32  # process everything in batches of 32
    for i in tqdm(range(0, len(input_texts), batch_size)):
        # set end position of batch
        i_end = min(i + batch_size, len(input_texts))
        # get batch of lines and IDs
        lines_batch = input_texts[i: i + batch_size]
        ids_batch = [str(n) for n in range(i, i_end)]
        # create embeddings
        res = openai_client.embeddings.create(input=map(lambda pair: pair[1], lines_batch), model=MODEL)
        embeds = [record.embedding for record in res.data]
        # prep metadata and upsert batch
        meta = [{'drug': line[0], 'text': line[1]} for line in lines_batch]
        to_upsert = zip(ids_batch, embeds, meta)
        # upsert to Pinecone
        index.upsert(vectors=list(to_upsert))


def query_index(query, index):
    xq = openai_client.embeddings.create(input=query, model=MODEL).data[0].embedding
    res = index.query(vector=[xq], top_k=2, include_metadata=True)
    return res

# if __name__ == '__main__':
# trec = ['a', 'r', 'v', 'd']
# index = get_index()
# populate_index(trec, index)
