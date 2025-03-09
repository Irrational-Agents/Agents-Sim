import json
import yaml
from API.server_draft.server import app
def generate_openapi_json(app, output_file: str = "openapi.json"):
   """
   Generate OpenAPI specification JSON file from FastAPI app
   """
   openapi_schema = app.openapi()
   with open(output_file, "w", encoding="utf-8") as f:
       json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
   print(f"OpenAPI specification saved to {output_file}")


if __name__ == "__main__":
   generate_openapi_json(app)