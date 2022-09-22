import re
from submodules.model.business_objects import attribute, embedding, user, general


def gateway_1_3_0() -> bool:
    __gateway_1_3_0_add_engineer()
    __gateway_1_3_0_add_attribute_for_embedding()
    return True


def __gateway_1_3_0_add_engineer() -> bool:
    print("add ENGINEER role to existing users", flush=True)
    users = user.get_all()
    something_changed = False
    for u in users:
        if not u.role:
            u.role = "ENGINEER"
            something_changed = True
    if something_changed:
        general.commit()
        print("Added role.", flush=True)
    else:
        print("Nothing changed", flush=True)
    return something_changed


def __gateway_1_3_0_add_attribute_for_embedding() -> bool:
    print("add attribute id to existing embeddings", flush=True)
    embedding_added = False
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
            embedding_added = True
    if embedding_added:
        general.commit()
        print("Added attribute id.", flush=True)
    else:
        print("No attribute id added.", flush=True)

    return embedding_added


def __get_attribute_name_from_embedding_name(embedding_name: str) -> str:
    regex = "^(.+)-(?:classification|extraction).*"
    return re.match(regex, embedding_name).group(1)
