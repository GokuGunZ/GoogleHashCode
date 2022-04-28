import random
import copy


class Project():
	def __str__(self):
		return self.name

	def __init__(self, name, days, score, best_before):
		self.name = name
		self.days = int(days)
		self.score = int(score)
		self.best_before = int(best_before)
		self.roles = []
		self.ended = None

	def add_role(self, name, level):
		self.roles.append((name, int(level)))

	def ended(self, day):
		self.ended = int(day)


class Contributor():
	def __str__(self):
		return self.name

	def __init__(self, name):
		self.name = name
		self.skills = {}
		self.free_from = 0

	def get_skill(self, name):
		return self.skills.get(name, 0)

	def upgrade_skill(self, name):
		self.skills[name] = self.skills.get(name, 0) + 1

	def set_free_from(self, day):
		self.free_from = int(day)

	def add_skill(self, name, level):
		self.skills[name] = int(level)


class Skill():
	def __str__(self):
		return self.name

	def __init__(self, name):
		self.name = name
		self.contributors = []

	def add_contributor(self, contributor):
		self.contributors.append(contributor)


def is_feasible(prj, skills, contributors):
	mentors = {}  # migliori livelli raggiunti per le skill, skill:level
	team = []  # persone che partecipano al progetto

	required_day_start = prj.best_before + prj.score - 1

	for skill, level in prj.roles:
		# prj.roles è (skill, level)
		min_day_start = -1
		contrib = None
		act_level = -1

		if mentors.get(skill, 0) >= level:
			level -= 1

		if level == 0:
			for pp in contributors:
				pippo = contributors[pp]
				if pippo in team:
					continue

				# pippo è il contributor
				if pippo.get_skill(skill) >= level and pippo.free_from <= required_day_start:
					# pippo può partecipare al progetto
					if min_day_start == -1 or pippo.free_from < min_day_start:
						min_day_start = pippo.free_from
						contrib = pippo
						act_level = pippo.get_skill(skill)
					elif pippo.free_from == min_day_start and pippo.get_skill(skill) < act_level:
						contrib = pippo
						act_level = pippo.get_skill(skill)

		else:

			for pippo in skills[skill].contributors:
				if pippo in team:
					continue

				# pippo è il contributor
				if pippo.get_skill(skill) >= level and pippo.free_from <= required_day_start:
					# pippo può partecipare al progetto
					if min_day_start == -1 or pippo.free_from < min_day_start:
						min_day_start = pippo.free_from
						contrib = pippo
						act_level = pippo.get_skill(skill)
					elif pippo.free_from == min_day_start and pippo.get_skill(skill) < act_level:
						contrib = pippo
						act_level = pippo.get_skill(skill)


		if min_day_start == -1:
			return False

		team.append(contrib)
		for pippo_skill in contrib.skills:
			mentors[pippo_skill] = max(mentors.get(pippo_skill, 0), contrib.get_skill(pippo_skill))

	return team


IN_PATH = 'input_data'
OUT_PATH = 'out_data'

for filename in ['a', 'b', 'c', 'd', 'e', 'f']:
	print(filename)

	with open(f'{IN_PATH}/{filename}.txt', 'r') as f:
		lines = f.readlines()

	projects = {}
	contributors = {}
	skills = {}
	ncontr, nproj = map(int, lines[0].rstrip('\n').split(' '))
	actual_line = 1
	for _ in range(ncontr):
		name, j = lines[actual_line].rstrip('\n').split(' ')
		j = int(j)
		c = Contributor(name)
		contributors[name] = c
		actual_line += 1
		for _ in range(j):
			skill, level = lines[actual_line].rstrip('\n').split(' ')
			actual_line += 1
			c.add_skill(skill, level)
			if skill in skills:
				skills[skill].add_contributor(c)
			else:
				skills[skill] = Skill(skill)
				skills[skill].add_contributor(c)
	for _ in range(nproj):
		name, days, score, best_before, j = lines[actual_line].rstrip('\n').split(' ')
		j = int(j)
		p = Project(name, days, score, best_before)
		projects[name] = p
		actual_line += 1
		for _ in range(j):
			skill, level = lines[actual_line].rstrip('\n').split(' ')
			actual_line += 1
			p.add_role(skill, level)

	best_score = 0
	best_out = []
	og_projects = copy.deepcopy(projects)
	og_contributors = copy.deepcopy(contributors)
	og_skills = copy.deepcopy(skills)
	for _ in range(3):
		projects = copy.deepcopy(og_projects)
		contributors = copy.deepcopy(og_contributors)
		skills = copy.deepcopy(og_skills)
		out = []
		score = 0
		projects_left = projects
		last_lenght = len(projects) + 1
		while last_lenght > len(projects) and len(projects) > 0:
			last_lenght = len(projects)
			keys = list(projects.keys())
			random.shuffle(keys)
			for nn in keys:
				prj = projects[nn]

				team = is_feasible(prj, skills, contributors)
				if not team:
					continue
				else:
					del projects_left[nn]

				# eventualmente miglioro le skill
				for i, role in enumerate(prj.roles):
					skill, level = role
					if team[i].get_skill(skill) <= level:
						team[i].upgrade_skill(skill)

				# aggiorno il tempo di fine
				end_time = prj.days + max(i.free_from for i in team)
				for i in team:
					i.set_free_from(end_time)

				score += min(prj.score - (end_time - prj.best_before), prj.score)

				out.append(prj.name)
				team = ' '.join(i.name for i in team)
				out.append(team)
			projects = dict(projects_left)

		if score > best_score:
			print(score)
			best_score = score
			best_out = out

	fout = ''
	fout += str(len(out)//2) + '\n'
	for i in best_out:
		fout += i + '\n'

	with open('out_data' + filename + '.txt', 'w') as fh:
		fh.write(fout)