import os
import requests

from submodules.model.business_objects import embedding, general


NEURAL_SEARCH = os.getenv("NEURAL_SEARCH")


def neural_search_1_15_0() -> bool:
    neural_search_1_15_0_delete_all_tf_idf_embeddings()
    return True


def neural_search_1_15_0_delete_all_tf_idf_embeddings() -> bool:
    # previous tf-idf embeddings didn't do anything useful so we can just delete them
    # Note that tensors are deleted by cascading
    query = "SELECT id FROM embedding WHERE platform = 'python' AND model = 'tf-idf'"
    embedding_ids = general.execute_all(query)
    if len(embedding_ids) > 0:
        url_delete = f"{NEURAL_SEARCH}/delete_collection"
        for embedding_id in embedding_ids:
            try:
                params = {"embedding_id": embedding_id[0]}
                requests.put(url_delete, params=params)
            except Exception as e:
                print(
                    f"Error deleting tf-idf embedding {embedding_id[0]} from qdrant: {e}"
                )
                return False

        query = "DELETE FROM embedding WHERE platform = 'python' AND model = 'tf-idf'"
        general.execute(query)
        general.commit()


def neural_search_1_12_0() -> bool:
    __neural_search_1_12_0_update_qdrant()
    return True


def __neural_search_1_12_0_update_qdrant() -> bool:
    print("upgrade qdrant version, recreate collections", flush=True)
    success = True

    # only recreate collections, no need to create missing collections
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

    if success:
        print("Recreated all collections.", flush=True)
    else:
        print("Recreating collections failed.", flush=True)
    return success


def neural_search_1_2_1() -> bool:
    print("upgrade qdrant version, recreate collections", flush=True)
    success = __recreate_qdrant_collections()
    if success:
        print("Recreated all collections.", flush=True)
    else:
        print("Recreating collections failed.", flush=True)
    return success


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
        print(response.content, flush=True)
        success = False

    return success
