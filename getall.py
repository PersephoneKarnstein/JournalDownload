# -*- coding: utf-8 -*-
import requests, re, mechanize, os, sys, codecs, unicodedata, getopt, os.path
from bs4 import BeautifulSoup
from itertools import ifilterfalse
from PyPDF2 import PdfFileWriter, PdfFileReader, merger, PdfFileMerger
import numpy as np

def get_all(latexfile='latextableofcontents.txt', url, volstart='newest', volstop='oldest', downloadall='True'):

	r = requests.get(url)
	soup = BeautifulSoup(r.text)

	journaltitlefull = soup.title.get_text().split(":: ")[1]
	if ": " in journaltitlefull:
		journaltitle = journaltitlefull.split(": ")[0]
		journalsubtitle = journaltitlefull.split(": ")[1]
	else:
		journaltitle = journaltitlefull
		journalsubtitle = ""

	volumes = []
	rofls = []
	weirds = []

	for roflcopter in soup.find_all(class_="content"): #gets numbers of listed volumes
		foo = roflcopter.a
		if foo is not None:
			try:
				soupp = BeautifulSoup(str(foo))
				volnum = soupp.a['name']
				volnum = re.sub("\D", "", volnum)
				try: volumes.append(int(volnum))
				except ValueError: volumes.append(volnum)
			except KeyError: pass
		else: pass

		getvols = []

		if (volstart is not 'newest') or (volstop is not 'oldest'):
			if (volstart is not 'newest') and (volstop is 'oldest'):
				try: getvols = volumes[volumes.index(int(volstart)):]
				except ValueError: print("That is not a valid journal number with which to begin.")

			elif (volstop is not 'oldest') and (volstart is 'newest'):
				try: getvols = volumes[:volumes.index(int(volstop+1))]
				except ValueError: print("That is not a valid journal number with which to end.")

			elif (volstart is not 'newest') and (volstop is not 'oldest'):
				try: getvols = volumes[volumes.index(int(volstart)):volumes.index(int(volstop+1))]
				except ValueError: print("That is not a valid journal number with which to begin or end.")
		
		else: getvols = volumes

		rofl2 = roflcopter.find(class_="volume issueStyleCategory")
		if rofl2 is not None:
			rofl3 = rofl2.get('href')
			rofl3 = rofl3.split("?open=")
			weirdo = rofl3[1].split("&repitition=")
			weirdo = weirdo[1].split('#vol')
			rofls.append(rofl3[0])
			weirds.append(weirdo[0])
		else: pass

	if len(rofls) > 2:
		if (rofls[0] == rofls[1]): therofl = rofls[0] 
		else: print("I'm having some trouble parsing the urls here. The list of issue redirects is: \n" + rofls)
	elif len(rofls) != 0: therofl = rofls[0]
	else: print("I don't see any article urls of the common type...")


	for vol in getvols:
		volurl = "http://www.tandfonline.com" + str(therofl) + "?open=" + str(vol) + "&repitition=" + str(weirds[volumes.index(vol)]) + "#vol_" + str(vol)
		r = requests.get(volurl)
		sloup = BeautifulSoup(r.text)

		print("""
		#####################################
		############# Volume """ + str(vol)) + """ #############
		#####################################
		"""
		gg.write("\multicolumn{2}{l}{\\textbf {\Large Volume " + str(vol) + "}}& \\\ \n")
		gg.write("\hline \\\ \n")

		accesslist = []
		issuelist = []
		issuenum = []
		issuetitles = []

		for volvol in sloup.find_all(class_="volumeIssueList"):
			numiss = []
			for iss in volvol.find_all(class_="indent floatContainer"):
				numiss.append(iss)
			
			if len(numiss) != 0:
				for icon in numiss:
					
					access = icon.find(class_="accessIcon")
					ssoupp = BeautifulSoup(str(access.img))
					tag = ssoupp.img
					# print ssoupp
					# print tag
					# print ""
					accesspr = tag['title'] #checks whether or not I have access to each issue
					if accesspr == "Full Access":
						accesslist.append(True)
					else: 
						accesslist.append(False)
						print("%I don't see access")
					
					try:
						link = icon.find(class_="issueInfo")
						issuelist.append("http://www.tandfonline.com"+link.a.get('href'))
						issuenum.append(link.a.get_text())
					except AttributeError: pass
					
					try:
						title = icon.find(class_="issueTitle").get_text().strip()
						if title is not None:
							issuetitles.append(title)
					except AttributeError: issuetitles.append("")
			else: pass

		# print accesslist, issuelist

				
		if len(accesslist)>len(issuelist):
			accesslist = accesslist[-len(issuelist):] #sometimes there's a random one hanging out at the top which used to trip it up

		if len(issuetitles)>len(issuelist):
			issuetitles = issuetitles[-len(issuelist):]

		for issue in np.arange(len(issuelist)):
			if accesslist[int(issue)] == True:
				issueurl = issuelist[issue]
				r = requests.get(issueurl)
				souppy = BeautifulSoup(r.text)

				br.open(issuelist[issue])
				gg.write("{\\textsc{\large "+issuenum[issue].strip()+ "}} & ")
				print(issuenum[issue].strip())
				if issuetitles[issue] is not "": 
					gg.write("{\\textit{\\textbf{\large "+issuetitles[issue]+ "}}} & \\\ \\\ \n")
					print(issuetitles[issue])
				else: gg.write("& \\\ \\\ \n")

				links = []
				names = []
				authors = []
				pdfnames = []

				for link in souppy.find_all("a", class_="pdf last"):
					links.append('http://www.tandfonline.com'+link.get('href')) 
					#links to pdfs look like this for this site
				
				for name in souppy.find_all("a", class_="entryTitle"):
					bar = name.find('h3')
					if bar is not None:
						foob = bar.i
						if foob is not None:
							bar.i.unwrap() #if there's any italicized text in titles, this fixes it
						else: pass
						pdfnametest = bar.get_text() #get names of articles

						if pdfnametest is not None:
							pdfname = re.sub('&', '\&', pdfnametest)
						else:
							try:
								foo = BeautifulSoup(str(bar)) #because the 'reviews' section is grumpy
								foo = foo.h3
								foo2 = foo.div.extract()
								pdfname = foo.string
								pdfname = re.sub('&', '\&', pdfname)
							except AttributeError: pdfname = "<<<<<Error Getting Article Title>>>>>"
					else: pdfname = ""
					names.append(pdfname)

				for aut in souppy.find_all("h4"):
					markup = str(aut)
					soupy = BeautifulSoup(markup)
					author = soupy.get_text()
					author = re.sub('page', ': page', author) #re-adds a space that was eaten
					author = re.sub('&', '\&', author)
					author = author.split(": pages ")
					if len(author) == 1: 
						try: author = str(author[0]).split(": page ")
						except UnicodeEncodeError: pass
					else: pass
					if len(author[0]) > 3: pass
					else: author[0] = ""
					authors.append(author)
					#this pulls a lot of other random shit from that tag, so we need to trim

				numarts = len(links)
				authors = authors[::-1][0:numarts][::-1] 
				#preserves the null author for the editorial board when such exists

				if bool(downloadall) == True:
					if vol in getvols: ###I want it to still write a table of contents for all volumes if I start in a weird place, just not download them. But it's not.. T_T
						if len(names) != 0:
							for elem in np.arange(len(names)):
								print("Now Downloading")
								try: 
									print(names[int(elem)])
									gg.write( "&{\\normalsize{" + names[int(elem)] + "}} & {" + authors[int(elem)][1] + "}\\\ \n")
								except IndexError: 
									print(names[int(elem)])
									gg.write( "&{\\normalsize{" + names[int(elem)] + "}} & { - }\\\ \n")
								try: 
									print("By "+authors[int(elem)][0])
									gg.write( "&{\small {\it " + authors[int(elem)][0] + "}} & \\\ \\\ \n")
								except IndexError: 
									gg.write( "&{\small {\it " + "}} & \\\ \\\ \n")
								gg.write("\n")
								
								try:
									data = br.open(links[int(elem)]).get_data()
									articleid = "vol"+str(vol).zfill(3)+'-issue'+re.sub("\D", "", str(issuenum[issue]).lstrip()).zfill(2)+'-'+str(elem).zfill(2)+".pdf"

									f = open(articleid,'wb')
									f.write(data)
									f.close()

									#Now hand it off to a shit module that can kinda edit pdfs
									output_file = PdfFileWriter()
									input_file = PdfFileReader(open(articleid, 'rb'))
									num_pages = input_file.getNumPages()

									if len(pdfnames) != 0: 
										previnput = PdfFileReader(open(pdfnames[-1], 'rb'))
										prevnum = int(previnput.getNumPages())
										prevlast = (previnput.getPage(prevnum-1)).extractText()
									else: prevlast = ""

									try: curfirst = (input_file.getPage(1)).extractText()
									except TypeError: 
										print "something fucking weird just happened."
										curfirst = ""
									curfirst = "".join(curfirst.split())
									
									francisclaim = """Conditions of accessand use can be found at http://www.tandfonline.com/page/terms-and-conditions"""
									francisclaim = "".join(francisclaim.split()) #removing possible issues with strangely placed spaces in recovered text

									if francisclaim not in curfirst:		
										if (curfirst != prevlast): #i.e., all is as it should be
											for i in xrange(1, num_pages):					
												output_file.addPage(input_file.getPage(i)) #this is dumb why isn't this built into the module
										else:
											for i in xrange(2, num_pages): #not disclaimer pt 2 but a copy of the last page of previous			
												output_file.addPage(input_file.getPage(i))
									else:
										if (curfirst != prevlast): #is disclaimer pt. 2, but not a copy of the last page of prev
											for i in xrange(2, num_pages):					
												output_file.addPage(input_file.getPage(i)) 
										else: #there was a disclaimer pt.2 AND copy of the last page of prev
											for i in xrange(3, num_pages):					
													output_file.addPage(input_file.getPage(i)) 

									os.remove(articleid)

									output_stream = file(articleid,'wb')
									output_file.write(output_stream)

									output_stream.close()

									pdfnames.append(articleid)
								except IndexError: pass


					    #FIRST WE MAKES A FILE AND THEN WE SAYS FUCK IT AND OVERWRITES IT WITH ITSELF
					    #BECAUSE NOBODY THOUGHT DELETING PAGES IN A SIMPLER WAY WOULD BE USEFUL

						#print('<<<' + names[int(elem)] + ' has been downloaded.>>>')
						#print "" #downloads each article in an issue #we have our article pdfs by the end of this


							issuename = "vol"+str(vol).zfill(3)+'-issue'+re.sub("\D", "", str(issuenum[issue]).lstrip()).zfill(2)+".pdf"

							with open(pdfnames[::-1][0], 'rb') as f2:
								merger = PdfFileMerger()
								merger.merge(position=0, fileobj=f2)
								for artfi in np.arange(int(len(pdfnames)-1))+1:
									with open(pdfnames[::-1][artfi], 'rb') as f:
										merger.merge(position=0, fileobj=f)
								merger.write(open(issuename, 'wb')) 
							            ####currently (if it works) merges with no thought for duplicated
							            ####pages in the reviews section. we can do better.

							for remd in pdfnames: os.remove(remd)
						else: pass #in the list but length 0
					else: #not in the list
						for elem in np.arange(len(names)):
							print "not downloading volume", vol
							try: print( names[int(elem)])
							except IndexError: pass #print( "&{\\normalsize{" + names[int(elem)] + "}} & { - }\\\ ")
							print("BY " + authors[int(elem)][0])
							print("")
				else: #prints all but downloads none
					for elem in np.arange(len(names)):
						try: gg.write( "&{\\normalsize{" + names[int(elem)] + "}} & {" + authors[int(elem)][1] + "}\\\ \n")
						except IndexError: gg.write( "&{\\normalsize{" + names[int(elem)] + "}} & { - }\\\ \n")
						gg.write( "&{\small {\it " + authors[int(elem)][0] + "}} & \\\ \\\ \n")
						gg.write("\n")








