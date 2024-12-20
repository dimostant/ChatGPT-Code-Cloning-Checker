import os

import ChatGBT_db.devgpt_chats as chatgpt_db

from cloning import code_cloning_check
from code_handling import extract_html_code, extract_html_text, extract_dictionary_code, remove_non_utf8_chars
import json

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# TODO: to test
def compare_questions(api_question, gpt_question):
    # print removing the \n and replacing with " " for ease
    print("\ncomparing questions :\n", api_question.replace("\n", " "), "\nand :\n", gpt_question.replace("\n", " "))
    #
    # x_list = word_tokenize(api_question)
    # y_list = word_tokenize(gpt_question)
    #
    # sw = stopwords.words('english')
    # l1 = []
    # l2 = []
    #
    # x_set = {w for w in x_list if not w in sw}
    # y_set = {w for w in y_list if not w in sw}
    #
    # r_vector = x_set.union(y_set)
    #
    # for w in r_vector:
    #     if w in x_set:
    #         l1.append(1)
    #     else:
    #         l1.append(0)
    #     if w in y_set:
    #         l2.append(1)
    #     else:
    #         l2.append(0)
    # c = 0
    #
    # # cosine formula
    # for i in range(len(r_vector)):
    #     c += l1[i] * l2[i]
    #
    # cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    # print("similarity: ", cosine)
    #
    # return cosine
    return 0.8

def compare_answers(so_api_answers_json, gpt_conversation): #might change to answers
    gpt_answer_dictionary = chatgpt_db.get_conversation_code(gpt_conversation)
    gpt_answer_code = extract_dictionary_code(gpt_answer_dictionary)
    gpt_answer_clean_code = remove_non_utf8_chars(gpt_answer_code)
    # TODO: complete and test if "remove" function provides code safe to be compared
    # print("DevGPT code : \n", gpt_answer_clean_code)

    # TODO: check for empty DevGPT answer # test if this is done
    if "".join(gpt_answer_clean_code.split()) != "": #removes all whitespaces
        for item in so_api_answers_json:
           if item.get("body"):
                so_api_answer_body = item["body"]
                so_api_answer_code = extract_html_code(so_api_answer_body)
                so_api_answer_clean_code = remove_non_utf8_chars(so_api_answer_code)
                # print("api code: ", so_api_answer_clean_code)

                cloning_percentage = code_cloning_check(gpt_answer_clean_code, so_api_answer_clean_code) #TODO: hardcoded, change

                if cloning_percentage == 1:
                    print("cloned code")
                elif cloning_percentage > 0.7:
                    print("almost identical code")
                elif 0.3 < cloning_percentage < 0.7:
                    print("inconclusive similarity") # TODO: does that mean something else?
                else :
                    print("completely different code")

                # TODO: cloning Code comparison and result extraction, then store the results in CSV or JSON and in what structure

def compare_process ():
    # get questions
    with open(os.path.join('StackOverflow_api_db', 'questions.json'), 'r') as q:
        so_api_questions_json = json.load(q)

    # get DevGPT conversations
    dev_gpt_json = chatgpt_db.get_json_data(
        'ChatGBT_db/DevGPT/snapshot_20231012/20231012_235320_discussion_sharings.json')

    # get answers
    with open(os.path.join('StackOverflow_api_db', 'answers.json'), 'r') as a:
        so_api_answers_json = json.load(a)

    # iterate through every question
    for item in so_api_questions_json.get("items", []):
        if item.get("body") :
            so_api_question_id = item["question_id"]
            so_api_question_body = item["body"] #improve? # for title?
            str_so_api_question = extract_html_text(so_api_question_body)
            str_so_api_clean_question = remove_non_utf8_chars(str_so_api_question)
            # print("StackOverflow question :", str_so_api_clean_question)

            counter = 0 # delete after testing # used to choose number ( almost ) of gpt chats

            # compare question with every DevGPT question
            for source in dev_gpt_json.get("Sources", []):
                for sharing_data in source.get("ChatgptSharing", []):
                    for gpt_conversation in sharing_data.get("Conversations", []):
                        if gpt_conversation :
                            gpt_question = chatgpt_db.get_conversation_question(gpt_conversation)
                            str_gpt_question = chatgpt_db.json_data_to_str(gpt_question)
                            # TODO: check for empty question and others empty things like this ( i think {}) EVERYWHERE
                            # TODO: check for chinese characters e.t.c and skip question
                            # print("DevGPT        question :", str_gpt_question)

                            counter = counter + 1
                            print(counter)

                            similarity = compare_questions(str_so_api_clean_question, str_gpt_question) #TODO: hardcoded, change

                            if similarity == 1:
                                print("identical questions\n") #special case to check??

                            elif 0.7 <= similarity < 1:
                                # print("similar questions, checking...\n")
                                # does answer file need checking?
                                try:
                                    # TODO: what is returned, if the id has no answers
                                    so_api_answers_json = (item[str(so_api_question_id)] for item in so_api_answers_json["items"] if list(item.keys())[0] == str(so_api_question_id))
                                    print("a", so_api_answers_json)
                                except:
                                    continue

                                if so_api_answers_json:
                                    compare_answers(so_api_answers_json, gpt_conversation)

                            # TODO: is smaller batch, e.g 0.3 neccessary?

                            else:
                                print("different questions\n")

                if counter >= 4: break # inner conv increase the counter e.g. 1 2 3, 3 seen out. 4 5, 5 out. "if" checks out the loop so need >=

# TODO: only compare with python code from DEVGPT
# TODO: extra code that confirms its python code? where? ( at answer code extraction funtion? at data retrieval? after data retrieval? )

# TODO: identical case [questionId],[gpt_conversation]
# TODO: different case [questionId],[gpt_conversation]
# TODO: match     case [questionId],[gpt_conversation]
compare_process()

#TODO: future considerations:
    # TODO: take only the answer with the most votes
    # TODO: compare question context instead of only the title? compare answer context with chat non code repsonse??

