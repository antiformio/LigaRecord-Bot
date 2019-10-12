import json
import os
import pickle
import smtplib
import time
import re

import numpy as np
import pandas as pd
import requests
from envelopes import Envelope, GMailSMTP
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import serialize


def readCredentials():
    with open("//Users//filipemartins//Desktop//VScodeProjects//LigaRecord-Bot//credentials.json") as f:
        data = json.load(f)
    return data["email"], data["password"], data["gecko_path"]


def readBotCredentials():
    with open("//Users//filipemartins//Desktop//VScodeProjects//LigaRecord-Bot//telegramCreds.json") as f:
        data = json.load(f)
    return data["bot_token"], data["bot_chatID"]


def getData():
    """
        Web-Scrapping site da liga record.
    """
    options = Options()
    options.headless = True

    email, pass_word, gecko_path = readCredentials()

    browser = webdriver.Firefox(options=options, executable_path=gecko_path)
    browser.get(
        "https://aminhaconta.xl.pt/LoginNonio?returnUrl=https%3a%2f%2fliga.record.pt%2fdefault.aspx"
    )

    user = browser.find_element_by_css_selector("#email")
    user.send_keys(email)
    time.sleep(5)

    password = browser.find_element_by_xpath(
        "/html/body/section/div/div/div/div[2]/form/div[2]"
    )
    password.click()
    realpass = browser.find_element_by_css_selector("#password")
    realpass.send_keys(pass_word)

    browser.find_element_by_css_selector("#loginBtn").click()
    time.sleep(10)

    ronda = browser.find_element_by_id("id-round-main").text

    browser.get("https://liga.record.pt/common/services/teamsleague_page.ashx?guid=8116be3e-d932-4866-874f-a01212e8045c&page=1&pagesize=20&mode_ranking=round&type_ranking=")

    equipas = browser.find_elements_by_class_name("nome")
    pontos = browser.find_elements_by_class_name("pontos_equipa")

    return {equipas[i].text: re.findall(r'\d+', pontos[i].text)[0] for i in range(0, 16)}, ronda


def getTable():
    """
        Download da tabela classificativa
    """
    readSave = serialize.serialization()
    readSave.AWSdownload("Tabela", "TableDownloaded")
    tabelaDownloaded = pickle.load(open("TableDownloaded", "rb"))
    os.remove("TableDownloaded")
    return tabelaDownloaded


def getCalendar(jornada):
    """
        Download do ficheiro do calendário, de uma determinada jornada
    """
    readSave = serialize.serialization()
    readSave.AWSdownload(f"Calendario{jornada}", f"Calendario{jornada}")
    calendario = pickle.load(open(f"Calendario{jornada}", "rb"))
    os.remove(f"Calendario{jornada}")
    return calendario


def telegram_bot_sendtext(bot_message):
    """
        Recebe mensagem por parametro e envia para o bot.
    """
    bot_token, bot_chatID = readBotCredentials()
    send_text = (
        "https://api.telegram.org/bot"
        + bot_token
        + "/sendMessage?chat_id="
        + bot_chatID
        + "&parse_mode=Markdown&text="
        + bot_message
    )
    requests.get(send_text)


def __getResultByJogo(casa, fora, dict):
    """
        Função privada para calcular a mensagem dos resultados para enviar por telegram.
    """
    resultCasa = dict[casa]
    resultFora = dict[fora]
    return (
        "\n"
        + str(casa)
        + ": "
        + resultCasa
        + " "
        + str(fora)
        + ": "
        + resultFora
        + "\n"
    )


def buildResult(tuplos, dictPontuacoes):
    """
        Produz tanto a string com os resultados (para enviar por telegram) como a lista com um dicionário por jogo.
        A listaResultados tem o formato : [{'equipa1': 20, 'equipa2': 30}, {'equipa3': 12, 'equipa4': 38}]
    """
    resultadoString = ""
    listaResultados = []
    for jogo in tuplos:
        casa, fora = jogo[0], jogo[1]
        resultadoString += __getResultByJogo(casa, fora, dictPontuacoes)
        newDic = {
            jogo[0]: int(dictPontuacoes[jogo[0]]),
            jogo[1]: int(dictPontuacoes[jogo[1]]),
        }
        listaResultados.append(newDic)
    return resultadoString, listaResultados


