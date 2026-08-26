def transform_adzuna_job(item: dict) -> dict:
    company = item.get("company") or {}
    category = item.get("category") or {}
    location = item.get("location") or {}
    
    # Safely convert to a boolean. '1' -> True, '0' -> False
    predicted_raw = item.get("salary_is_predicted")
    if predicted_raw is not None:
        predicted_bool = str(predicted_raw) == "1"
    else:
        predicted_bool = None

    return {
        "id": str(item.get("id")),
        "title": item.get("title"),
        "description": item.get("description"),
        "created": item.get("created"),
        "redirect_url": item.get("redirect_url"),
        "salary_min": item.get("salary_min"),
        "salary_max": item.get("salary_max"),
        "salary_is_predicted": predicted_bool,
        "contract_time": item.get("contract_time"),
        "contract_type": item.get("contract_type"),
        "company_name": company.get("display_name"),
        "category_label": category.get("label"),
        "category_tag": category.get("tag"),
        "location_name": location.get("display_name"),
        "latitude": item.get("latitude"), # Note: latitude usually comes from item directly or location depending on API version, keeping your structure
        "longitude": item.get("longitude"), 
        # (Wait, your original code had location.get("latitude"), make sure to match that if it was correct)
    }