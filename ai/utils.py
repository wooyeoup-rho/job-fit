def token_approximation(text: str) -> int:
    return max(1, len(text) // 4)

def prompt_builder(resume, job_description, add_info, output_instructions):
    return f"""
    You are a career coach. Compare the following job description with resume & additional information:
    
    Job description:
    {job_description}
    
    Resume:
    {resume}
    
    Additional info:
    {add_info}
    
    Return ONLY the sections specified. Do NOT add extra commentary or text.
    {output_instructions}
    """

def estimate_cost(tokens_input: int, tokens_output: int, model="gpt-5-mini"):
    rates = {
        "gpt-5-mini": {"input": 0.25/1000000, "output": 2/1000000},
        "gpt-5": {"input": 1.25/1000000, "output": 10/1000000},
    }

    if model not in rates:
        raise ValueError(f"Unknown model {model}")

    return round(tokens_input * rates[model]["input"] + tokens_output * rates[model]["output"], 5)