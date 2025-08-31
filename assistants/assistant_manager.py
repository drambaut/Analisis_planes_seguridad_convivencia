# assistants/assistant_manager.py
from openai import AzureOpenAI

def get_or_create_assistant(client: AzureOpenAI, name: str, instructions: str, model: str) -> str:
    """
    Ensures an assistant exists with NO tools and the provided instructions/model.
    If an existing assistant is found by name, it will be updated to remove tools,
    set the model and refresh instructions.
    """
    # Find by name
    assistants = client.beta.assistants.list()
    target = None
    for a in assistants.data:
        if a.name == name:
            target = a
            break

    if target:
        # Normalize: remove tools, set model & instructions
        updated = client.beta.assistants.update(
            assistant_id=target.id,
            name=name,
            instructions=instructions,
            model=model,
            tools=[],  # <- IMPORTANT: remove any previous tools like file_search
            temperature=0.6,
            top_p=1,
        )
        print(f"Using existing assistant: {updated.id}")
        return updated.id

    # Create fresh assistant (no tools)
    created = client.beta.assistants.create(
        name=name,
        instructions=instructions,
        model=model,
        tools=[],  # no tools
        temperature=0.6,
        top_p=1,
    )
    print(f"Created assistant: {created.id}")
    return created.id