url = raw_input("Enter the url of the journal's issue directory: ")

br = mechanize.Browser() #allows me to pretend I'm actually using the browser
						 #(circumventing nasty troubles with cookies)
br.set_handle_robots(False) #be manly, impulsive, and ignore robot.txt

r = requests.get(url)
soup = BeautifulSoup(r.text)

journaltitlefull = soup.title.get_text().split(":: ")[1]
if ": " in journaltitlefull:
	journaltitle = journaltitlefull.split(": ")[0]
	journalsubtitle = journaltitlefull.split(": ")[1]
else:
	journaltitle = journaltitlefull
	journalsubtitle = ""

with codecs.open(latexfile, "a", encoding="utf-8") as gg:

	gg.write("""
	\documentclass{article} \n

	\usepackage[english]{babel} \n
	\usepackage{amsmath} \n
	\usepackage{lmodern} \n
	\usepackage{graphicx} \n
	\usepackage{tabu} \n
	\usepackage{longtable} \n
	\usepackage[margin=1in]{geometry} \n
	\n
	\\newcommand*{\\titleTH}{\\begingroup  \n
	\\raggedleft \n
	\\vspace*{\\baselineskip} \n
	\n
	{\Large Table of Contents}\\\[0.167\\textheight] \n
	\n
	{\Huge """ + journaltitle + """ }\\\[\\baselineskip] \n
	\n
	{\Large \\textit{""" + journalsubtitle + """}}\par \n
	\n
	\\vspace*{3\\baselineskip} \n
	\endgroup} \n
	\n
	\n
	\\begin{document} \n
	\n
	\\titleTH \n
	\n
	\n
	\\begin{center} \n
	\\begin{longtabu} to \\textwidth {X[0.25,c]X[4,l]X[.5,r]} \n

	""")

	volfinished = False
	volstartpr = 9999
	volstoppr = 0


