import os
import typing
from sqlalchemy import create_engine


engine = create_engine(os.getenv("POSTGRES"), convert_unicode=True)


# READ
def get_all_organization_ids() -> typing.Dict[str, typing.List[str]]:
    query = f"""
    SELECT organization_id::TEXT, array_agg(id::TEXT) project_ids
    FROM project p
    GROUP BY organization_id
    """
    with engine.connect() as conn:
        organizations = conn.execute(query).fetchall()
        if not organizations:
            return None
        return {org[0]:set(org[1]) for org in organizations}
