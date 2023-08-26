from ChatGPT import ChatGPT
import re
import json
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')


class JobMatcher:
    #the standard system_msg for this class
    sys_msg = "You are a system knowledgable about the skill requirments for any job"
    #the output format for the skill finder
    output_format_finder = "Produce a python dictionary of the 10 most important skills " \
                   "needed as the key, and as the value: number ranking in importance for "
    #The output format for the skill comparator
    output_format_comparator = "Produce a 300 word description, including what industries use it, of the following skill "
    def __init__(self, employees: [{str: [str]}] = [], jobs: [str] = []):
        self.employees = employees
        self.jobs = jobs
        self.job_skills = {}
        self.skill_finder_ai = ChatGPT(JobMatcher.sys_msg, JobMatcher.output_format_finder)
        self.skill_comparator_ai = ChatGPT(JobMatcher.sys_msg, JobMatcher.output_format_comparator)
        self.skill_descriptions = {}
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

    """This function gets chat GTP to write 150 words describing each skill, and then a cosine similarity is 
    produced between the two texts.
    This allows a comparable, interpretable and relatively consistent similarity score to be generated for each skill"""
    def skill_comparator(self, skill_needed: str, candidate_skill: str) -> float:
        for skill in (skill_needed, candidate_skill):
            # get a description of both skills, check if there is already a chatgpt description saved
            if skill not in self.job_skills.keys():
                self.job_skills[skill] = self.skill_comparator_ai.getChatGPTResponse(
                    JobMatcher.output_format_comparator + skill
                )
        needed_desc = self.job_skills[skill_needed]
        candidate_desc = self.job_skills[candidate_skill]
        #print("needed: " + needed_desc)
        #print("candidate: " + candidate_desc)
        return self.cosine_sim(needed_desc, candidate_desc)



    def cosine_sim(self, text1, text2):
        # perform tokenization and lemmatization on the texts
        tokens1 = word_tokenize(text1)
        tokens2 = word_tokenize(text2)
        lemmatizer = WordNetLemmatizer()
        tokens1 = [lemmatizer.lemmatize(token) for token in tokens1]
        tokens2 = [lemmatizer.lemmatize(token) for token in tokens2]

        # remove stop words
        stop_words = stopwords.words('english')
        tokens1 = [token for token in tokens1 if token not in stop_words]
        tokens2 = [token for token in tokens2 if token not in stop_words]
        print(tokens1)
        print(tokens2)
        # convert the descriptions into bag of words form
        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform([', '.join(tokens1),', '.join(tokens2)])
        # Calculate the cosine similarity between the vectors
        cosine_sim = cosine_similarity(vectors[0],vectors[1])

        return cosine_sim









jobMatcher = JobMatcher()
#print(jobMatcher.getSkills("Financial analyst")) # -> output {'Financial Modeling': 1, 'Data Analysis': 2, ... }
#print(jobMatcher.getSkills("SalesForces implementation"))
#print(jobMatcher.skill_comparator("risk management","history teaching")) -> 0.1413
#jobMatcher.skill_comparator("risk management","data analysis")) -> 0.147
print(jobMatcher.skill_comparator("risk management","accounting"))
print(jobMatcher.skill_comparator("risk management","security guard"))
#print(jobMatcher.skill_comparator("java programming","bartending")) -> 0.07
#print(jobMatcher.skill_comparator("java programming","python programming")) -> 0.439

text1 = "Java programming is a highly in-demand skill in the technology industry. It is an object-oriented programming language that is widely used to develop various applications and software solutions. Proficiency in Java requires a strong understanding of its syntax, principles, and concepts, such as classes, objects, inheritance, and polymorphism."\

"A skilled Java programmer has the ability to write clean, efficient, and modular code. They have knowledge of data structures and algorithms, which enables them to design and implement optimized solutions. They are experienced in using Java frameworks, such as Spring or Hibernate, to build robust and scalable applications."\

"Moreover, Java programmers possess problem-solving skills, as they often encounter complex programming challenges and bugs that require analytical thinking and logical reasoning to overcome. They also have a good understanding of software development practices, including version control, testing, and debugging."\

"With a solid foundation in Java programming, individuals can pursue various career paths, ranging from software development, web application development, mobile app development, and even systems programming."

text2 =  "Bartending requires a unique blend of skills, making it a dynamic and versatile profession in the hospitality industry. Firstly, a bartender must possess excellent communication skills to engage customers,"\
    "take orders, and provide friendly and efficient service. They need to be adept at multitasking, as they may be required to prepare multiple orders"\
    "simultaneously while maintaining accuracy and quality. Attention to detail is crucial for bartenders to carefully measure ingredients,"\
    "mix cocktails, and garnish beverages to create visually appealing drinks. Moreover, a good bartender must have a solid knowledge of various "\
    "alcoholic and non-alcoholic beverages, being able to suggest suitable options to customers based on their preferences and make recommendations accordingly. "\
    "Time management skills are also essential in organizing inventory, restocking supplies, and managing the overall flow of the bar operation. "\
    "A responsible bartender should prioritize safety and enforce responsible alcohol consumption. Lastly, being able to maintain a friendly and welcoming"\
    "atmosphere, handle stressful situations calmly, and adapt to fast-paced environments are additional qualities that contribute to a successful career in bartending."
#print(jobMatcher.cosine_sim(text1, text2))