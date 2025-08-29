def create_message(role, content, tool_name=None):
    if tool_name:
        return {"role":role, "content":content, "tool_name":tool_name}
    
    return {"role":role, "content":content}

def print_messages(messages):
    for message in messages:
        print(message)