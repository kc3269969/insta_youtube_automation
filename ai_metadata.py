import openai
from utils import get_env

openai.api_key = get_env("OPENAI_API_KEY")

def generate_metadata(video_path):
    # Use caption or basic info as prompt
    prompt = f"Create a catchy YouTube Shorts title, description (with CTA), and tags for this fact video."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    # Extract from response
    content = response.choices[0].message['content']
    # Parse AI output (expected: title, description, tags)
    # For now, dummy split
    title, description, tags = content.split("\n")[:3]
    return title, description, tags.split(",")