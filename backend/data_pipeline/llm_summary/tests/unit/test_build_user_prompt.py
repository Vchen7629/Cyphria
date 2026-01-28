from src.llm_client.prompts import build_user_prompt


def test_no_negative_or_neutral_comments() -> None:
    """Negative and Neutral should have None available"""
    comments = [f"comment_{i}" for i in range(10)]
    product_name = "product"

    expected_result = """Product: product
Top Positive Comments:
1. comment_0
2. comment_1
3. comment_2
4. comment_3
5. comment_4
6. comment_5
7. comment_6
8. comment_7
9. comment_8
10. comment_9

Top Negative Comments:
None available

Top Neutral Comments:
None available

Generate a TLDR (8-16 words, conversational tone):
"""

    assert build_user_prompt(product_name, comments) == expected_result


def test_all_comment_categories_filled() -> None:
    """All categories should be populated when we have 25 comments"""
    comments = [f"comment_{i}" for i in range(25)]
    product_name = "product"

    expected_result = """Product: product
Top Positive Comments:
1. comment_0
2. comment_1
3. comment_2
4. comment_3
5. comment_4
6. comment_5
7. comment_6
8. comment_7
9. comment_8
10. comment_9

Top Negative Comments:
1. comment_10
2. comment_11
3. comment_12
4. comment_13
5. comment_14
6. comment_15
7. comment_16
8. comment_17
9. comment_18
10. comment_19

Top Neutral Comments:
1. comment_20
2. comment_21
3. comment_22
4. comment_23
5. comment_24

Generate a TLDR (8-16 words, conversational tone):
"""

    assert build_user_prompt(product_name, comments) == expected_result


def test_extra_comments_ignored() -> None:
    """Comments beyond 25 should be ignored"""
    comments = [f"comment_{i}" for i in range(100)]
    product_name = "product"

    expected_result = """Product: product
Top Positive Comments:
1. comment_0
2. comment_1
3. comment_2
4. comment_3
5. comment_4
6. comment_5
7. comment_6
8. comment_7
9. comment_8
10. comment_9

Top Negative Comments:
1. comment_10
2. comment_11
3. comment_12
4. comment_13
5. comment_14
6. comment_15
7. comment_16
8. comment_17
9. comment_18
10. comment_19

Top Neutral Comments:
1. comment_20
2. comment_21
3. comment_22
4. comment_23
5. comment_24

Generate a TLDR (8-16 words, conversational tone):
"""

    assert build_user_prompt(product_name, comments) == expected_result


def test_product_name_with_special_characters() -> None:
    """Should handle special characters in product name"""
    comments = ["comment_1", "comment_2"]
    product_name = 'Product\'s "name" & <Tags>'

    result = build_user_prompt(product_name, comments)

    assert product_name in result
