import requests
import random
original_questions = {}
def quizapi(amt=5,category=21,difficulty="easy"):
    url = f"https://opentdb.com/api.php?amount=&category=21&difficulty=easy&type=multiple"
    parameters = {
        "amount": amt,
        "category": category,
        "difficulty":difficulty,
        "type": "multiple",
    }
    response = requests.get(url,params=parameters)
    all_questions = response.json()["results"]
    #if (o==True):
        #return all_questions

    #print(all_questions)
    i = 1
    for ques in all_questions:
        ques["incorrect_answers"].append(ques["correct_answer"])
        ques["id"] = str(i)
        #print(ques["id"])
        i = i+1
        random.shuffle(ques["incorrect_answers"])
        #print(ques["incorrect_answers"])
    return all_questions

#print(original_questions)
#quizapi()