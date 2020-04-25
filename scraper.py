from bs4 import BeautifulSoup
import csv
import os
import requests
import sys


INPUT_FILENAME = 'input.txt'
OUTPUT_FILENAME = 'output.csv'
TEMP_DIRECTORY_NAME = 'temp'


def get_soup(url):
	html_filename = f'{sanitize_filename(url)}.html'
	html_filepath = os.path.join(TEMP_DIRECTORY_NAME, html_filename)
	has_cached_content = os.path.exists(html_filepath)
	if not has_cached_content:
		response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=25)
		content = response.content
		f = open(html_filepath, 'wb')
		f.write(content)
	with open(html_filepath, 'r', encoding='utf-8') as f:
		content = f.read()
	soup = BeautifulSoup(content, 'html.parser')
	return soup


def sanitize_filename(the_string):
	return the_string.replace('/', '_').replace(':', '').replace('?', '')


def get_vote_results(soup):
	vote_results = {}
	first_table = soup.find('table')
	header_row = first_table.find_all('th')
	count_row = first_table.find_all('td')
	for vote_type, vote_count in zip(header_row, count_row):
		vote_results[vote_type.text.strip()] = vote_count.text.strip()
	return vote_results 

def get_attributes(soup):
	attributes = {}
	divs = soup.find('section', id='info-ficha').find('div', class_='auxi').find_all('div', class_= 'datos-ficha')
	for div in divs:
		attribute_name, attribute_value = get_attribute(div)
		attributes[attribute_name] = attribute_value
	return attributes


def get_congress_members(soup):
	congress_members = {
		'A Favor': [],
		'En Contra': [],
		'Abstención': [],
		'Pareos': [],
	}
	type_table_id_map = {
		'A Favor': 'ContentPlaceHolder1_ContentPlaceHolder1_PaginaContent_dtlAFavor',
		'En Contra': 'ContentPlaceHolder1_ContentPlaceHolder1_PaginaContent_dtlEnContra',
		'Abstención': 'ContentPlaceHolder1_ContentPlaceHolder1_PaginaContent_dtlAbstencion',
		'Pareos': 'ContentPlaceHolder1_ContentPlaceHolder1_PaginaContent_dtlPareos',
	}
	for table_type, table_id in type_table_id_map.items():
		table = soup.find('table', id=table_id)
		if not table:
			continue
		for table_row in table.find_all('tr', recursive=False):
			for table_cell in table_row.find_all('td', recursive=False):
				li = table_cell.find('li')
				if not li:
					break
				anchor_tags = li.find_all('a', recursive=False)
				member_name = anchor_tags[0].text.strip()
				pareo = anchor_tags[1].text.strip() if len(anchor_tags) > 1 else ''
				congress_members[table_type].append(
					{
						'name': member_name,
						'pareo': pareo,
					}
				)
	return congress_members


def get_attribute(div):
	name = div.find('div', class_= 'dato').text.strip()
	name = name[:-1] if name.endswith(':') else name
	value = div.find('div', class_= 'info').text.strip()
	return name, value	

def is_error_page(soup):
	error_msg = "Error de servidor en la aplicación '/'."
	first_span_h1 = soup.find('body').find('span').h1
	if first_span_h1:
		if first_span_h1.text == error_msg:
			return True
	return False

def get_data_from_url(url):
	soup = get_soup(url)
	if is_error_page(soup):
		return None
	vote_results = get_vote_results(soup)
	attributes = get_attributes(soup)
	congress_members = get_congress_members(soup)
	return {
		'vote_results': vote_results,
		'attributes': attributes,
		'congress_members': congress_members,
	}


def create_csv(filename):
	with open(filename, 'w', newline='') as file:
		heading_row = ['Congress Member Name', 'id', 'Date', 'Materia', 'Artículo', 'Vote', 'Trámite', 'Quorum', 'Proyecto Ley', 'Pareo', 'Tipo de Votación', 'Resultado', 'A favor', 'En contra', 'Abstención']
		writer = csv.DictWriter(file, fieldnames=heading_row)
		writer.writeheader()


def get_ids(filename):
	ids = []
	with open(filename) as file:
		for line in file:
			id = line.strip()
			if id and id not in ids:
				ids.append(id)
	return ids


def prepare_rows(data):
	rows = []
	
	id = data.get('id', '')
	date = data.get('attributes').get('Fecha', '')
	materia = data.get('attributes').get('Materia', '')
	articulo = data.get('attributes').get('Artículo', '')
	tramite = data.get('attributes').get('Trámite', '')
	quorum = data.get('attributes').get('Quorum', '')
	proyecto_ley = data.get('attributes').get('Proyecto Ley', '')
	tipo_de_votacion = data.get('attributes').get('Tipo de Votación', '')
	resultado = data.get('attributes').get('Resultado', '')
	a_favor = data.get('vote_results').get('A Favor', '')
	en_contra = data.get('vote_results').get('En Contra', '')
	abstencion = data.get('vote_results').get('Abstención', '')

	for heading, members in data.get('congress_members').items():
		for member in members:
			name = member.get('name')
			pareo = member.get('pareo')
			vote = '' if pareo else heading
			row = [name, id, date, materia, articulo, vote, tramite, quorum, proyecto_ley,
				pareo, tipo_de_votacion, resultado, a_favor, en_contra, abstencion]
			rows.append(row)
	
	return rows


def append_to_csv(filename, rows):
	with open(filename, 'a', newline='') as file:
		writer = csv.writer(file)
		writer.writerows(rows)


def create_directory(name):
    if not os.path.exists(name):
        os.makedirs(name)

def get_arguments(argv):
	if len(argv) < 3:
		print('Please provide input and output filenames')
		sys.exit(1)
	return argv[1], argv[2]

def main():
	input_filename, output_filename = get_arguments(sys.argv)
	create_directory(TEMP_DIRECTORY_NAME)
	create_csv(output_filename)
	ids = get_ids(input_filename)
	for index, id in enumerate(ids):
		print(f'Processing ID: {id} | {index + 1}/{len(ids)}')
		url = f'https://www.camara.cl/legislacion/sala_sesiones/votacion_detalle.aspx?prmIdVotacion={id}'
		data = get_data_from_url(url)
		if not data:
			print('ID does not exist')
			continue
			
		data['id'] = id
		rows = prepare_rows(data)
		append_to_csv(output_filename, rows)
	print('Output created successfully')


if __name__ == '__main__':
	main()
