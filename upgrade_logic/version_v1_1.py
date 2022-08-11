import os
import requests

from submodules.model.business_objects import embedding


NEURAL_SEARCH = os.getenv("NEURAL_SEARCH")


def upgrade():
    print("upgrade qdrant version, recreate collections")
    success = __recreate_qdrant_collections()
    if success:
        print("Recreated all collections.")
    else:
        print("Recreating collections failed.")


def __recreate_qdrant_collections() -> bool:

    success = True

    # recreate collections
    embedding_items = embedding.get_finished_attribute_embeddings()

    url_recreate = f"{NEURAL_SEARCH}/recreate_collection"
    for project_id, embedding_id in embedding_items:
        params = {
            "project_id": str(project_id),
            "embedding_id": str(embedding_id),
        }
        response = requests.post(url=url_recreate, params=params)

        if response.status_code != 200:
            print(response.content)
            success = False

    # create missing collections
    # to be sure that an collection exists for every embedding
    url_missing_collections = f"{NEURAL_SEARCH}/create_missing_collections"
    response = requests.put(url=url_missing_collections)

    if response.status_code != 200 and response.status_code != 412:
        print(response.content)
        success = False

    return success
