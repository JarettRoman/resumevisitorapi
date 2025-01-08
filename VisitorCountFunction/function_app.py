import logging
import json
import os
from azure.cosmos import CosmosClient
from azure.functions import HttpRequest, HttpResponse

def main(req: HttpRequest) -> HttpResponse:
    logging.info('Processing visitor count request.')

    # Cosmos DB connection details
    endpoint = os.getenv("COSMOS_DB_ENDPOINT")
    key = os.getenv("COSMOS_DB_PRIMARY_KEY")
    database_name = os.getenv("COSMOS_DB_NAME") 
    container_name = "VisitorCount"

    try:
        # Connect to Cosmos DB
        client = CosmosClient(endpoint, key)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        # Read and update the visitor count
        item = container.read_item(item="1", partition_key="Counter")
        visitor_count = item.get("count", 0)
        visitor_count += 1
        item["count"] = visitor_count
        container.upsert_item(item)

        # Return the updated count
        return HttpResponse(
            json.dumps({"visitorCount": visitor_count}),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",  # Allow all origins
                "Access-Control-Allow-Methods": "GET, POST",  # Allowed methods
                "Access-Control-Allow-Headers": "Content-Type"  # Allowed headers
            }
        )

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return HttpResponse(
            json.dumps({"error": "Unable to process request"}),
            status_code=500,
            mimetype="application/json"
        )
