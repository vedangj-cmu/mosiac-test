"""
Mosaic API Tests
src/server/server_test.py

Run with: pytest server_test.py -v
"""

import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)


class TestHealth:
    """Test health endpoint."""

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestDirectory:
    """Test directory endpoints."""

    def test_get_directory_success(self):
        response = client.get("/directory?name=data_20250912")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "data_20250912"
        assert "files" in data
        assert data["file_count"] == 8

    def test_get_directory_not_found(self):
        response = client.get("/directory?name=invalid_dir")
        assert response.status_code == 404
        error = response.json()
        assert error["detail"]["code"] == "DIRECTORY_NOT_FOUND"

    def test_get_directory_missing_param(self):
        response = client.get("/directory")
        assert response.status_code == 422


class TestFile:
    """Test file endpoints."""

    def test_get_file_success(self):
        response = client.get("/file?name=sensor_data_20250916_162938_0.mcap")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "sensor_data_20250916_162938_0.mcap"
        assert "size_bytes" in data
        assert "created_at" in data

    def test_get_file_not_found(self):
        response = client.get("/file?name=nonexistent_file.mcap")
        assert response.status_code == 404
        error = response.json()
        assert error["detail"]["code"] == "FILE_NOT_FOUND"

    def test_get_file_missing_param(self):
        response = client.get("/file")
        assert response.status_code == 422


class TestFeeds:
    """Test feed endpoints."""

    def test_get_feeds_success(self):
        response = client.get("/feeds?file=sensor_data_20250916_162938_0.mcap")
        assert response.status_code == 200
        feeds = response.json()
        assert isinstance(feeds, list)
        assert len(feeds) > 0
        assert feeds[0]["name"] == "/center_rear/camera_info"
        assert "enabled" in feeds[0]

    def test_get_feeds_not_found(self):
        response = client.get("/feeds?file=unknown_file.mcap")
        assert response.status_code == 404
        error = response.json()
        assert error["detail"]["code"] == "FEED_NOT_AVAILABLE"

    def test_get_feeds_missing_param(self):
        response = client.get("/feeds")
        assert response.status_code == 422


class TestGroundTruth:
    """Test ground truth endpoints."""

    def test_get_groundtruth_success(self):
        response = client.get("/groundtruth?file=sensor_data_20250916_162938_0.mcap")
        assert response.status_code == 200
        gt_data = response.json()
        assert isinstance(gt_data, list)
        assert len(gt_data) > 0
        assert gt_data[0]["layer_name"] in ["Nucleus", "ML Output"]
        assert "boxes" in gt_data[0]

    def test_get_groundtruth_not_found(self):
        response = client.get("/groundtruth?file=unknown_file.mcap")
        assert response.status_code == 404
        error = response.json()
        assert error["detail"]["code"] == "GROUNDTRUTH_NOT_FOUND"

    def test_get_groundtruth_missing_param(self):
        response = client.get("/groundtruth")
        assert response.status_code == 422


class TestErrorHandling:
    """Test error responses."""

    def test_error_response_structure(self):
        """Verify error responses follow standard format."""
        response = client.get("/directory?name=invalid")
        assert response.status_code == 404
        error = response.json()
        assert "detail" in error
        assert "code" in error["detail"]
        assert "message" in error["detail"]
        assert "retryable" in error["detail"]

    def test_invalid_endpoint(self):
        response = client.get("/invalid_endpoint")
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
