"""Scraper Selenium headless para buscar clínicas no site da Unimed.

Uso:
    python -m app.scraper 13050-000 "Unimed Pleno" "Clínica Médica"
"""
import sys, json, time, os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

CEP, PLANO, AREA = sys.argv[1:4]

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# Render instala chromium-browser em /usr/bin/chromium-browser
if os.path.exists("/usr/bin/chromium-browser"):
    chrome_options.binary_location = "/usr/bin/chromium-browser"

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
results = []
try:
    driver.set_page_load_timeout(30)
    driver.get("https://www.unimed.coop.br/pct/index.jsp?cd_canal=60")  # URL genérica; ajuste se necessário

    # Preenche CEP
    cep_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Endereço']")
    cep_input.send_keys(CEP)
    time.sleep(0.5)

    # Seleciona plano
    driver.find_element(By.CSS_SELECTOR, "div[label*='Rede']").click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, f"//span[contains(text(), '{PLANO}')]" ).click()

    # Seleciona área
    driver.find_element(By.CSS_SELECTOR, "div[label*='Área']").click()
    time.sleep(0.5)
    driver.find_element(By.XPATH, f"//span[contains(text(), '{AREA}')]" ).click()

    # Clica em buscar
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']" ).click()
    time.sleep(5)  # espera carregar

    cards = driver.find_elements(By.CSS_SELECTOR, ".resultado-guia")[:5]
    for c in cards:
        try:
            nome = c.find_element(By.TAG_NAME, "h3").text
        except NoSuchElementException:
            nome = "—"
        try:
            endereco = c.find_element(By.CSS_SELECTOR, ".endereco").text
        except NoSuchElementException:
            endereco = "—"
        results.append({"nome": nome, "endereco": endereco})
finally:
    driver.quit()

print(json.dumps(results, ensure_ascii=False))
