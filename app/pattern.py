import string
from enum import Enum

from app.ontologygenerator import Generator, Ontology

class Constructor:
	def __init__(self, nlp, user_stories):
		self.nlp = nlp
		self.user_stories = user_stories

	def make(self, ontname):
		pf = PatternFactory(self)

		self.onto = Ontology(ontname)

		for us in self.user_stories:
			pf.make_patterns(us)

		g = Generator(self.onto.classes, self.onto.relationships)
		return g.prt(self.onto)
		
	def get_main_verb(self, us):
		if not us.means.main_verb.phrase:
			av = string.capwords(us.means.main_verb.main.lemma_)
		else:
			av = ""
			for p in us.means.main_verb.phrase:
				av += string.capwords(p.lemma_)		
		return av

	def get_direct_object(self, us):
		return string.capwords(us.means.direct_object.main.lemma_)
	

	def remove_duplicates(self, arr):
		li = list()
		li_add = li.append
		return [ x for x in arr if not (x in li or li_add(x))]

	
	def t(self, token):
		return token.main.text


class PatternFactory:
	def __init__(self, constructor):
		self.constructor = constructor

	def make_patterns(self, us):
		pi = PatternIdentifier()
		pi.identify_patterns(us)

		# WIP Prints all patterns that are found
		#print("US", us.number, ">", pi.found_patterns)

		self.constructor.onto.get_class_by_name('Person')
		self.constructor.onto.get_class_by_name('FunctionalRole', 'Person')

		for fp in pi.found_patterns:
			self.construct_pattern(us, fp)

		return self

	def construct_pattern(self, us, pattern):
		action_v = self.constructor.get_main_verb(us)		
		direct_obj = self.make_direct_object(us)

		if pattern == Pattern.desc_func_adj:
			func_role = self.make_subtype_functional_role(us)
		else:
			func_role = self.make_functional_role(us)


	def make_subtype_functional_role(self, us):
		func_role = string.capwords(us.role.functional_role.main.lemma_)
		subtype = ""		
		compound_adj = []

		for token in us.role.functional_role.adjectives:
			if token.dep_ == 'compound':
				compound_adj.append(token)
		for ca in compound_adj:
			subtype += string.capwords(ca.lemma_)

		self.constructor.onto.get_class_by_name(func_role, 'FunctionalRole')
		self.constructor.onto.get_class_by_name(subtype + func_role, func_role)
		self.constructor.onto.get_class_by_name(subtype)
		self.make_has_relationship(subtype, func_role, subtype + func_role)
		self.make_can_relationship(subtype + func_role, self.constructor.get_main_verb(us), self.constructor.get_direct_object(us))

		return func_role

	def make_functional_role(self, us):
		func_role = string.capwords(us.role.functional_role.main.lemma_)
		self.constructor.onto.get_class_by_name(func_role, 'FunctionalRole')
		self.make_can_relationship(func_role, self.constructor.get_main_verb(us), self.constructor.get_direct_object(us))
		return func_role

	def make_direct_object(self, us):
		direct_obj = self.constructor.get_direct_object(us)
		self.constructor.onto.get_class_by_name(direct_obj)
		return direct_obj

	def make_can_relationship(self, pre, rel, post):
		self.make_relationship(pre, rel, post, 'can')

	def make_has_relationship(self, pre, rel, post):
		self.make_relationship(pre, rel, post, 'has')

	def make_relationship(self, pre, rel, post, connector):
		self.constructor.onto.new_relationship(pre, connector + rel, post)	

class PatternIdentifier:
	def __init__(self):
		self.found_patterns = []

	def identify_patterns(self, story):
		if self.identify_desc_func_adj(story):
			self.found_patterns.append(Pattern.desc_func_adj)
		else:
			self.found_patterns.append(Pattern.basic)		

	def identify_desc_func_adj(self, story):
		if story.role.functional_role.adjectives:
			for token in story.role.functional_role.adjectives:
				if token.dep_ == 'compound':
					return True
		return False

class Pattern(Enum):
	basic = 0
	desc_func_adj = 1
