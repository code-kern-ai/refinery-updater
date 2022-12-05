import re
from submodules.model.business_objects import attribute, embedding, user, general
from submodules.model import enums

def gateway_1_6_1() -> bool:
    __gateway_1_6_1_add_attribute_visibility()
    return True


def __gateway_1_6_1_add_attribute_visibility() -> bool:
    sql = f"""
    UPDATE attribute
    SET visibility = '{enums.AttributeVisibility.DO_NOT_HIDE.value}'
    WHERE visibility IS NULL
    """
    general.execute_sql(sql)
    general.commit()
    return True


def gateway_1_3_0() -> bool:
    __gateway_1_3_0_add_engineer()
    __gateway_1_3_0_add_attribute_for_embedding()
    __gateway_1_3_0_add_attribute_default_state()
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


def __gateway_1_3_0_add_attribute_default_state() -> bool:
    print("add UPLOADED state to existing attributes", flush=True)
    attributes = attribute.get_all(None, None)
    something_changed = False
    for a in attributes:
        if not a.state:
            a.state = "UPLOADED"
            something_changed = True
    if something_changed:
        general.commit()
        print("Added state.", flush=True)
    else:
        print("Nothing changed", flush=True)
    return something_changed
