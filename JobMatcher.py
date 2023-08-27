from ChatGPT import ChatGPT
import re
import json
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
from DBQuery import read_db, write_to_db, get_skill_desc


class JobMatcher:
    #the standard system_msg for this class
    sys_msg = "You are a system knowledgable about the skill requirments for any job"
    #the output format for the skill finder
    output_format_finder = "Produce a python dictionary of the 10 most important skills " \
                   "needed as the key, and as the value: number ranking in importance for "
    #The output format for the skill comparator
    output_format_comparator = "Produce a 300 word description, including what industries use it," \
                               "what the skill is used to create, of the following skill "
    def __init__(self, employees = [], jobs = []):
        self.employees = employees
        self.jobs = jobs
        self.job_skills = {}
        self.skill_finder_ai = ChatGPT(JobMatcher.sys_msg, JobMatcher.output_format_finder)
        self.skill_comparator_ai = ChatGPT(JobMatcher.sys_msg, JobMatcher.output_format_comparator)
        self.skill_descriptions = {}
        self.fill_skills_database()
    #
    def getSkills(self, job: str):
        user_msg = self.output_format_finder + job

        # check if the job is already in the system and create a response
        if job not in self.job_skills.keys():
            self.job_skills[job] = self.skill_finder_ai.getChatGPTResponse(user_msg)
            response = self.job_skills[job]
        else:
            response = self.job_skills[job]
        # capture only the dictionary
        dictionary = re.search(r"\{([^}]+)\}", response)
        # try to convert to json
        try:
            response = json.loads(dictionary.group())
        except AttributeError:
            print(response)
            return "error"

        return response

    """searches through the employees and preloads skills into the database of the form [{skill: desc},{skill:desc}] """
    def fill_skills_database(self, skill_limit=0):
        #terminates at limit
        if skill_limit == 0:
            return "Done"
        limit_counter = 0
        emps = read_db('mockdatabase.json')
        known_skills = read_db('skillsDB.json')
        # case where db is empty
        if not known_skills:
            first_skill = emps[0]["skills"][0]
            print(first_skill)
            first_desc = self.skill_comparator_ai.getChatGPTResponse(
                JobMatcher.output_format_comparator + first_skill
            )
            limit_counter += 1
            write_to_db("skillsDB.json", {"skill": first_skill, "desc": first_desc})
            # refresh view of db
            known_skills = read_db('skillsDB.json')

        # The case where the DB is not empty
        for employee in emps:
            for skill in employee["skills"]:
                skill_known = False
                for known_skill in known_skills:
                    # check if skill is known
                    print(known_skill["skill"] + " " + skill)
                    if known_skill["skill"] == skill:
                        skill_known = True
                if skill_known == False:
                        skill_desc = self.skill_comparator_ai.getChatGPTResponse(
                            JobMatcher.output_format_comparator + skill
                        )
                        write_to_db('skillsDB.json', {"skill": skill, "desc": skill_desc})
                        limit_counter += 1
                        if limit_counter >= skill_limit:
                            return "Done"
                        #update skills
                        known_skills = read_db('skillsDB.json')






    """This function gets chat GTP to write 150 words describing each skill, and then a cosine similarity is 
    produced between the two texts.
    This allows a comparable, interpretable and relatively consistent similarity score to be generated for each skill"""
    def skill_comparator(self, skill_needed: str, candidate_skill: str) -> float:
        if(skill_needed == candidate_skill):
            return 1
        else:
            for skill in (skill_needed, candidate_skill):
                # get a description of both skills, check if there is already a chatgpt description saved
                skill_desc = get_skill_desc(skill)
                if not skill_desc:
                    self.job_skills[skill] = self.skill_comparator_ai.getChatGPTResponse(
                        JobMatcher.output_format_comparator + skill
                    )
                    write_to_db('skillsDB.json', {"skill": skill, "desc": self.job_skills[skill]})
                else:
                    self.job_skills[skill] = skill_desc

            needed_desc = self.job_skills[skill_needed]
            candidate_desc = self.job_skills[candidate_skill]
            # print("needed: " + needed_desc)
            # print("candidate: " + candidate_desc)
            return self.cosine_sim(needed_desc, candidate_desc)


    def cosine_sim(self, text1, text2):
        #remove non-alphabetic characters
        regex = re.compile('[^a-zA-Z]')
        regex.sub('',text1)
        regex.sub('',text2)
        # perform tokenization and lemmatization on the texts
        tokens1 = word_tokenize(text1.lower())
        tokens2 = word_tokenize(text2.lower())
        lemmatizer = WordNetLemmatizer()
        tokens1 = [lemmatizer.lemmatize(token) for token in tokens1]
        tokens2 = [lemmatizer.lemmatize(token) for token in tokens2]

        # remove stop words
        stop_words = stopwords.words('english')
        tokens1 = [token for token in tokens1 if token not in stop_words]
        tokens2 = [token for token in tokens2 if token not in stop_words]

        # convert the descriptions into bag of words form
        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform([', '.join(tokens1),', '.join(tokens2)])
        # Calculate the cosine similarity between the vectors
        cosine_sim = cosine_similarity(vectors[0],vectors[1])

        return cosine_sim

    """This function gives the most similar skill in the organisation, if we can't find an exact match"""
    def most_similar_skill_in_org(self, skill: str, returnDict = False):
        sim_dict = {}
        sim_skills = read_db('skillsDB.json')
        for candidate_skill in sim_skills:
            sim_dict[candidate_skill["skill"]] = (self.skill_comparator(skill, candidate_skill["skill"]))
        result = sorted(sim_dict.items(),key=lambda x: x[1])
        if returnDict:
            return dict(result)
        return result[len(sim_dict)-1]

    """Function finds employees with closest skill, depth means the function will look for the 5th closest skill
    before giving up if the other most closest are not found"""
    def find_closest_employee(self, skill: str, depth = 5):
        emps = read_db('mockdatabase.json')
        closest_employees = []

        skill_scores = list(self.most_similar_skill_in_org(skill,returnDict = True).keys())
        skill_scores.reverse()
        closest_skills = skill_scores[0:5]
        print(closest_skills)
        i = 0
        while(i < depth):
            for emp in emps:
                for s in emp["skills"]:
                    print(s + " " + closest_skills[i])
                    print(closest_skills[i])
                    if s == closest_skills[i]:
                        closest_employees.append(emp["name"])
            if len(closest_employees) > 0:
                return closest_employees
            else:
                i += 1
        return False










jobMatcher = JobMatcher()
#print(jobMatcher.find_closest_employee("python")) -> ['Alex Johnson', 'Daniel Kim', 'Emma Davis', 'Ava Jackson', '...
