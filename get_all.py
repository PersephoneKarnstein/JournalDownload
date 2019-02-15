# -*- coding: utf-8 -*-
import requests, re, mechanize, os, sys, codecs, unicodedata, getopt, os.path, getpass
from bs4 import BeautifulSoup
from itertools import ifilterfalse
from PyPDF2 import PdfFileWriter, PdfFileReader, merger, PdfFileMerger
import numpy as np
from urllib2 import HTTPError
from httplib import IncompleteRead

def get_all(url, latexfile='latextableofcontents.txt', volstart='newest', volstop='oldest', downloadall='True'):

	r = br.open(url)
	soup = BeautifulSoup(r)

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

		globals()["volumes"] = volumes

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


	for volute in np.arange(len(getvols)):
		vol = getvols[volute] #having my cake and eating it too
		if volute > 0:
			closeurl = "http://www.tandfonline.com" + str(therofl) + "?close=" + str(volute-1) + "&repitition=" + str(weirds[volumes.index(vol)]) + "#vol_" + str(volute-1)
			br.open(closeurl)
		else: pass
		volurl = "http://www.tandfonline.com" + str(therofl) + "?open=" + str(vol) + "&repitition=" + str(weirds[volumes.index(vol)]) + "#vol_" + str(vol)
		r = br.open(volurl)
		sloup = BeautifulSoup(r)

		print("""
		#####################################
		############# Volume """ + str(vol)) + """ #############
		#####################################
		"""
		gg.write("\multicolumn{2}{l}{\\textbf {\Large Volume " + str(vol) + "}}& \\\ \n")
		gg.write("\hline \\\ \n")

		
		if volute != 0: del issuelist
		else: pass
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
					if (accesspr == "Full Access") or (accesspr == "Free or Open Access"):
						accesslist.append(True)
					elif accesspr == "Partial Access":
						accesslist.append(False)
						print "%Ignoring Partial Access Link"
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

		globals()["issuenum"] = issuenum
		# print accesslist, issuelist

		while True: #switching to full mechanize makes this necessary: make sure you're not reopening old links
			checker = True
			# print issuelist
			for issue in np.arange(len(issuelist)): 
				try:
					# print issuelist[issue]
					# print (issuelist[issue].split("/"))[5], vol
					if int((issuelist[issue].split("/"))[5]) != int(vol): 
						del issuelist[issue]
						checker = False
				except IndexError: 
					checker = False
			if checker == False:
				continue
			else: break

		if len(accesslist)>len(issuelist):
			accesslist = accesslist[-len(issuelist):] #sometimes there's a random one hanging out at the top which used to trip it up

		if len(issuetitles)>len(issuelist):
			issuetitles = issuetitles[-len(issuelist):]

		print issuelist, accesslist
		for issue in np.arange(len(issuelist)):
			if accesslist[int(issue)] == True:
				issueurl = issuelist[issue]
				r = br.open(issueurl)
				souppy = BeautifulSoup(r)

				br.open(issuelist[issue])
				gg.write("{\\textsc{\large "+issuenum[issue].strip()+ "}} & ")
				print("\n \n"+issuenum[issue].strip())
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
						globals()["vol"]=vol
						if len(names) != 0:
							for elem in np.arange(len(names)):
								print("\nNow Downloading")
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
									try:
										data = br.open(links[int(elem)]).get_data()
									except IncompleteRead, e:
										print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
										print "%%%Encountered an IncompleteRead Error%%%"
										print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
										data = e.partial
									articleid = "vol"+str(vol).zfill(3)+'-issue'+re.sub("\D", "", str(issuenum[issue]).lstrip()).zfill(2)+'-'+str(elem).zfill(2)+".pdf"

									f = open(articleid,'wb')
									f.write(data)
									f.close()

									#Now hand it off to a shit module that can kinda edit pdfs
									output_file = PdfFileWriter()
									try: 
										input_file = PdfFileReader(open(articleid, 'rb'))
										num_pages = input_file.getNumPages()
									except IOError: 
										input_file = None
										num_pages = 0

									if len(pdfnames) != 0: 
										previnput = PdfFileReader(open(pdfnames[-1], 'rb'))
										prevnum = int(previnput.getNumPages())
										try:
											prevlast = (previnput.getPage(prevnum-1)).extractText()
										except Exception:
											print "I don't even know, dude..."
											prevlast = ""
									else: prevlast = ""

									try: curfirst = (input_file.getPage(1)).extractText()
									except TypeError: 
										print "something fucking weird just happened."
										curfirst = "notprevlast"
									except Exception: 
										print "something fucking weird just happened."
										curfirst = "not prevlast" #I'd rather have a useless page than a missing one
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

							globals()["pdfnames"] = pdfnames

					    #FIRST WE MAKES A FILE AND THEN WE SAYS FUCK IT AND OVERWRITES IT WITH ITSELF
					    #BECAUSE NOBODY THOUGHT DELETING PAGES IN A SIMPLER WAY WOULD BE USEFUL

						#print('<<<' + names[int(elem)] + ' has been downloaded.>>>')
						#print "" #downloads each article in an issue #we have our article pdfs by the end of this


							issuename = "vol"+str(vol).zfill(3)+'-issue'+re.sub("\D", "", str(issuenum[issue]).lstrip()).zfill(2)+".pdf"
							globals()["issuename"] = issuename

							# print pdfnames
							# print pdfnames[::-1]
							# print pdfnames[::-1][0]

							
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
getall = raw_input("get all articles? (y/n): ")
if getall == 'n':
	startvol = int(raw_input('start with vol: '))
