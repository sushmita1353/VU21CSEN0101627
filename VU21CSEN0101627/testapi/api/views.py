# products/views.py

from django.http import JsonResponse
from django.core.cache import cache
import requests



def fetch_product_data(category):
    cache_key = f"products_{category}"
    products = cache.get(cache_key)

    if not products:
        products = []
        response = requests.get(
            f"http://20.244.56.144/test/companies/AMZ/categories/{category}/products",
            params={
                "top": 10,
                "minPrice": 1,
                "maxPrice": 10000,
            },
            headers={
                "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiZXhwIjoxNzI0NzQyMTQxLCJpYXQiOjE3MjQ3NDE4NDEsImlzcyI6IkFmZm9yZG1lZCIsImp0aSI6ImVlNTI3OTNhLThmZGUtNDZmZC1iNTdkLWMwMjlkYTEwNGZlMSIsInN1YiI6InNkb2trYXJpQGdpdGFtLmluIn0sImNvbXBhbnlOYW1lIjoiZ2l0YW0iLCJjbGllbnRJRCI6ImVlNTI3OTNhLThmZGUtNDZmZC1iNTdkLWMwMjlkYTEwNGZlMSIsImNsaWVudFNlY3JldCI6InJYU2dxRWVEaGNYVUZuSEIiLCJvd25lck5hbWUiOiJTdXNobWl0YSBEb2trYXJpIiwib3duZXJFbWFpbCI6InNkb2trYXJpQGdpdGFtLmluIiwicm9sbE5vIjoiVlUyMUNTRU4wMTAxNjI3In0.8__DIHIrjZiOSiw9j3-u09FESTUii87lKXfg2pgFFUg"
            },
        )
        print(response.status_code)
        if response.status_code == 200:
            products.extend(response.json())
        cache.set(cache_key, products, timeout=600)
    return products


def add_unique_id(product, categoryname, index):
    product["id"] = f"{categoryname}_{index}"
    return product


def top_products_view(request, categoryname):
    n = int(request.GET.get("n", 10))
    page = int(request.GET.get("page", 1))
    sort = request.GET.get("sort", None)
    order = request.GET.get("order", "asc")

    try:
        products = fetch_product_data(categoryname)

        if sort:
            reverse = order == "desc"
            products = sorted(products, key=lambda x: x.get(sort), reverse=reverse)

        start_index = (page - 1) * n
        paginated_products = products[start_index : start_index + n]

        response = [
            add_unique_id(product, categoryname, start_index + i)
            for i, product in enumerate(paginated_products)
        ]

        return JsonResponse(response, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def product_detail_view(request, categoryname, productid):
    try:
        products = fetch_product_data(categoryname)
        product = next(
            (p for p in products if f"{categoryname}_{products.index(p)}" == productid),
            None,
        )

        if not product:
            return JsonResponse({"error": "Product not found"}, status=404)

        return JsonResponse(product)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
