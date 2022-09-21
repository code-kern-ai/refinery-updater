from submodules.model.business_objects import user, general


def gateway_1_3_0() -> bool:
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