def updateTabela(listaResult, tabela):
    """
        Actualiza tabela. Em função do resultado de cada jogo da jornada.
    """
    for dic in listaResult:
        maiorPontuacao = 0
        equipaVencedora = ""
        pontuacoes = list(dic.values())
        if pontuacoes[0] == pontuacoes[1]:
            equipaVencedora = "empate"
            for equipa, pontos in dic.items():
                row = tabela.loc[tabela["Equipa"] == equipa].index.values.astype(int)[0]
                tabela.at[row, "Pontos"] += 1
                tabela.at[row, "Jogos"] += 1
                tabela.at[row, "E"] += 1
                tabela.at[row, "GM"] += pontos
                tabela.at[row, "GS"] += pontos
        else:
            for equipa, pontos in dic.items():
                if pontos > maiorPontuacao:
                    maiorPontuacao = pontos
                    equipaVencedora = equipa
            for equipa, pontos in dic.items():
                if equipa != equipaVencedora:
                    equipaPerdedora = equipa
                    pontuacaoPerdedora = pontos
            # Equipa Vencedora
            row = tabela.loc[tabela["Equipa"] == equipaVencedora].index.values.astype(
                int
            )[0]
            tabela.at[row, "Pontos"] += 3
            tabela.at[row, "Jogos"] += 1
            tabela.at[row, "V"] += 1
            tabela.at[row, "GM"] += maiorPontuacao
            tabela.at[row, "GS"] += pontuacaoPerdedora
            tabela.at[row, "GA"] = tabela.at[row, "GM"] - tabela.at[row, "GS"]
            # Equipa Perdedora
            row = tabela.loc[tabela["Equipa"] == equipaPerdedora].index.values.astype(
                int
            )[0]
            tabela.at[row, "Jogos"] += 1
            tabela.at[row, "D"] += 1
            tabela.at[row, "GM"] += pontuacaoPerdedora
            tabela.at[row, "GS"] += maiorPontuacao
            tabela.at[row, "GA"] = tabela.at[row, "GM"] - tabela.at[row, "GS"]
    return tabela


def saveResultsDict(dictPontuacoes, jornada):
    """
        Upload para a s3 dos dicionários com os resultados por jornada
    """
    readSave = serialize.serialization()
    pickle.dump(dictPontuacoes, open(jornada, "wb"))
    readSave.AWSupload(jornada, jornada)
    os.remove(jornada)


def saveUpdatedTable(tabelaUpdated):
    """
        Upload para a s3 da tabela actualizada (depois de feitas todas as alterações, de classificacao e melhores equipas)
    """
    readSave = serialize.serialization()
    pickle.dump(tabelaUpdated, open("Tabela", "wb"))
    readSave.AWSupload("Tabela", "Tabela")


def biggestScorer(dictPontuacoes, tabela):
    """
        Procura o(s) melhores resultados da jornada e dá mais um ponto a essa(s) equipa(s)
    """
    for key in dictPontuacoes:
        dictPontuacoes[key] = int(dictPontuacoes[key])
    max_value = max(dictPontuacoes.values())
    max_keys = [k for k, v in dictPontuacoes.items() if v == max_value]

    for equipa in max_keys:
        row = tabela.loc[tabela["Equipa"] == equipa].index.values.astype(int)[0]
        tabela.at[row, "Pontos"] += 1
    return tabela, max_keys


def reduceTableDetails(tabela):
    """
        Reduz os detalhes da tabela final. Limita-se a imprimir tabela com ranking equipa e pontos.
    """
    tabelaCompact = tabela[["Equipa", "Pontos"]]
    tabelaSorted = tabelaCompact.sort_values(["Pontos"], ascending=False)
    tabelaSorted = tabelaSorted.reset_index(drop=True)
    tabelaSorted.index = np.arange(1, len(tabelaSorted) + 1)
    return tabelaSorted


def tableToHtmlAndEmail(table, bestTeams, jornada):
    """
        Ordena a tabela por Pontos descendente. Cria novo index.
        Converte a tabela para HTML, e envia email.
    """
    listaEmails = ["fjnmgm@gmail.com"]  # ,'Teixeira.capela@gmail.com'
    tableHtml = table.sort_values(["Pontos"], ascending=False).reset_index(drop=True)
    tableHtml.index = np.arange(1, len(tableHtml) + 1)
    htmlTable = tableHtml.to_html()
    textoEmail = (
        "<b>Resultados da Jornada: </b><br>"
        + jornada.replace("\n", "<br>")
        + "<br><br><b>Equipa(s) com melhor pontuaçao (mais um ponto): </b> <br> "
        + ", ".join(bestTeams)
        + "<br><br><b>Tabela classificativa: </b>"
        + htmlTable
    )
    sendEMail(textoEmail, jornada, listaEmails)


