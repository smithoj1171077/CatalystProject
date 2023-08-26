from ChatGPT import ChatGPT
class JobMatcher:
    #the standard system_msg for this class
    sys_msg = "You are a system knowledgable about the skill requirments for any job"
    #the output format
    outputFormat = "Produce a python dictionary of the 10 most important skills needed and ranking in importance for "
    def __init__(self, employees: [{str: [str]}], jobs: [str]):
        self.employees = employees
        self.jobs = jobs
        self.job_skills = {}
        self.ai = ChatGPT(JobMatcher.sys_msg, JobMatcher.outputFormat)
    def getSkills(self, job: str):
        user_msg = self.outputFormat + job

        # check if the job is already in the system and create a response
        if job not in self.job_skills.keys():
            self.job_skills[job] = self.ai.getChatGPTResponse(user_msg)
            response = self.job_skills[job]
        else:
            response = self.job_skills[job]
        return response
      