###############################I am here: work from this point
	try: 
		get_all(latexfile='latextableofcontents.txt', url)
		#need to put in something here stopping it if it finishes the whole journal
	
	except mechanize._response.httperror_seek_wrapper:
		
		br.open("https://wlan.berkeley.edu/logout/") #wonder if this works
		print "You have been logged out of AirBears because Taylor&Francis caught on to your nefarious downloading. Log back in for a new IP address and to continue nefariously. \n \n I'll wait..."
		idonotcarewhatyoupress = raw_input("press any key when you're done:") #useful pause
		del idonotcarewhatyoupress #not like we're going to use it

		while (volstoppr < volstartpr) or (volfinished = False): #should only end if the beginning and ending volumes are the same, AND the last full issue downloaded was issue 1
			
			volstartpr = globals()["vol"] #starts with the last gotten volume
			volstoppr = min(globals()["volumes"]) #ends with the earliest volume
			
			try:
				get_all(latexfile='latextableofcontents.txt', url, volstart=volstartpr, volstop=volstoppr, downloadall='True')
			
			except mechanize._response.httperror_seek_wrapper:

				#need to put in log out/log in to airbears step here
				br.open("https://wlan.berkeley.edu/logout/") #wonder if this works
				print "You have been logged out of AirBears because Taylor&Francis caught on to your nefarious downloading. Log back in for a new IP address and to continue nefariously. \n \n I'll wait..."
				

				idonotcarewhatyoupress = raw_input("press any key when you're done:") #useful pause
				del idonotcarewhatyoupress #not like we're going to use it


				lastgotten = globals()["vol"] #the below finds incomplete volumes and removes them
				if globals()["issuename"] == "vol"+str(lastgotten).zfill(3)+'-issue'+re.sub("\D", "", str((globals()['issuenum'])[-1]).lstrip()).zfill(2)+".pdf":
					volfinished = True
				else: 
					volfinished = False
					for remd in globals()["pdfnames"]: #gets rid of unincorperated articles
						if os.access(remd, os.R_OK): os.remove(remd) 
						else: pass
					for voliss in globals()['issuenum']: #gets rid of issues from unfinished volumes
						issuecheck = "vol"+str(lastgotten).zfill(3)+'-issue'+re.sub("\D", "", str(voliss).lstrip()).zfill(2)+".pdf":
						if os.access(issuecheck, os.R_OK): os.remove(issuecheck)
						else: pass






	gg.write("""
		\end{longtabu} \n
		\end{center} \n
		\n
		\end{document} \n
		""")

