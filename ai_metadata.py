import openai
from utils import log_message

# Placeholder function - **MUST** be replaced with actual OpenAI API calls
def generate_metadata_with_ai(video_topic_or_caption, env):
    """
    Generates YouTube title, description, and tags using AI based on content.
    For a real implementation, use the openai.Completion.create or 
    openai.ChatCompletion.create method with the provided API key.
    """
    log_message("INFO", f"Generating metadata for topic: '{video_topic_or_caption[:50]}...'")
    
    openai.api_key = env['OPENAI_API_KEY']
    
    # Simple placeholder logic based on the prompt's requirements
    topic = video_topic_or_caption.replace('\n', ' ')
    
    if "science" in topic.lower():
        title_base = "🤯 Scientific Fact That Will Blow Your Mind"
        description_base = "Dive into the world of science with this incredible fact!"
        tags_base = "facts,science,shorts,learn,knowledge,education"
    else:
        title_base = "🛑 You Won't Believe This Crazy Fact!"
        description_base = "Get your daily dose of amazing facts right here!"
        tags_base = "facts,shorts,amazing,crazy,didyouknow"
        
    
    # 1. Generate Title (under 100 characters)
    title = f"{title_base} #{topic.split()[0]}".replace('..', '.')[:95]
    
    # 2. Generate Description (with CTA)
    description = (
        f"{description_base}\n\n"
        f"✅ Subscribe for more daily facts! #shorts\n"
        f"👍 Like if you learned something new!"
    )
    
    # 3. Generate Tags & Hashtags
    hashtags = f"#shorts #facts #{topic.split()[0].lower()} #viral"
    tags = tags_base.split(',') + [topic.split()[0].lower()]

    return {
        "title": title,
        "description": description,
        "tags": ','.join(tags),
        "hashtags": hashtags
    }
