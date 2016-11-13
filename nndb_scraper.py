from lxml import html
import requests

def getRaceAndGender(name):
	name = name.split()
	query = '+'.join(name)
	searchPage = requests.get('http://search.nndb.com/search/?type=unspecified&query=' + query)
	searchTree = html.fromstring(searchPage.content)
	if len(name) > 1:
		condition = '[contains(.//text(), "' + name[0] + '") and contains(.//text(), "' + name[1] + '")]'
	else:
		condition = '[contains(.//text(), "' + name[0] + '")]'
	personList = searchTree.xpath('//table')[3].xpath('./tr')[1].xpath('./td' + condition)
	if personList:
		personUrl = personList[0].xpath('.//a/@href')[0]
	else:
		return None
	personPage = requests.get(personUrl)
	personTree = html.fromstring(personPage.content)
	race = personTree.xpath('//p/b[text()="Race or Ethnicity:"]/following-sibling::text()')[0].strip()
	gender = personTree.xpath('//p/b[text()="Gender:"]/following-sibling::text()')[0].strip()
	return race, gender