import requests

def get_osm_counts(lat: float, lon: float, radius: int = 1000) -> dict:
    """
    Đếm số lượng trường học và khu dân cư duy nhất trong bán kính, lọc trùng bằng name hoặc ID.

    Args:
        lat (float): Vĩ độ
        lon (float): Kinh độ
        radius (int): Bán kính tính theo mét (mặc định 1000)

    Returns:
        dict: {'schools': int, 'residential': int}
    """
    overpass_url = "http://overpass-api.de/api/interpreter"

    # Truy vấn các loại trường học
    school_query = f"""
    [out:json][timeout:25];
    (
      node["amenity"~"school|college|university"](around:{radius},{lat},{lon});
      way["amenity"~"school|college|university"](around:{radius},{lat},{lon});
      relation["amenity"~"school|college|university"](around:{radius},{lat},{lon});
    );
    out tags;
    """

    # Truy vấn khu dân cư (landuse = residential)
    residential_query = f"""
    [out:json][timeout:25];
    (
      way["landuse"="residential"](around:{radius},{lat},{lon});
      relation["landuse"="residential"](around:{radius},{lat},{lon});
    );
    out tags;
    """

    def count_unique_elements(query: str) -> int:
        try:
            resp = requests.get(overpass_url, params={'data': query})
            resp.raise_for_status()
            data = resp.json()

            unique = set()
            for el in data.get("elements", []):
                # Ưu tiên name, nếu không có thì dùng type + id để đếm riêng biệt
                name = el.get("tags", {}).get("name")
                if name:
                    unique.add(name.strip().lower())
                else:
                    unique.add(f"{el['type']}_{el['id']}")
            return len(unique)
        except Exception as e:
            print(f"❌ Lỗi khi truy vấn Overpass: {e}")
            return 0

    return {
        'schools': count_unique_elements(school_query),
        'residential': count_unique_elements(residential_query)
    }
