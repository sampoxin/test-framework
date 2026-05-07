import allure


@allure.epic("评论管理")
def test_get_comments_by_post(client):
    result = client.send("GET", "/comments", params={"postId":1})
    response_data = result.json()
    assert all([item["postId"] == 1 for item in response_data])

@allure.epic("评论管理")
def test_comment_fields(client):
    result = client.send("GET", "/comments/1")
    response_data = result.json()
    data_keys = set(response_data.keys())
    assert "id" in data_keys
    assert "body" in data_keys
    assert "email" in data_keys
    assert "name" in data_keys