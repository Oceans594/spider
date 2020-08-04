import base64
from fontTools.ttLib import TTFont
import io


def covert_secret_int(yuanma, base64_str):
    # base64解析转换成二进制  下载到本地ttf文件
    ttf = base64.decodebytes(base64_str.encode())
    #   BytesIO把一个二进制文件当成文件来操作
    font = TTFont(io.BytesIO(ttf))
    font.save('58zufang2.ttf')
    font.saveXML('58zufang2.xml')
    # 获取对应关系
    List = font['cmap'].tables[0].ttFont.getGlyphOrder()
    Listkey = font['cmap'].tables[0].ttFont.tables['cmap'].tables[0].cmap

    Table = {}
    for key, value in Listkey.items():
        Table[key] = str(int(value.replace("glyph0000", "").replace("glyph000", "")) - 1)

    real_num = Table.get(yuanma)
    return real_num


# 将字符串中含有加密数字转换成正常数字并返回
def get_result(yuan_str, base64_str):
    yuanma = ""
    for y_index in range(len(yuan_str)):
        num = covert_secret_int(ord(yuan_str[y_index]), base64_str)
        if num is None:
            yuanma += yuan_str[y_index]
        else:
            yuanma += num
    return yuanma