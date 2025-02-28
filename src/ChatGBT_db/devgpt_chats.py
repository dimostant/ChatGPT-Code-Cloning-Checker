import ujson


def json_data_to_str(json_data):
    return ujson.dumps(json_data)

def print_json_data(json_data):
    print(ujson.dumps(json_data))

# get data from json file and return it in usable format, always include
def get_json_data(file_path):
    with open(file_path, 'r') as file:
        return ujson.load(file)

# TODO: fix access safety issue with these functions
def get_sharing_title(sharing):
    sharing_title = sharing.get("Title", [])
    return sharing_title

def get_user_conversation(json_data, user, sharing, conversation):
    user_conversation = json_data["Sources"][user]["ChatgptSharing"][sharing]["Conversations"][conversation]
    return user_conversation

def get_conversation_question(user_conversation):
    question = user_conversation.get("Prompt", [])
    return question

def get_conversation_answer(user_conversation):
    answer = user_conversation.get("Answer", [])
    return answer

def get_conversation_code(user_conversation):
    code = user_conversation.get("ListOfCode", [])
    return code