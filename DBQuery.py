import re
import json

#reads json db
def read_db(filename: str):
    # Open the json
    with open(filename, "r") as read_file:
        try:
            db = json.load(read_file)
        except json.decoder.JSONDecodeError:
            return False
        except FileNotFoundError:
            print("The file does not exist")
            return False
        except TypeError:
            print("The input type is invalid")
            return False
    if type(db) == str:
        db = json.loads(db)
    return db
"""this function writes to a json db"""
def write_to_db(filename: str, data: json):
    with open(filename, "r+") as write_file:
        try:
            file_data = json.load(write_file)
            file_data.append(data)
            write_file.seek(0)
            json.dump(file_data,write_file,indent = 4)
        except FileNotFoundError:
            print("No file exists")
            return False



"""This function searches for people with a particular skill and returns their name"""
def skill_query(queried_skill: str) -> [str] or bool:
    #open the file
    db = read_db('skillsDB.json')
    if not db:
        print("Database loading failed")
        return False

    #define result array
    people_with_skill = []
    #add people to the results if they have the skill
    for person in db:
        for skill in person["skills"]:
            if queried_skill == skill:
                people_with_skill.append(person["name"])

    if not people_with_skill:
        return False

    return people_with_skill

"""Retrieve known skill from DB"""
def get_skill_desc(queried_skill: str) -> str or bool:
    known_skills = read_db('skillsDB.json')
    for skill in known_skills:
        if skill["skill"] == queried_skill:
            return skill["desc"]
    return False




