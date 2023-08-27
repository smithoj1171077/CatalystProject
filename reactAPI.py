from flask import Flask
from DBQuery import skill_query
from JobMatcher import JobMatcher
app = Flask(__name__)
jobMatcher = JobMatcher()
@app.route('/skill_query/<skill>')
@app.route('/get_skills/<job_name>')