def resetTable():
    """
        Function to reset the table to default values. Use carefully because it deletes the previous table.
    """
    readSave = serialize.serialization()
    dataForFrame = {
        "Equipa": [
            "Alphateam",
            "FC Kombichos",
            "Here for Beer",
            "FC Chupitos",
            "ClassOnGrass",
            "Virose",
            "FCBalasar",
            "SL Bernardes",
            "TascoFC",
            "Athletic Dafundo",
            "Chuecos FC",
            "FC Poukitxo",
            "Atlético Alijoense",
            "Black Mamba FC",
            "Fonte do Olmo FC",
            "Messishow",
        ],
        "Pontos": [0, 3, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 0, 0, 1, 0],
        "Jogos": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "V": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "E": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "D": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "GM": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "GS": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "GA": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
    tabela = pd.DataFrame(
        dataForFrame,
        columns=["Equipa", "Pontos", "Jogos", "V", "E", "D", "GM", "GS", "GA"],
    )
    pickle.dump(tabela, open("Tabela", "wb"))
    readSave.AWSupload("Tabela", "Tabela")


def createCalendar():
    """
        Function to create calendar. Eatch file (jornada) consists on a list of tuples. filenames is as following: CalendarioX (X being Ronda)
    """
    readSave = serialize.serialization()
    calendario = [
        ("Athletic Dafundo", "FCBalasar"),
        ("FC Chupitos", "FC Kombichos"),
        ("TascoFC", "Messishow"),
        ("Fonte do Olmo FC", "FC Poukitxo"),
        ("Here for Beer", "Black Mamba FC"),
        ("Atlético Alijoense", "SL Bernardes"),
        ("Alphateam", "Virose"),
        ("Chuecos FC", "ClassOnGrass"),
    ]
    pickle.dump(calendario, open("Calendario3", "wb"))
    readSave.AWSupload("Calendario3", "Calendario3")


def sendEMail(texto, jornada, listaEmails):
    """
        Sends the email to the selected mailing list
    """
    envelope = Envelope(
        from_addr=("aws.py.servidor@gmail.com", "Tasco BOT"),
        to_addr=[
            ("fjnmgm@gmail.com", "Filipe"),
            ("Teixeira.capela@gmail.com", "Capela"),
        ],
        subject=f"Misters do Tasco - Resultados da {jornada}",
        html_body=texto,
    )
    gmail = GMailSMTP("aws.py.servidor@gmail.com", "ketooketyr")
    gmail.send(envelope)


if __name__ == "__main__":
    """
        Vai buscar o dicionário das pontuacoes e a respectiva jornada à liga record
    """
    dictPontuacoes, ronda = getData()
    jornada = "Ronda " + str(int((ronda[-2:].strip())) - 1)
    tabelaOnServer = getTable()
    ######################################
    # TESTING ! RETIRAR DO FLUXO DEPOIS
    ######################################
    # dictPontuacoes = {
    #     "Athletic Dafundo": "34",
    #     "Chuecos FC": "21",
    #     "FCBalasar": "23",
    #     "FC Chupitos": "54",
    #     "FC Kombichos": "87",
    #     "TascoFC": "23",
    #     "Messishow": "23",
    #     "Fonte do Olmo FC": "78",
    #     "FC Poukitxo": "100",
    #     "Here for Beer": "66",
    #     "Black Mamba FC": "99",
    #     "Atlético Alijoense": "1",
    #     "SL Bernardes": "55",
    #     "Alphateam": "33",
    #     "Virose": "100",
    #     "ClassOnGrass": "12",
    # }
    # jornada = "RONDA 1"
    ######################################
    ######################################

    """
        Salvar o dicionário dos resultados na S3 (formato RONDA X)
    """
    # saveResultsDict(dictPontuacoes, jornada)

    """
        Vai buscar o calendário da jornada respectiva. Calcula a string dos resultados, e a lista com os dados para actualizar a tabela.
        Envia o telegram com a string dos resultados
    """
    # calendario = getCalendar(int(ronda))
    # resultadosString, listaResultados = buildResult(calendario, dictPontuacoes)
    # telegram_bot_sendtext(resultadosString)

    """
        Actualiza a tabela com os resultados da jornada.
        Actualiza novamente com o ponto adicional da(s) melhor(es) equipa(s) da jornada.
        Salva a nova tabela na S3.
    """
    # tabelaUpdated = updateTabela(listaResultados, tabelaOnServer)
    # tabelaUpdatedWithBiggestScorer, bestTeams = biggestScorer(
    #     dictPontuacoes, tabelaUpdated
    # )

    # saveUpdatedTable(tabelaUpdatedWithBiggestScorer)

    """
        Edita a tabela para compactar os dados e envia a nova tabela por telegram e email.
    """
    # tabelaFinal = reduceTableDetails(tabelaUpdatedWithBiggestScorer)
    # telegram_bot_sendtext(tabelaFinal.to_string(header=False))
    # telegram_bot_sendtext("Equipa(s) com melhor pontuaçao: \n" + ", ".join(bestTeams))
    # tableToHtmlAndEmail(tabelaUpdatedWithBiggestScorer, bestTeams, jornada)

    """
        Manter sempre comentado. Serve para fazer reset à tabela, e criar os calendários (não estão completos...)
    """
    # resetTable()
    createCalendar()