else: startvol = "newest"

br = mechanize.Browser() #allows me to pretend I'm actually using the browser
						 #(circumventing nasty troubles with cookies)
br.set_handle_robots(False) #be manly, impulsive, and ignore robot.txt
br.set_handle_refresh(False)
br.set_handle_redirect(True)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

r = br.open('https://proxy.lib.berkeley.edu/ucblibraryproxyauthorization/login?request_id=')
if "The proxy was unable to pass a cookie to your browser. Please configure your browser to accept cookies" in r.read():
	br.follow_link(text='try again.')
	br.follow_link(text='UC Berkeley CalNet Login')
	CalNet_usr = raw_input("CalNet Username: ")
	CalNet_pswd = getpass.getpass("CalNet Passphrase: ")
	br.select_form(nr=0)
	br.form['username'] = CalNet_usr
	br.form['password'] = CalNet_pswd
	br.submit()

r = br.open(url)
soup = BeautifulSoup(r)

journaltitlefull = soup.title.get_text().split(":: ")[1]
if ": " in journaltitlefull:
	journaltitle = journaltitlefull.split(": ")[0]
	journalsubtitle = journaltitlefull.split(": ")[1]
else:
	journaltitle = journaltitlefull
	journalsubtitle = ""

with codecs.open('latextableofcontents.txt', "a", encoding="utf-8") as gg:

	gg.write(""" 
	\\documentclass{article} \n
	%\usepackage[english]{babel}
	\\usepackage{amsmath}  \n
	\\usepackage{lmodern}  \n
	\\usepackage{fontspec} \n
	\\usepackage[Latin,Greek]{ucharclasses} \n
	\\setmainfont[Ligatures=TeX]{Latin Modern Roman} \n
	\\newfontfamily{\gfsartemisia}{GFS Artemisia} \n
	\\newfontfamily{\gfsbaskerville}{GFS Baskerville} \n
	\\newcommand{\greekfont}{\gfsbaskerville} \n
	\\setTransitionsForLatin{}{} \n
	\\setTransitionsForGreek{\begingroup\greekfont}{\endgroup} \n
	\\usepackage{graphicx}  \n
	\\usepackage{tabu}  \n
	\\usepackage{longtable}  \n
	\\usepackage[margin=1in]{geometry} \n
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
		get_all(url, latexfile='latextableofcontents.txt', volstart=startvol)
		#need to put in something here stopping it if it finishes the whole journal
	
	except HTTPError:
		
		# approx_num_downloads = len(globals()["getvols"]) * len(globals()["issuelist"]) * len(globals()["names"])

		br.open("https://wlan.berkeley.edu/logout/") #wonder if this works
		print "You have been logged out of AirBears because Taylor&Francis caught on to your nefarious downloading. "
		
		# if approx_num_downloads < 800:
		print "Log back in for a new IP address and to continue nefariously. \n \n I'll wait..."
		idonotcarewhatyoupress = raw_input("(press any key when you're done) ") #useful pause
		del idonotcarewhatyoupress #not like we're going to use it
		# else: 
		# 	print "There are a shitton of articles left, it'll be easiest for you to just tell me your login so I can automate this. \n \n (I'll be discreet; check lines >/~=380 if you don't believe me)"
		# 	calnet_id = raw_input("CalNet ID: ")
		# 	calnet_pass = passphrase.passphrase("Passphrase: ")

			########
			########now need to get it to log back in with it
			########



		while (volstoppr < volstartpr) or (volfinished == False): #should only end if the beginning and ending volumes are the same, AND the last full issue downloaded was issue 1
			
			volstartpr = globals()["vol"] #starts with the last gotten volume
			volstoppr = min(globals()["volumes"]) #ends with the earliest volume
			
			try:
				get_all(url, latexfile='latextableofcontents.txt', volstart=volstartpr, volstop=volstoppr, downloadall='True')
			
			except HTTPError: #http://stackoverflow.com/questions/20445390/what-is-the-exception-for-this-error-httperror-seek-wrapper-http-error-404-no

				#need to put in log out/log in to airbears step here
				br.open("https://wlan.berkeley.edu/logout/") #wonder if this works
				print "You have been logged out of AirBears because Taylor&Francis caught on to your nefarious downloading. Log back in for a new IP address and to continue nefariously. \n \n I'll wait..."
				gg.write("""
				%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
				%%%%%%%%%%% You had to log in and out here. %%%%%%%%%%
				%%%%%%%%%%%%%%%%%% Check for repeats %%%%%%%%%%%%%%%%%%
				%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%""")

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
						issuecheck = "vol"+str(lastgotten).zfill(3)+'-issue'+re.sub("\D", "", str(voliss).lstrip()).zfill(2)+".pdf"
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



