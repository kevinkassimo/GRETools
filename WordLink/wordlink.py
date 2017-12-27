#!/usr/bin/env python3

import sys
import json
from os.path import expanduser

class WordLink:
	msg_prompt = '(wl)>> '
	msg_help = """
Syntax:

??              help
++ word         add this word
-- word         remove this word
+ word1 word2   link 2 words
- word1 word2   remove link between words
? word          query word link
exit            exit program
"""

	def __init__(self, path):
		self.file = None
		self.data = None
		self.path = path
		self.do_load_db()
		self.do_cmdloop()

	def do_welcome(self):
		print("""
			WordLink (from GRETools)
			[✓] A tool for you to collect and check related words (useful for AWA)
			Type ?? for help
			""", end="")

	def do_cmdloop(self):
		self.do_prompt()
		for line in sys.stdin:
			self.do_handle(line)
			self.do_prompt()

	def do_load_db(self):
		try:
			self.file = open(self.path, 'a+')
			self.file.seek(0)
			try:
				self.data = json.load(self.file)
			except:
				self.data = {
					'entries': {}
				}
				self.do_update_db()
		except (e):
			print("[X] Cannot load wordlink. File might be corrupted or permission denied")
			raise e
			sys.exit()

	def do_update_db(self):
		try:
			self.file.seek(0)
			with open(self.path, 'w+') as output_file:
				json.dump(self.data, output_file)
		except:
			print("[X] Cannot save wordlink. File might be corrupted or permission denied")
			sys.exit()

	def do_prompt(self,):
		print(self.msg_prompt, end="")
		sys.stdout.flush()

	def do_help(self, args):
		print(self.msg_help)

	def do_add(self, args):
		if len(args) < 1:
			self.err_too_few_args(1, "Cannot add word: ")
		else:
			word = args[0]
			if word in self.data['entries']:
				self.warn_custom("word %s already exist" % (word))
			else:
				self.data['entries'][word] = {}
				self.do_update_db()

	def do_del(self, args):
		if len(args) < 1:
			self.err_too_few_args(1, "Cannot delete word: ")
		else:
			word = args[0]
			if word not in self.data['entries']:
				self.warn_custom('Nothing to remove')
			else:
				for link_word in self.data['entries'][word]:
					self.data['entries'].get(link_word, {}).pop(word, None)
				self.data['entries'].pop(word, None)
				self.do_update_db()

	def do_link(self, args):
		if len(args) < 2:
			self.err_too_few_args(2, "Cannot link: ")
		else:
			word_1 = args[0]
			word_2 = args[1]
			if word_1 not in self.data['entries']:
				self.data['entries'][word_1] = {}
			if word_2 not in self.data['entries']:
				self.data['entries'][word_2] = {}
			self.data['entries'][word_1][word_2] = 0
			self.data['entries'][word_2][word_1] = 0
			self.do_update_db()

	def do_delink(self, args):
		if len(args) < 2:
			self.err_too_few_args(2, "Cannot remove link: ")
		else:
			word_1 = args[0]
			word_2 = args[1]
			if word_1 not in self.data['entries']:
				self.warn_custom("'%s' not added" % (word_1))
				return
			if word_2 not in self.data['entries']:
				self.warn_custom("'%s' not added" % (word_2))
				return
			self.data['entries'][word_1].pop(word_2, None)
			self.data['entries'][word_2].pop(word_1, None)
			self.do_update_db()

	def do_find(self, args):
		if len(args) < 1:
			self.err_too_few_args(1, "Cannot find word: ")
		else:
			word = args[0]
			if word not in self.data['entries']:
				self.warn_custom("Word '%s' not recorded" % (word))
			else:
				for link_word in self.data['entries'].get(word, {}).keys():
					print(link_word + ' ')

	def do_exit(self, args):
		print("Bye")
		sys.exit()

	def do_handle(self, arg):
		args = self.do_parse(arg)
		if len(args) <= 0:
			pass
		else: # simulate switch using dict
			dispatch = {
				'??': self.do_help,
				'+': self.do_link,
				'-': self.do_delink,
				'?': self.do_find,
				'++': self.do_add,
				'--': self.do_del,
				'exit': self.do_exit,
				'quit': self.do_exit,
				'q': self.do_exit
			}.get(args[0], self.err_invalid_cmd)
			dispatch(args[1:])

	def do_parse(self, arg):
		return arg.split()

	def err_invalid_cmd(self, args):
		print("[X] Command not found: ", *args)

	def err_too_few_args(self, expect_count, msg=""):
		print("[X] " + msg + "Too few arguments, expect " + str(expect_count))

	def err_custom(self, err_msg):
		print("[X] " + err_msg)

	def warn_custom(self, warn_msg):
		print("[!] " + warn_msg)


def main():
	WordLink(expanduser('~/.gretools/wordlink.gretools'))

if __name__ == '__main__':
	main()