print("""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%% Download Complete %%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%It's good practice to log out of and then back%%%% 
%%%%%into AirBears after each completed download.%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%""")
	
#############################################################
#############################################################	

# The conversion table {{{1

# The following string contains the translation table.
# The syntax of each line is: <tab> <unicode> <tab> <TeX name>
# Lines not of this form are ignored.
# The TeX name is the control sequence without its leading backslash.

tex_unicode_table = u"""
	â€¦	dots

	Î±	alpha
	Î²	beta
	Î³	gamma
	Î´	delta
	Îµ	epsilon
	Î¶	zeta
	Î·	eta
	Î¸	theta
	Î¹	iota
	Îº	kappa
	Î»	lambda
	Î¼	mu
	Î½	nu
	Î¾	xi
	Ï€	pi
	Ï	rho
	Ïƒ	sigma
	Ï„	tau
	Ï…	upsilon
	Ï†	phi
	Ï‡	chi
	Ïˆ	psi
	Ï‰	omega
	Î“	Gamma
	Î”	Delta
	Î˜	Theta
	Î›	Lambda
	Îž	Xi
	Î 	Pi
	Î£	Sigma
	Î¦	Phi
	Î¨	Psi
	Î©	Omega

	â„“	ell
	â…‹	parr

	â†	leftarrow
	â†‘	uparrow
	â†’	to
	â†“	downarrow
	â†”	leftrightarrow
	â†•	updownarrow
	â‡	Leftarrow
	â‡’	Rightarrow
	â‡”	Leftrightarrow
	â‡š	Lleftarrow
	â‡›	Rrightarrow

	Â¬	neg
	Ã—	times

	âˆ€	forall
	âˆƒ	exists
	âˆ…	emptyset
	âˆˆ	in
	âˆ‰	notin
	âˆ˜	circ
	âˆ§	wedge
	âˆ¨	vee
	âˆ©	cap
	âˆª	cup
	â‰ƒ	simeq
	â‰…	cong
	â‰ 	neq
	â‰¡	equiv
	â‰¤	leq
	â‰¥	geq
	âŠ‚	subset
	âŠƒ	supset
	âŠ†	subseteq
	âŠ‡	supseteq
	âŠ	sqsubset
	âŠ	sqsupset
	âŠ‘	sqsubseteq
	âŠ’	sqsupseteq
	âŠ•	oplus
	âŠ—	otimes
	âŠ™	odot
	âŠ¢	vdash
	âŠ£	dashv
	âŠ¤	top
	âŠ¥	bot
	âŠ¨	vDash
	âŠ©	Vdash
	âŠ¸	multimap
	â‹…	cdot

	â™­	flat
	â™®	natural
	â™¯	sharp

	âŸ¦	llbracket
	âŸ§	rrbracket
	âŸ¨	langle
	âŸ©	rangle
"""

