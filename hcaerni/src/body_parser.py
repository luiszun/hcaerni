import json
import re
import requests
import urllib

from src.mailmod import EmailHandler

# Got these value pairs from https://api.avalanche.org/v2/public/products/map-layer
# Note to self, I know the order makes no sense, but who cares?
mapIdToCenter = {
    "183": "AAIC",
    "189": "AAIC",
    "197": "AAIC",
    "193": "AAIC",
    "186": "AAIC",
    "191": "AAIC",
    "194": "AAIC",
    "261": "BAC",
    "3": "BTAC",
    "1": "BTAC",
    "2": "BTAC",
    "205": "COAA",
    "300": "COAA",
    "203": "CNFAIC",
    "282": "CNFAIC",
    "121": "CNFAIC",
    "122": "CNFAIC",
    "122": "CNFAIC",
    "187": "CTCAK",
    "192": "JUAK",
    "301": "CAAC",
    "55": "CAIC",
    "52": "CAIC",
    "57": "CAIC",
    "56": "CAIC",
    "58": "CAIC",
    "60": "CAIC",
    "54": "CAIC",
    "59": "CAIC",
    "51": "CAIC",
    "53": "CAIC",
    "128": "ESAC",
    "207": "FAC",
    "208": "FAC",
    "209": "FAC",
    "109": "GNFAC",
    "281": "GNFAC",
    "117": "GNFAC",
    "116": "GNFAC",
    "115": "GNFAC",
    "110": "GNFAC",
    "112": "GNFAC",
    "111": "GNFAC",
    "190": "HPAC",
    "138": "IPAC",
    "149": "IPAC",
    "272": "IPAC",
    "202": "KPAC",
    "124": "WCMAC",
    "123": "MSAC",
    "297": "MWAC",
    "146": "NWAC",
    "145": "NWAC",
    "147": "NWAC",
    "148": "NWAC",
    "139": "NWAC",
    "141": "NWAC",
    "140": "NWAC",
    "143": "NWAC",
    "142": "NWAC",
    "144": "NWAC",
    "153": "PAC",
    "293": "SNFAC",
    "295": "SNFAC",
    "294": "SNFAC",
    "296": "SNFAC",
    "77": "SAC",
    "260": "TAC",
    "251": "UAC",
    "252": "UAC",
    "253": "UAC",
    "254": "UAC",
    "255": "UAC",
    "256": "UAC",
    "257": "UAC",
    "259": "UAC",
    "258": "UAC",
    "273": "WAC",
    "274": "WAC",
    "275": "WAC",
    "276": "WAC",
}


def ComposePOST(url, message):
    guid = re.findall(
        "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", url
    )[0]
    response = requests.get(url).text

    mIdLine = re.findall('id="MessageId".*value=.*"', response)[0]
    messageId = re.findall("[0-9]+", mIdLine)[0]
    message = urllib.parse.quote_plus(message)
    postMsg = (
        "ReplyAddress=nwac%40anxiousmountaineer.com&ReplyMessage="
        + message
        + "&MessageId="
        + messageId
        + "&Guid="
        + guid
    )
    # data = json.dumps({"ReplyAddress":"nwac@anxiousmountaineer.com", "ReplyMessage": message, "MessageId" : messageId, "Guid" : guid})
    return postMsg


def FindMapShare(body):
    share = re.findall("http[s]?://.*anxiousmountaineer\.com", body)
    if len(share) > 0:
        return share[0]
    return ""


def GetForecastMessage(id):
    # What we want is to get this: GET https://api.avalanche.org/v2/public/product?type=forecast&center_id=[Center]&zone_id=[id]
    response = json.loads(
        requests.get(
            "https://api.avalanche.org/v2/public/product?type=forecast&center_id="
            + mapIdToCenter[id]
            + "&zone_id="
            + id
        ).text
    )

    avyprobs = response["forecast_avalanche_problems"]

    tableValues = {
        "north": 0,
        "northeast": 1,
        "east": 2,
        "southeast": 3,
        "south": 4,
        "southwest": 5,
        "west": 6,
        "northwest": 7,
        "upper": 16,
        "middle": 8,
        "lower": 0,
    }

    problemsText = ""
    for problem in avyprobs:
        problemsText += problem["name"] + ":"
        for i in problem["size"]:
            problemsText += "D" + str(i)
        problemsText += "-" + problem["likelihood"]
        problemsText += "\n"
        dangerMap = 0
        for section in problem["location"]:
            nBit = 0
            # We get the corresponding location of the bit (MSB being bit 0)
            for val in section.split(" "):
                nBit += tableValues[val]
            dangerMap += 2 ** nBit

        problemsText += "{:06x}".format(dangerMap) + "\n"

    sendMessage = response["forecast_zone"][0]["name"]

    dangerData = ""
    for danger in response["danger"]:
        dangerData += danger["valid_day"] + ":"
        dangerData += "up" + str(danger["upper"]) + "/5\n"
        dangerData += "mid" + str(danger["middle"]) + "/5\n"
        dangerData += "low" + str(danger["lower"]) + "/5\n"

    text = (
        response["forecast_zone"][0]["name"] + " Danger\n" + dangerData + problemsText
    )

    return text


def ParseAndTriage(body: str, From: str, email_parser: EmailHandler) -> None:
    firstLine = body.partition("\n")[0]
    lineSplitR = firstLine.split(" ")
    lineSplit = []

    for i in lineSplitR:
        lineSplit.append(i.rstrip())

    # Check to see if this is a test - example
    # "test email@anxiousmountaineer.com 141"
    # This would try to read the mapshare link from the body and send an email with it to luis@luiszun.com
    # Serves to verify that the body structure of the email hasn't changed or that it can still be parsed.
    if lineSplit[0] == "test" and len(lineSplit) > 1:
        share = FindMapShare(body)
        if share != "":
            message = (
                "Successfully parsed the MapShare link\n The followed link has been replaced by SendGrid  to be: "
                + share
            )
            if len(lineSplit) > 2 and lineSplit[2].isnumeric():
                message += "\n\n\n" + GetForecastMessage(lineSplit[2])
            email_parser.SendMail(message, lineSplit[1])

    # If this is malformed, there's nothing to be done
    elif lineSplit[0].isnumeric() is True and lineSplit[0] in mapIdToCenter:
        msg = GetForecastMessage(lineSplit[0])
        email_parser.SendMail(msg, From)
        url = FindMapShare(body)
        if url == "":
            return
        post = ComposePOST(url, msg)
        print("==========\n" + post + "\n==========")
        response = requests.post(
            "https://us0.explore.garmin.com/TextMessage/TxtMsg",
            data=post,
            headers={
                "Accept": "*/*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://us0.explore.garmin.com",
                "Referer": url,
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        print(response.text)
