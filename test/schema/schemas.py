def individual_serial(plan) -> dict:
    return {
        "id": str(plan["_id"]),
        "name": plan["name"],
        "description": plan["description"],
        "complete": plan["complete"]
    }


def list_serial(plan) -> list:
    return [individual_serial(plan) for plan in plan]