# Translating between Unicode code points and TeX names {{{1

class Translator:
	def __init__ (self):
		self.warned = {}
		self.u2t = {}
		self.t2u = {}
		self.read_string(tex_unicode_table)

	def read_string (self, text):
		lnum = 0
		for line in text.split('\n'):
			lnum = lnum + 1
			if len(line) == 0 or line[0] != u'\t':
				continue
			line = line.split('\t')
			if len(line[1]) != 1 or len(line) < 3:
				sys.stderr.write("invalid data at line %d\n" % lnum)
				continue
			self.u2t[line[1]] = line[2]
			self.t2u[line[2]] = line[1]

	def has_unicode (self, c):
		return self.u2t.has_key(c)
	def to_tex (self, c):
		if self.u2t.has_key(c):
			return self.u2t[c]
		if not warned.has_key(c):
			warned[c] = None
			sys.stderr.write("unknown character: %5d %4x %s\n" % (ord(c), ord(c), unicodedata.name(c)))
		return ""

	def has_tex (self, s):
		return self.t2u.has_key(s)
	def to_unicode (self, s):
		return self.t2u[s]

# Writing TeX code with proper spacing {{{1

class TeXWrite:
	def __init__ (self, file, enc="latin-1"):
		self.str = codecs.lookup(enc)[3](file)
		self.need_space = 0

	def write (self, text):
		if len(text) == 0:
			return
		if self.need_space:
			c = text[0]
			if (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z') or c == '@':
				self.str.write(" ")
			self.need_space = 0
		self.str.write(text)

	def cseq (self, name):
		if name == "":
			return
		self.str.write("\\" + name)
		self.need_space = 1

# The command line {{{1

tex_enc = "latin-1"
action = None
in_fname = None
out_fname = None

def help ():
	print """\
usage: tex-utf8 [options] [input [output]]
  -e, --encoding=ENCODING   use ENCODING for the non-Unicode side
  -h, --help                display this help and exit
  -t, --tex                 translate from Unicode to TeX commands
  -u, --unicode             translate from TeX commands to Unicode\
"""
	sys.exit(0)

opts, args = getopt.getopt(sys.argv[1:], "e:htu",
	["encoding=", "help", "tex", "unicode"])
for (opt,arg) in opts:
	if opt in ("-e", "--encoding"):
		tex_enc = arg
	elif opt in ("-h", "--help"):
		help()
	elif opt in ("-t", "--tex"):
		action = "tex"
	elif opt in ("-u", "--unicode"):
		action = "unicode"
if len(args) >= 1:
	in_fname = args[0]
	if len(args) == 2:
		out_fname = args[1]
	elif len(args) > 2:
		sys.stderr.write("too many arguments\n")
		sys.exit(1)

if action is None:
	sys.stderr.write("no action specified\n")
	sys.exit(1)

trans = Translator()

if in_fname is None:
	in_str = sys.stdin
else:
	in_str = open(in_fname)

if out_fname is None:
	out_str = sys.stdout
else:
	out_str = open(out_fname, "w")

# The main program {{{1

if action == "tex":
	in_str = codecs.lookup("UTF-8")[2](in_str)
	out_str = TeXWrite(out_str, enc=tex_enc)
	
	for line in in_str.readlines():
		for c in line:
			o = ord(c)
			if o < 256:
				out_str.write(c)
			else:
				out_str.cseq(trans.to_tex(c))

elif action == "unicode":
	in_str = codecs.lookup(tex_enc)[2](in_str)
	out_str = codecs.lookup("UTF-8")[3](out_str)

	re_cseq = re.compile(r"\\(?P<name>[a-zA-Z]+) ?")

	for line in in_str.readlines():
		p = q = 0
		m = re_cseq.search(line, q)
		while m:
			name = m.group("name")
			if trans.has_tex(name):
				out_str.write(line[p:m.start()])
				out_str.write(trans.to_unicode(name))
				p = q = m.end()
			else:
				q = m.end()
			m = re_cseq.search(line, q)
		out_str.write(line[p:])



























				

#############################################################
#############################################################



