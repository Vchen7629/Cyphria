from src.llm_client.prompts import format_comments


def test_empty_comment_list() -> None:
    """Empty comment list should return 'None available'"""
    assert format_comments([]) == "None available"


def test_comment_with_embedded_newline() -> None:
    """Comments with newline might break formatting"""
    comments = ["comment_1", "comment_2\ncomment_3", "comment_4"]
    expected_result = "1. comment_1\n2. comment_2\ncomment_3\n3. comment_4"

    assert format_comments(comments) == expected_result


def test_empty_string_in_list() -> None:
    """Empty string should still be numbered"""
    comments = ["comment_1", "", "comment_3"]
    expected_result = "1. comment_1\n2. \n3. comment_3"

    assert format_comments(comments) == expected_result


def test_whitespace_only_comments() -> None:
    """Whitespace-only strings should be preserved"""
    assert format_comments(["  ", "\t"]) == "1.   \n2. \t"


def test_single_comment() -> None:
    """Single comment should be numbered as 1."""
    assert format_comments(["jajaja"]) == "1. jajaja"


def test_adds_numbers_before_individual_comment() -> None:
    """It should add numbers like 1. before comments"""
    comments = ["comment_1", "comment_2", "comment_3"]
    expected_result = "1. comment_1\n2. comment_2\n3. comment_3"

    assert format_comments(comments) == expected_result


def test_double_digit_numbering() -> None:
    """Numbering should work correctly for 10+ items"""
    comments = [f"comment_{i}" for i in range(21)]
    result = format_comments(comments)
    assert "10. comment_9" in result
    assert "15. comment_14" in result
    assert "21. comment_20" in result
