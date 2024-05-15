import os
import re
import requests
from config_handler import get_config_value
from submodules.model.business_objects import (
    attribute,
    embedding,
    user,
    general,
)
from submodules.model import enums


def gateway_1_15_0() -> bool:
    # Note: A previous version had the previous update listed as v1.15.
    # That was false, the updates already ran through. This is now for the actual 1.15 release
    __gateway_1_15_0_add_default_admin_log_level()
    return True


def __gateway_1_15_0_add_default_admin_log_level() -> bool:
    query = "UPDATE organization SET log_admin_requests = 'NO_GET' WHERE log_admin_requests IS NULL"
    general.execute(query)
    general.commit()
    return True


def gateway_1_14_0() -> bool:
    # here, we update data for cognition using the gateway pattern
    # as the corresponding database updates (alembic) are managed using the refinery gateway it is
    # ensured that these updates are executed at the correct time
    gateway_1_14_0_add_cognition_project_state()
    gateway_1_14_0_add_cognition_strategy_complexity()
    __gateway_1_14_0_add_cognition_project_file_defaults()
    __gateway_1_14_0_add_cognition_conversation_file_defaults()
    __gateway_1_14_0_remove_cognition_step_type_relevance()
    return True


def gateway_1_14_0_add_cognition_project_state() -> bool:
    query = f"""
    UPDATE cognition.project
    SET state = '{enums.CognitionProjectState.PRODUCTION.value}'
    WHERE state IS NULL
    """
    general.execute(query)
    general.commit()
    return True


def gateway_1_14_0_add_cognition_strategy_complexity() -> bool:
    cognition_url = os.getenv("COGNITION_GATEWAY")
    if not cognition_url:
        print(
            "No cognition gateway url found. Skipping cognition strategy complexity update."
        )
        return False

    response = requests.post(
        f"{cognition_url}/api/v1/strategies/internal/calculate_missing_complexities"
    )
    if response.status_code != 200:
        print(
            f"Failed to update cognition strategy complexities. Status code: {response.status_code}"
        )
        return False

    return True


def __gateway_1_14_0_add_cognition_project_file_defaults() -> bool:
    query = """
    UPDATE cognition.project
    SET max_file_size_mb = 3,
        allow_file_upload = FALSE
    WHERE max_file_size_mb IS NULL
    """
    general.execute(query)
    general.commit()
    return True


def __gateway_1_14_0_add_cognition_conversation_file_defaults() -> bool:
    query = """
    UPDATE cognition.conversation
    SET has_tmp_files = FALSE,
        archived = FALSE
    WHERE has_tmp_files IS NULL
    """
    general.execute(query)
    general.commit()
    return True


def __gateway_1_14_0_remove_cognition_step_type_relevance() -> bool:
    query = """
    DELETE FROM cognition.strategy_step WHERE step_type = 'RELEVANCE'
    """
    general.execute(query)
    general.commit()
    return True


def gateway_1_10_1() -> bool:
    __gateway_1_10_1_add_additional_embedding_information()
    return True


def __gateway_1_10_1_add_additional_embedding_information() -> bool:
    def __transform_embedding_by_name(embedding_name: str):
        splitted_name = embedding_name.split("-")
        attribute_name = splitted_name[0]
        embedding_type = splitted_name[1]
        model = "-".join(splitted_name[2:])
        if "bag-of-words" == model or "bag-of-characters" == model or "tf-idf" == model:
            platform = enums.EmbeddingPlatform.PYTHON.value
        else:
            platform = enums.EmbeddingPlatform.HUGGINGFACE.value
        name = f"{attribute_name}-{embedding_type}-{platform}-{model}"
        return platform, model, name

    print(
        "Infer platform and new name and model out of old embedding name and add it to the embedding table ",
        flush=True,
    )
    embeddings = embedding.get_all_embeddings()
    idx = 0
    for embedding_item in embeddings:
        if embedding_item.platform:
            continue
        idx += 1
        platform, model, name = __transform_embedding_by_name(embedding_item.name)
        embedding_item.platform = platform
        embedding_item.model = model
        embedding_item.name = name

    general.commit()
    print(f"Updated information for {idx} embeddings", flush=True)

    return True


def gateway_1_8_1() -> bool:
    __gateway_1_8_1_add_organization_limits()
    return True


def __gateway_1_8_1_add_organization_limits() -> bool:
    is_managed = get_config_value("is_managed")
    if is_managed:
        max_rows = 50000
        max_cols = 25
        max_char_count = 100000
    else:
        max_rows = get_config_value("max_rows") or 50000
        max_cols = get_config_value("max_cols") or 25
        max_char_count = get_config_value("max_char_count") or 100000

    print(
        "Add default limit for organizations",
        flush=True,
    )
    general.execute(
        f"""
        UPDATE organization
        SET max_rows = {max_rows}, max_cols = {max_cols}, max_char_count = {max_char_count}
        WHERE max_rows IS NULL
    """
    )
    general.commit()
    print("Added default limit for organizations", flush=True)

    return True


def gateway_1_6_1() -> bool:
    __gateway_1_6_1_add_attribute_visibility()
    return True


def __gateway_1_6_1_add_attribute_visibility() -> bool:
    print(
        f"Set visibility of attributes to value {enums.AttributeVisibility.DO_NOT_HIDE.value}",
        flush=True,
    )
    (count,) = general.execute(
        """SELECT COUNT(id)
    FROM attribute
    WHERE visibility IS NULL
    """
    ).first()

    if count > 0:
        general.execute(
            f"""
        UPDATE attribute
        SET visibility = '{enums.AttributeVisibility.DO_NOT_HIDE.value}'
        WHERE visibility IS NULL
        """
        )
        general.commit()
        print(f"Set value to {count} attributes.", flush=True)
    else:
        print("Nothing changed", flush=True)

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
