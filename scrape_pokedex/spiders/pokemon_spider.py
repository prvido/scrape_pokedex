import scrapy
from scrapy.crawler import CrawlerProcess

# Max ID desconsiderando as gerações depois de Alola 719
global max_id
max_id = 719

# Para acessar o sheel basta usar o comando:
# scrapy shell 'https://pokemondb.net/pokedex/1'

def convert_to_int(x):
    try:
        return int(x)
    except:
        return None

def convert_to_float(x):

    dicionario = {
        '(': '',
        ' ': '',
        '%': '',
        'w': ''
    }

    try:
        return float(x.translate(str.maketrans(dicionario))) / 100
    except:
        return None

def get_id(response):
    pokemon = response.xpath('//*[@id="main"]/nav[1]/a/text()').getall()[-1]
    id = int(pokemon[0:4].replace('#', '').replace(' ', '')) - 1
    return str(id)

def get_defenses(response, id):

    x = {}

    if len(response.xpath('//*[@id="tab-basic-' + id + '"]/div[2]/div[2]/div/table[1]/tr/td/@class').getall()) > 0:
        tab = response.css('div.sv-tabs-panel.active::attr(id)').get()
        type_arr1 = response.xpath('//*[@id="' + tab + '"]/div[2]/div[2]/div/table[1]/tr/th/a/text()').getall()
        data_arr1 = response.xpath('//*[@id="' + tab + '"]/div[2]/div[2]/div/table[1]/tr/td/@class').getall()
        type_arr2 = response.xpath('//*[@id="' + tab + '"]/div[2]/div[2]/div/table[2]/tr/th/a/text()').getall()
        data_arr2 = response.xpath('//*[@id="' + tab + '"]/div[2]/div[2]/div/table[2]/tr/td/@class').getall()
    
    else:

        tab = response.css('div.sv-tabs-panel.active::attr(id)').getall()[1]
        type_arr1 = response.xpath('//*[@id="' + tab + '"]/div/table[1]/tr/th/a/text()').getall()
        data_arr1 = response.xpath('//*[@id="' + tab + '"]/div/table[1]/tr/td/@class').getall()
        type_arr2 = response.xpath('//*[@id="' + tab + '"]/div/table[2]/tr/th/a/text()').getall()
        data_arr2 = response.xpath('//*[@id="' + tab + '"]/div/table[2]/tr/td/@class').getall()

    for i in range(len(type_arr1)):
            x[type_arr1[i].upper()] = int(data_arr1[i][21:25])/100
            #x[type_arr1[i].upper()] = int(data_arr1[i][21:25])/100
    
    for i in range(len(type_arr2)):
            x[type_arr2[i].upper()] = int(data_arr2[i][21:25])/100




    return x

def get_generations(response):
    titles = response.css('a::attr(title)').getall()

    generations = []

    for t in titles:
        if 'Generation' in t:
            generations.append({'gen': t[11], 'gen_desc': t})

    return generations

def get_evolutions(response, id):

    extractions = response.css('span small::text').getall()

    evolutions = []

    if len(extractions) > 0:
        for e in extractions:

            evolution_id = convert_to_int(e[1:])

            if e[0] == '#' and evolution_id > id and evolution_id <= max_id:
                evolutions.append(evolution_id)
    
    return evolutions



class PokemonSpider(scrapy.Spider):
    name = 'pokemon'
    start_urls = ['https://pokemondb.net/pokedex/1']

    def parse(self, response):

        id = get_id(response)

        try:
            next_page = response.xpath('//*[@id="main"]/nav[1]/a/@href').getall()[-1]
        except:
            next_page = None
        
        if next_page is not None and int(id) <= max_id:

           
            tab = 'tab-basic-' + id

            yield {
                'id': convert_to_int(response.xpath('//*[@id="' + tab + '"]/div[1]/div[2]/table/tbody/tr[1]/td/strong/text()').get()),
                'name': response.xpath('//*[@id="main"]/h1/text()').get(),
                'type': response.xpath('//*[@id="' + tab + '"]/div[1]/div[2]/table/tbody/tr[2]/td/a/text()').getall(),
                'stats': {
                    'base_hp': convert_to_int(response.xpath('//*[@id="' + tab + '"]/div[2]/div[1]/div[2]/table/tbody/tr[1]/td[1]/text()').get()),
                    'base_attack': convert_to_int(response.xpath('//*[@id="' + tab + '"]/div[2]/div[1]/div[2]/table/tbody/tr[2]/td[1]/text()').get()),
                    'base_defense': convert_to_int(response.xpath('//*[@id="' + tab + '"]/div[2]/div[1]/div[2]/table/tbody/tr[3]/td[1]/text()').get()),
                    'base_sp_attack': convert_to_int(response.xpath('//*[@id="' + tab + '"]/div[2]/div[1]/div[2]/table/tbody/tr[4]/td[1]/text()').get()),
                    'base_sp_defense': convert_to_int(response.xpath('//*[@id="' + tab + '"]/div[2]/div[1]/div[2]/table/tbody/tr[5]/td[1]/text()').get()),
                    'base_speed': convert_to_int(response.xpath('//*[@id="' + tab + '"]/div[2]/div[1]/div[2]/table/tbody/tr[6]/td[1]/text()').get())
                },
                'catch_rate': convert_to_float(response.xpath('//*[@id="' + tab + '"]/div[1]/div[3]/div/div[1]/table/tbody/tr[2]/td/small/text()').get()[0:7]),
                'defenses': get_defenses(response, id),
                'img_link': response.css('img::attr(src)').get(),
                'generations': get_generations(response),
                'evolutions': get_evolutions(response, convert_to_int(id))
            }

            next_page = 'https://pokemondb.net' +  next_page

            yield response.follow(next_page, callback=self.parse)

process = CrawlerProcess(
                    settings = {
                        'FEEDS': {
                            'pokemon.json': {'format': 'json'}
                        }
                    }
                )

process.crawl(PokemonSpider)
process.start()