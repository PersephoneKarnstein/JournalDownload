# -*- coding: utf-8 -*-
import requests, re, mechanize, os, sys
from bs4 import BeautifulSoup
from itertools import ifilterfalse
from PyPDF2 import PdfFileWriter, PdfFileReader, merger, PdfFileMerger
import numpy as np

br = mechanize.Browser() #allows me to pretend I'm actually using the browser
						 #(circumventing nasty troubles with cookies)
br.set_handle_robots(False) #be manly, impulsive, and ignore robot.txt

url = raw_input("Enter the url of the journal's issue directory: ")
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

print("""
\documentclass{article}

\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{tabu}
\usepackage{longtable}
\usepackage[margin=1in]{geometry}

\\newcommand*{\\titleTH}{\\begingroup 
\\raggedleft
\\vspace*{\\baselineskip}

{\Large Table of Contents}\\\[0.167\\textheight]

{\Huge """ + journaltitle + """ }\\\[\\baselineskip]

{\Large \\textit{""" + journalsubtitle + """}}\par

\\vspace*{3\\baselineskip}
\endgroup}


\\begin{document}

\\titleTH


\\begin{center}
\\begin{longtabu} to \\textwidth {X[0.25,c]X[4,l]X[.5,r]}

""")

for aut in soup.find_all(class_="content"): #gets numbers of listed volumes
	foo = aut.a
	if foo is not None:
		try:
			soupp = BeautifulSoup(str(foo))
			volnum = soupp.a['name']
			volnum = re.sub("\D", "", volnum)
			try: volumes.append(int(volnum))
			except ValueError: volumes.append(volnum)
		except KeyError: pass
	else: pass

rofls = []
weirds = []

for roflcopter in soup.find_all(class_="content"): #need to open the right link - it's harder than it looks
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


for vol in volumes:
	volurl = "http://www.tandfonline.com" + str(therofl) + "?open=" + str(vol) + "&repitition=" + str(weirds[volumes.index(vol)]) + "#vol_" + str(vol)
	r = requests.get(volurl)
	sloup = BeautifulSoup(r.text)

	print("\multicolumn{2}{l}{\\textbf {\Large Volume " + str(vol) + "}}& \\\ ")
	print("\hline \\\ ")

	accesslist = []
	issuelist = []
	issuenum = []

	for icon in sloup.find_all(class_="accessIcon"):
		# print icon
		# print ""
		soupp = BeautifulSoup(str(icon.img))
		tag = soupp.img
		if tag is not None:
			access = tag['title'] #checks whether or not I have access to each issue
			if access == "Full Access":
				accesslist.append(True)
			else: 
				accesslist.append(False)
				print("%I don't see access")
		else: pass

	for link in sloup.find_all(class_="issueInfo"):
	    issuelist.append("http://www.tandfonline.com"+link.a.get('href'))
	    issuenum.append(link.a.get_text())
	
	if len(accesslist)>len(issuelist):
		accesslist = accesslist[-len(issuelist):]

	for issue in np.arange(len(issuelist)):
		if accesslist[int(issue)] == True:
			issueurl = issuelist[issue]
			r = requests.get(issueurl)
			souppy = BeautifulSoup(r.text)

			br.open(issuelist[issue])
			print ("\multicolumn{2}{l}{\\textbf{\large "+issuenum[issue].lstrip()+"}}& \\\ ")

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


			for elem in np.arange(len(names)):
				try: print( "&{\\normalsize{" + names[int(elem)] + "}} & {" + authors[int(elem)][1] + "}\\\ ")
				except IndexError: print( "&{\\normalsize{" + names[int(elem)] + "}} & { - }\\\ ")
				print( "&{\small {\it " + authors[int(elem)][0] + "}} & \\\ \\\ ")
				print("")
				
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

				curfirst = (input_file.getPage(1)).extractText()
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

			
print """
\end{longtabu}
\end{center}

\end{document}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%% Download Complete %%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%It's good practice to log out of and then back%%%% 
%%%%%into AirBears after each completed download.%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"""
			


































			