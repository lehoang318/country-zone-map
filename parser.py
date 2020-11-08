import json
import re
from country_map import *

def extractOffset(offsetToken):
    absOffset = re.findall('[0-9]{2}:[0-9]{2}', offsetToken)[-1]
    if('00:00' != absOffset):
        sign = re.findall('(\+|-)', offsetToken)[-1]
    else:
        sign = ''

    return '{0:s}{1:s}'.format(sign, absOffset)

def extractCountryCode(cCodeToken):
    cCode = -1
    cCodeToken = cCodeToken.strip()
    try:
        cCode = int(cCodeToken, 16)
    except Exception as e:
        print('Invalid Country Code hex string: {0:s}\n{1:s}'.format(cCodeToken, str(e)))
        cCode = -1

    return cCode

# Exceptions:
# 'CK COCOS ISLANDS CK 0x434B UTC - 03:00 +06:30',
# 'VENEZUELA WASAD VE 0x5645 UTC - 03:00 04:30',
# 'NORFOLK ISLANDS WSPCE NF 0x4E46 UTC + 12:00 11:30',
def findZoneId(regionName, offset):
    # Default
    zoneId = None
    defaultZoneId = None
    regionName = regionName.lower()
    rTokens = re.split(' |\(|\)|\.|&', regionName.lower())
    rTokens = list(filter(None, rTokens))
    #print('Tokens: {0:s}'.format(str(rTokens)))

    with open('zoneinfo.json') as fr:
        zoneDatabase = json.load(fr)
        zoneIdArr = zoneDatabase[offset]
        defaultZoneId = zoneIdArr[0]
        for zi in zoneIdArr:
            for token in rTokens:
                if ((token is not None) and (token in zi.lower())):
                    zoneId = zi
                    break
            if (zoneId is not None):
                break
            if ('Etc/GMT' in zi):
                defaultZoneId = zi

    if (zoneId is None):
        zoneId = defaultZoneId

    print('Best matched: {0:s} -> {1:s}'.format(regionName, str(zoneId)))

    return zoneId

database = {}

for line in COUNTRY_MAP:
    info = {}
    offsetIndex = line.rfind('UTC')
    offsetToken = line[offsetIndex:]
    offset = extractOffset(offsetToken)
    line = line[:offsetIndex].strip()

    cLetterPattern = '[A-Z]{2}'
    cHexPattern = '0x[0-9 A-F]{4}'
    cCodePattern = '\s{0:s}\s{1:s}$'.format(cLetterPattern, cHexPattern)
    cCodeMatches = re.findall(cCodePattern, line)
    if ((cCodeMatches is None) or (0 >= len(cCodeMatches))):
        cCodePattern = '{0:s}$'.format(cHexPattern)
        cCodeMatches = re.findall(cHexPattern, line)
        cCode = extractCountryCode(cCodeMatches[-1])
    else:
        cCode = extractCountryCode(re.findall(cHexPattern,cCodeMatches[-1])[-1])

    line = re.sub(cCodePattern, '', line, 1).strip()

    wersPattern = '\s[A-Z 0-9]{5}$'
    wersMatches = re.findall(wersPattern, line)
    if(0 < len(wersMatches)):
        info['wers'] = wersMatches[-1]
        line = re.sub(wersPattern, '', line, 1).strip()
    else:
        info['wers'] = 'N/A'

    info["country"] = line

    zoneId = findZoneId(line, offset)
    info['zone id'] = zoneId

    database[cCode] = info

    print('{0:d}: {1:s}'.format(cCode, str(info)))

OCLASS_NAME = 'DefaultTimezoneMap'
with open('{0:s}.java'.format(OCLASS_NAME), 'w') as fw:
    fw.write('import java.util.HashMap;\n')

    fw.write('public class {0:s} {{\n'.format(OCLASS_NAME))

    fw.write('\tHashMap<Integer, String> Map = new HashMap<Integer, String>();\n')

    fw.write('\tpublic {0:s} () {{\n'.format(OCLASS_NAME))

    for cCode, info in database.items():
        zoneId = info['zone id']
        fw.write('\t\tMap.put({0:d}, "{1:s}");\n'.format(cCode, str(zoneId)))

    fw.write('\t}\n')

    fw.write('}\n')
