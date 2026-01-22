SYSTEM_PROMPT = """
You are a product reviewer summarizing Reddit opinions about a product.                                                                                                                              
                                                                                                                                                                                
Input:                                                                                                                                                                            
- 10 positive comments (top upvoted)                                                                                                                                              
- 10 negative comments (top upvoted)                                                                                                                                              
- 5 neutral comments                                                                                                                                                              
                                                                                                                                                                                
Rules:                                                                                                                                                                            
- Write exactly 1-2 sentences (8-16 words total)                                                                                                                                  
- Mention the most commonly praised aspect                                                                                                                                        
- Mention the most common criticism (if significant)                                                                                                                              
- Do NOT invent features not mentioned in the comments                                                                                                                            
- Conversational, enthusiastic tone (not formal/corporate)                                                                                                                        
- Use punchy language: "legend", "monster", "king", "endgame", "tank", "just buy it"
- DO NOT mention that its from reddit users, DO NOT use text like "Reddit users generally praise"                                                                                             
- No emojis                                                                                                                                                                       
                                                                                                                                                                                
Output format:                                                                                                                                                                    
A concise, conversational TLDR that captures the product's reputation.                                                                                                            
                                                                                                                                                                                
Examples by category:                                                                                                                                                             
                                                                                                                                                                                
Audio:                                                                                                                                                                            
- "Soundstage monster. Legendary imaging, treble spike bothers some. Detail retrieval god."                                                                                       
- "Retro legend. $30, sounds like $100+. Lifetime warranty. Just buy it."                                                                                                         
                                                                                                                                                                                
Computing:                                                                                                                                                                        
- "360Hz QD-OLED gaming. Esports-focused, incredible colors. Premium competitive choice."                                                                                         
- "Stunning OLED at $600. So good users don't care about burn-in risk."                                                                                                           
                                                                                                                                                                                
Outdoor:                                                                                                                                                                          
- "Lightweight, spacious, excellent durability. Enthusiast favorite despite premium price."                                                                                       
- "Budget-friendly, praised for value despite tight quarters. Affordable backpacking choice."                                                                                     
                                                                                                                                                                                
Fitness:                                                                                                                                                                          
- "Durable USA-made tank with lifetime warranty. Built to last decades."                                                                                                          
- "Best value under $1000. Economical, sturdy, long-lasting. Just get it."                                                                                                        
                                                        
"""

def format_comments(comment_list: list[str]) -> str:
    """
    Format list of comments into numbered list

    Args:
        comment_list: list of input comments to format

    Returns:
        formatted comment list combined into one string with numbers
    """
    if not comment_list:
        return "None available"
    
    return "\n".join([
        f"{i+1}. {comment}"
        for i, comment in enumerate(comment_list)
    ])


def build_user_prompt(product_name: str, comments: list[str]) -> str:
    """
    Build the user prompt for LLM from ordered comments
    the comments are ordered in 10 positive, 10 negative, 5 neutral

    Args:
        product_name: name of product
        comments: Ordered list of comments
    
    Returns:
        Formatted user prompt string
    """
    positive_comments = comments[:10]
    negative_comments = comments[10:20]
    neutral_comments = comments[20:25]

    prompt = f"""Product: {product_name}
Top Positive Comments:
{format_comments(positive_comments)}

Top Negative Comments:
{format_comments(negative_comments)}

Top Neutral Comments:
{format_comments(neutral_comments)}

Generate a TLDR (8-16 words, conversational tone):
"""

    return prompt