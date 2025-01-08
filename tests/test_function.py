import json
import pytest
from unittest.mock import Mock, patch
from azure.functions import HttpRequest
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from VisitorCountFunction.function_app import main

# Test case for a successful response
@patch("VisitorCountFunction.function_app.CosmosClient")
def test_function_success(mock_cosmos_client):
    # Mock Cosmos DB client behavior
    mock_container = Mock()
    mock_container.read_item.return_value = {"id": "1", "PartitionKey": "Counter", "count": 5}
    mock_container.upsert_item.return_value = None
    mock_database = Mock()
    mock_database.get_container_client.return_value = mock_container
    mock_cosmos_client.return_value.get_database_client.return_value = mock_database

    # Create a mock HTTP request
    req = HttpRequest(
        method="GET",
        url="/api/VisitorCountFunction",
        body=None
    )

    # Call the function
    response = main(req)

    # Assert the response is as expected
    assert response.status_code == 200
    response_data = json.loads(response.get_body())
    assert response_data["visitorCount"] == 6  # Previous count + 1
    
# Test case for a failure (e.g., missing database)
@patch("VisitorCountFunction.function_app.CosmosClient")
def test_function_failure(mock_cosmos_client):
    # Simulate an exception when connecting to Cosmos DB
    mock_cosmos_client.side_effect = Exception("Database connection failed")

    # Create a mock HTTP request
    req = HttpRequest(
        method="GET",
        url="/api/VisitorCountFunction",
        body=None
    )

    # Call the function
    response = main(req)

    # Assert the response is a 500 error
    assert response.status_code == 500
    response_data = json.loads(response.get_body())
    assert response_data["error"] == "Unable to process request"
    
@patch("VisitorCountFunction.function_app.CosmosClient")
def test_document_not_found(mock_cosmos_client):
    # Mock Cosmos DB behavior
    mock_container = Mock()
    # Simulate a NotFound exception when trying to read the document
    mock_container.read_item.side_effect = CosmosResourceNotFoundError

    # Mock the database and container clients
    mock_database = Mock()
    mock_database.get_container_client.return_value = mock_container
    mock_cosmos_client.return_value.get_database_client.return_value = mock_database

    # Create a mock HTTP request
    req = HttpRequest(
        method="GET",
        url="/api/VisitorCountFunction",
        body=None
    )

    # Call the function
    response = main(req)

    # Assert the response is a 500 error
    assert response.status_code == 500
    response_data = json.loads(response.get_body())
    assert response_data["error"] == "Unable to process request"