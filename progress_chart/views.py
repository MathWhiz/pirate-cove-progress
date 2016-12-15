from django.shortcuts import render
from django.template.loader import render_to_string
import requests

# Create your views here.
from django.http import HttpResponse
from django.core.cache import cache

ARTICLE_NAME = 'The_Keep:Pirate_Cove/Guilds_with_Inactive_Leaders'
SECTIONS = ['Not Started', 'Unknown', 'In Progress', 'To Be Read Last Rites', 'Finished']
SECTION_MATCH = {
    'Not Started': lambda title: title.lower().startswith('not started'),
    'In Progress': lambda title: title.lower().startswith('in progress'),
    'Finished': lambda title: title.lower().startswith('finished'),
    'To Be Read Last Rites': lambda title: title.lower().startswith('to be read last rites'),
}
SECTION_MATCH['Unknown'] = lambda title: not (SECTION_MATCH['Not Started'](title) or SECTION_MATCH['In Progress'](title) or SECTION_MATCH['Finished'](title) or SECTION_MATCH['To Be Read Last Rites'](title))

def groupGuilds():
    # Get details on 'The Keep:Pirate Cove/Guilds with Inactive Leaders' (article id)
    article_data = requests.get('http://habitica.wikia.com/api/v1/Articles/Details?titles={}'.format(ARTICLE_NAME)).json()['items']
    article_id = article_data[article_data.keys()[0]]['id']
    
    # Get content of 'The Keep:Pirate Cove/Guilds with Inactive Leaders'
    article_content = requests.get('http://habitica.wikia.com/api/v1/Articles/AsSimpleJson?id={}'.format(article_id)).json()['sections'][1:]
    
    return article_content, {section: [guild['title'] for guild in article_content if SECTION_MATCH[section](guild['title'])] for section in SECTIONS}
    

def index(request):
    
    article_content, content_sections = groupGuilds()
    
    section_numbers = [len(content_sections[section]) for section in SECTIONS]
    
    print(u', '.join(content_sections['Unknown']).encode('utf-8').strip())
    
    chart_data = {
        'chtt': 'Pirate Cove - Progress',
        'cht': 'pd',
        'chof': '.png',
        'chs': '500x300',
        'chf': 'bg,s,FFFFFF00',
        'chdl': '|'.join(SECTIONS),
        'chco': 'e55050,e57550,e5c050,e5e550,50e550',
        'chd': 't:{}'.format(','.join([str(x) for x in section_numbers])),
        'chl': '|'.join([str(x) if x > 0 else '' for x in section_numbers]),
        'chli': '{} Guilds'.format(len(article_content)),
    }
    image = requests.get('https://image-charts.com/chart',params=chart_data)
    return HttpResponse(image.content, content_type='image/png')

def list(request):
    article_content, content_sections = groupGuilds()
    context = {
        'content': article_content,
        'sorted_list': content_sections,
        'sections': SECTIONS
    }
    template = render_to_string('list.html', context)
    
    return HttpResponse(template)
