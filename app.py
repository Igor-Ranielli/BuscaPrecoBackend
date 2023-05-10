import psycopg2
from datetime import datetime, timezone
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as condicao_esperada
import schedule
from time import sleep

conexao = psycopg2.connect(
    database='railway',
    user='postgres',
    password='B3S4EWWSSC6mzssoR3Hj',
    host='containers-us-west-41.railway.app',
    port='7344'
)

sql = conexao.cursor()

def novo_produto(sql,conexao,nome, preco, site, data_cotacao, link_imagem):
    # verificar se um produto igual já está cadastrado
    query = 'SELECT * FROM app_buscapreco_produto WHERE nome=%s and preco=%s and site=%s'
    valores = (nome, preco, site)
    resultado = sql.execute(query, valores)
    dados = sql.fetchall()

    if len(dados) == 0:
        # se não houver dados iguais, gravar um novo produto
        query = 'INSERT INTO app_buscapreco_produto(nome, preco, site, data_cotacao, link_imagem) VALUES(%s,%s,%s,%s,%s)'
        valores = (nome, preco, site, data_cotacao, link_imagem)
        sql.execute(query, valores)
    else:
        # se já houver dados iguais, não gravar um novo produto
        print('Dados já cadastrados anteriormente!')

# novo_produto(sql, conexao, 'Iphone 15', 13000.50, 'apple.com/iphone15', datetime.now(), 'www.imagem.com/imagem1.jpg')
    conexao.commit()

def iniciar_driver():
    chrome_options = Options()

    arguments = ['--lang=en-US', '--window-size=1920,1080',
                 '--incognito', '--headless']
    
    for argument in arguments:
        chrome_options.add_argument(argument)

    chrome_options.add_experimental_option('prefs', {
        'download.prompt_for_download': False,
        'profile.default_content_setting_values.notifications': 2,
        'profile.default_content_setting_values.automatic_downloads': 1

    })

    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(
        driver,
        10,
        poll_frequency=1,
        ignored_exceptions=[
        NoSuchElementException,
        ElementNotVisibleException,
        ElementNotSelectableException,
        ]
    )
    return driver, wait

def varrer_site_1():
    # 1 - Entrar no site - https://site1produto.netlify.app/
    driver, wait = iniciar_driver()
    driver.get('https://site1produto.netlify.app/')
    # 2 - Anotar o nome do produto
    nomes = wait.until(condicao_esperada.visibility_of_all_elements_located((By.XPATH,"//div[@class='detail-box']/a")))
    # 3 - Anotar o preço
    precos = wait.until(condicao_esperada.visibility_of_all_elements_located((By.XPATH, "//h6[@class='price_heading']")))
    # 4 - Anotar o link de onde foi extraido a info
    site = driver.current_url
    # 5 - Anotar o link da imagem
    links_imagem = wait.until(condicao_esperada.visibility_of_all_elements_located((By.XPATH, "//div[@class='img-box']/img")))
    nome_iphone = nomes[0].text
    nome_gopro = nomes[1].text

    preco_iphone = precos[0].text.split(' ')[1]
    preco_gopro = precos[1].text.split(' ')[1]

    link_imagem_iphone = links_imagem[0].get_attribute('src')
    link_imagem_gopro = links_imagem[1].get_attribute('src')

    novo_produto(sql, conexao, nome_iphone, preco_iphone, site, datetime.now(), link_imagem_iphone)
    novo_produto(sql, conexao, nome_gopro, preco_gopro, site, datetime.now(), link_imagem_gopro)

    print('site 1 varrido')

def varrer_site_2():
    driver, wait = iniciar_driver()
    driver.get('https://site2produto.netlify.app/')
    precos = wait.until(condicao_esperada.visibility_of_all_elements_located((By.XPATH,"//div[@class='why-text']//h5")))
    nomes = wait.until(condicao_esperada.visibility_of_all_elements_located((By.XPATH,"//div[@class='why-text']")))
    imagens = wait.until(condicao_esperada.visibility_of_any_elements_located((By.XPATH,"//img[@class='img-fluid']")))

    link_imagem_iphone = imagens[0].get_attribute('src')
    link_imagem_gopro = imagens[1].get_attribute('src')

    nome_iphone = nomes[0].text.split('\n')[0]
    nome_gopro = nomes[1].text.split('\n')[0]

    preco_iphone = nomes[0].text.split('$')[1]
    preco_gopro = precos[1].text.split('$')[1]

    novo_produto(sql,conexao,nome_iphone,float(preco_iphone),driver.current_url,datetime.now(),link_imagem_iphone)
    novo_produto(sql,conexao,nome_gopro,float(preco_gopro),driver.current_url,datetime.now(),link_imagem_gopro)

    print('site 2 varrido')

def varrer_site_3():
    driver, wait = iniciar_driver()
    driver.get('https://site3produto.netlify.app/')
    precos = wait.until(condicao_esperada.visibility_of_all_elements_located((By.XPATH, '//div[@class="product__item__text"]//h5')))
    nomes = wait.until(condicao_esperada.visibility_of_all_elements_located((By.XPATH,'//div[@class="product__item__text"]//h6/a')))
    imagens = wait.until(condicao_esperada.visibility_of_all_elements_located((By.XPATH,'//div[@class="product__item__pic set-bg"]')))

    link_imagem_iphone = driver.current_url+imagens[0].get_attribute('style').split(' ')[1][5:-3]
    link_imagem_gopro = driver.current_url+imagens[1].get_attribute('style').split(' ')[1][5:-3]

    nome_iphone = nomes[0].text
    nome_gopro = nomes[1].text

    preco_iphone = precos[0].text.split('$')[1]
    preco_gopro = precos[1].text.split('$')[1]

    novo_produto(sql,conexao,nome_iphone,float(preco_iphone),driver.current_url,datetime.now(),link_imagem_iphone)
    novo_produto(sql,conexao,nome_gopro,float(preco_gopro),driver.current_url,datetime.now(),link_imagem_gopro)

    print('site 3 varrido')



def rodar_tarefas():
    varrer_site_1()
    varrer_site_2()
    varrer_site_3()

schedule.every().day.at('06:00').do(rodar_tarefas)
# se quiser rodar a cada 30 segundos coloque: schedule.every(30).seconds.do(rodar_tarefas)

while True:
    schedule.run_pending()
    sleep(1)