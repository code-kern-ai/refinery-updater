# function name tamplate: <service_name>_<version_with_underscore>
# example: update logic for service AUTHORIZER for version 1.2.2 would be def authorizer_1_2_2()->bool:
# should always return True if update logic was successful
import re

from submodules.model.business_objects import attribute, embedding, general


def gateway_1_2_1() -> bool:
    print("update gateway to 1.2.1", flush=True)
    # fills attribute id column for existing embeddings
    embedding_items = embedding.get_all_embeddings()
    for i, embedding_item in enumerate(embedding_items):
        if embedding_item.attribute_id is None:
            attribute_name = __get_attribute_name_from_embedding_name(
                embedding_item.name
            )
            attribute_item = attribute.get_by_name(
                embedding_item.project_id, attribute_name
            )
            embedding_item.attribute_id = attribute_item.id
        if (i + 1) % 100 == 0:
            general.flush_or_commit(True)
    general.flush_or_commit(True)
    print("updated gateway to 1.2.1", flush=True)
    return True


def __get_attribute_name_from_embedding_name(embedding_name: str) -> str:
    regex = "^(.+)-(?:classification|extraction).*"
    return re.match(regex, embedding_name).group(1)
