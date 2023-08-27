# CatalystProject
The core backend functionalities implemented are the skills finder, which queries chat gtp to get the skills for a input project and the closest employee finder, which finds the employee with the skill most similar
to the needed skill, when the organisation does not have someone with exactly that skill. Also skill query was implemented, allowing the employee skill database to be queried for exact matches. 
The way the similar skill algorithm works is that it calculates a simularity score(cosine simularity) between two lengthy skill descriptions, 
the descriptions are stored in a database so they can be reused in the future. The closest_employee function requires chatGTP to run if a skill is not known to the database, refer to skillsDB.json file for skills
you can use to test the function with without paying for gtp. 
