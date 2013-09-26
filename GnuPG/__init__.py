import os
import os.path
import subprocess
import shutil
import random
import string

def public_keys( keyhome ):
	cmd = '/usr/bin/gpg --homedir %s --list-keys --with-colons' % keyhome
	p = subprocess.Popen( cmd.split(' '), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	p.wait()
	keys = list()
	for line in p.stdout.readlines():
		if line[0:3] == 'uid' or line[0:3] == 'pub':
			if ('<' not in line or '>' not in line):
				continue
			key = line.split('<')[1].split('>')[0]
			if keys.count(key) == 0:
				keys.append(key)
	return keys

# confirms a key has a given email address
def confirm_key( content, email ):
	tmpkeyhome = ''

	while True:
		tmpkeyhome = '/tmp/' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(12))
		if not os.path.exists(tmpkeyhome):
			break

	os.mkdir(tmpkeyhome)
	p = subprocess.Popen( ['/usr/bin/gpg', '--homedir', tmpkeyhome, '--import', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE )
	result = p.communicate(input=content)[1]
	confirmed = False

	for line in result.split("\n"):
		if 'imported' in line and '<' in line and '>' in line:
			if line.split('<')[1].split('>')[0].lower() == email.lower():
				confirmed = True
				break
			else:
				break # confirmation failed

	# cleanup
	shutil.rmtree(tmpkeyhome)

	return confirmed

# adds a key and ensures it has the given email address
def add_key( keyhome, content ):
	p = subprocess.Popen( ['/usr/bin/gpg', '--homedir', keyhome, '--import', '--batch'], stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE )
	p.communicate(input=content)
	p.wait()

def delete_key( keyhome, email ):
	from email.utils import parseaddr
	result = parseaddr(email)

	if result[1]:
		# delete all keys matching this email address
		p = subprocess.Popen( ['/usr/bin/gpg', '--homedir', keyhome, '--delete-key', '--batch', '--yes', result[1]], stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
		p.wait()
		return True

	return False

class GPGEncryptor:
	def __init__(self, keyhome, recipients = None, charset = None):
		self._keyhome = keyhome
		self._message = ''
		self._recipients = list()
		self._charset = charset
		if recipients != None:
			self._recipients.extend(recipients)

	def update(self, message):
		self._message += message

	def encrypt(self):
		p = subprocess.Popen( self._command(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,stderr=subprocess.PIPE )
		encdata = p.communicate(input=self._message)[0]
		return encdata

	def _command(self):
		cmd = ["/usr/bin/gpg", "--trust-model", "always", "--homedir", self._keyhome, "--batch", "--yes", "--pgp7", "--no-secmem-warning", "-a", "-e"]

		# add recipients
		for recipient in self._recipients:
			cmd.append("-r")
			cmd.append(recipient)

		# add on the charset, if set
		if self._charset:
			cmd.append("--comment")
			cmd.append('Charset: ' + self._charset)

		return cmd
