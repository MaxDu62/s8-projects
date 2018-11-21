
import xml.sax
import cStringIO
import sys

ELEMENT_DELIMITER = "|"
KEY_VALUE_DELIMITER = ":"
END_OF_LINE = "\n"

file = None

class ItemSet(object):

	def __init__(self):
		pass

	def append(self, key, value, pattern, index=-1):
		pass

	def newLine(self):
		pass

	def getData(self):
		return list()

class ItemSetFirstPart(ItemSet):

	def __init__(self):
		super(ItemSetFirstPart, self).__init__()

		self.__data = [""]
		self.__pattern_in_last = False

	def append(self, key, value, pattern):
		if (key[0] == 'a' and key[1] == 'u'):
			if value == pattern:
				self.__pattern_in_last = True
				
			self.__data[-1] += value + ELEMENT_DELIMITER

	def newLine(self):
		if self.__pattern_in_last:
			self.__data[-1] += END_OF_LINE
			self.__data.append("")
		else:
			self.__data[-1] = ""

		self.__pattern_in_last = False

	def getData(self):
		return self.__data

class ItemSetSecondePart(ItemSet):

	def __init__(self):
		super(ItemSetSecondePart, self).__init__()
		self.__previous_one_letter = False
		self.__previous = ""

	def append(self, key, value, pattern):
		if (key[0] == 'a' and key[1] == 'u'):

			if value[0].isupper() or not (value[0] < 128):
				file.write(ELEMENT_DELIMITER)

			file.write(value.encode('utf-8').strip()) 

			self.__previous = value.encode('utf-8').strip()

	def newLine(self):
		file.write('\n')

class ItemSetSecondePart2(ItemSet):

	def __init__(self):
		super(ItemSetSecondePart2, self).__init__()
		self.__data = []
		self.__pattern_in_last = False

	def getResult(self, pattern):
		for line in file:
			if pattern in line:
				self.__data.append(line[1:-1])

	def getData(self):
		return self.__data

class ItemSetExtract(ItemSet):

	liste = ['a','t','y']
		
	def __init__(self):
		super(ItemSet, self).__init__()

	def append(self, key, value, pattern):
		if key[0] in self.liste:
			file.write('<')
			file.write(key)
			file.write('>')
			file.write(value.encode('utf-8'))
			file.write('</')
			file.write(key)
			file.write('>')

	def newLine(self):
		file.write('\n')

class TransformateurXML(xml.sax.ContentHandler, object):

	ITEMSET_NAME = ["article","inproceedings"]

	def __init__(self, pattern="", itemSetClass=""):
		self.__itemSet = itemSetClass
		self.__balise_name = None
		self.__current_balise = None
		self.__parser = xml.sax.make_parser()
		self.__pattern = pattern
	
	def startElement(self, name, attrs):
		try:
			self.__balise_name = self.ITEMSET_NAME.index(name)
			file.write('<')
			file.write(name)
			file.write(' key="')
			file.write(attrs['key'])
			file.write('">')
		except ValueError:
			index_value = None

		self.__current_balise = name
		
	def endElement(self, name):
		if name in self.ITEMSET_NAME:
			self.__balise_name = None
			file.write('</')
			file.write(name)
			file.write('>\n')
	
	def characters(self, data):
		if (data != END_OF_LINE) and (self.__balise_name != None):
			self.__itemSet.append(self.__current_balise, data, self.__pattern)
			
	def parse(self, file_dir):
		self.__parser.setContentHandler(self)
		self.__parser.parse(file_dir)
		return self.__itemSet

	def getResult(self):
		result = []
		x = []
		i = 0
		for items in self.__itemSet.getData():
			if self.__pattern in items:
				for item in items.split(ELEMENT_DELIMITER):
					if item != self.__pattern and item != END_OF_LINE:
						result.append(item)

		while i < len(result):
			x.append(result[i])
			i += 1
			while i < len(result) and not result[i][0].isupper():
				x[-1] += result[i]
				i += 1
			if x.index(x[-1]) < len(x)-1:
				x.pop()

                print("\n\n")
		print('"%s" has %d coauthors:' % (self.__pattern, len(x)))
		for i in x:
			print("-" + i)

	def pullResult(self):
		self.__itemSet.getResult(pattern=self.__pattern)

class ExtracteurXML(TransformateurXML):

	def __init__(self, *args, **kwargs):
		super(ExtracteurXML, self).__init__(*args, **kwargs)
		self.__pattern = kwargs['pattern']

	def startDocument(self):
		file.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
		file.write('<!DOCTYPE dblp SYSTEM "extract.dtd">\n')
		file.write('<extract>\n')
		file.write('<name>')
		file.write(self.__pattern)
		file.write('</name>\n')

	def endDocument(self):
		file.write('</extract>')

if len(sys.argv) == 1:
	print("Question 1:  ./dblp-prof-linux2 -name name dblp.xml")
	print("Question 2a: ./dblp-prof-linux2 -out file.gob dblp.xml")
	print("Question 2b: ./dblp-prof-linux2 -name name -in file.gob")
	print("Question 3:  ./dblp-prof-linux2 -name name dblp.xml -extract file.gob")
	print("Use *.gob or resultSet.txt as output file for gitignore")

elif sys.argv[1] == '-name':

	if sys.argv[3] == '-in':
		t = TransformateurXML(pattern=sys.argv[2], itemSetClass=ItemSetSecondePart2())
		file = open(sys.argv[4], 'r')
		t.pullResult()
		t.getResult()
		file.close()
	
	elif sys.argv[4] == '-extract':
		t = ExtracteurXML(pattern=sys.argv[2], itemSetClass=ItemSetExtract())
		file = open(sys.argv[5], 'w')
		t.parse(file_dir=sys.argv[3])
		file.close()

	else:
		t = TransformateurXML(pattern=sys.argv[2], itemSetClass=ItemSetFirstPart())
		t.parse(file_dir=sys.argv[3])
		t.getResult()

else:

	file = open(sys.argv[2], 'w')
	t = TransformateurXML(itemSetClass=ItemSetSecondePart())
	t.parse(file_dir=sys.argv[3])
	file.close()

