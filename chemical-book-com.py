# coding=utf-8

# import sys
import time
import re
import urllib2
from pyquery import PyQuery as pQuery
import xlwt


# # 解决无法写入中文的错误
# reload(sys)
# sys.setdefaultencoding('utf-8')

# 写文件
# fo = open("outcome/detail_with_gold2.html", "wb+")
# fo.write(text)
# fo.close()

# State为时从本地加载（调试用）
running_state = 1


def get_content(uri, state):
    if state == 0:
        fo = open(uri, "r+")
        content = unicode(fo.read(), "utf-8")
        fo.close()
        return content
    else:
        # proxy_support = urllib2.ProxyHandler({'http': 'htp://172.24.13.15:80'})
        # opener = urllib2.build_opener(proxy_support)
        # urllib2.install_opener(opener)
        page = urllib2.urlopen(uri, timeout=60)
        content = unicode(page.read(), "utf-8")
        return content


def get_provider_page_uri(element_num, page_num):
    uri = 'http://www.chemicalbook.com/ProdSupplierGN.aspx?CBNumber=CB' +\
          str(element_num)+'&ProvID=1000&start='+str(page_num)
    return uri


def get_main_info_uri(page_num):
    uri = 'http://www.chemicalbook.com/ProductCASList_12_'+str(page_num)+'00.htm'
    return uri


def get_provider_info(content, element_num):
    total_provider_num = 0
    total_golden_product = 0
    jq_pa = pQuery(content)
    num_arr_html = jq_pa('#ContentPlaceHolder1_ProductSupplier').nextAll()
    num_arr = num_arr_html('font')
    page_num = num_arr.length
    place_holder_1_pa = jq_pa('table.ProdGN_4')
    font_pa = place_holder_1_pa('font')
    font_text_pa = pQuery(font_pa).text()

    total_golden_product = font_text_pa.count(u'黄金产品') + total_golden_product
    total_provider_num = place_holder_1_pa.length + total_provider_num
    if page_num > 1:
        for i_page_num in range(1, page_num):
            url = get_provider_page_uri(element_num, i_page_num)
            # print url
            content = get_content(url, running_state)
            jq = pQuery(content)
            place_holder_1 = jq('table.ProdGN_4')
            font = place_holder_1('font')
            font_text = pQuery(font).text()
            total_golden_product = font_text.count(u'黄金产品') + total_golden_product
            total_provider_num = place_holder_1.length + total_provider_num
        return [total_provider_num, total_golden_product]
    else:
        return [total_provider_num, total_golden_product]


# 获取各元素主要信息
def get_main_info(content):
    # 使用py query解析文本
    jq = pQuery(content)

    # 各元素信息提取
    row_num = 0
    tr = jq('tr')
    for i_tr in tr:
        td = pQuery(i_tr)
        arr = td('td')
        if len(arr) >= 3:
            row_num += 1
            chemical_name = arr('a').eq(0)
            chinese_name = arr('a').eq(1)
            cas = arr('a').eq(2)
            href = str(pQuery(chemical_name).attr['href'])
            element_num = re.findall(r'\d+', href)

            # Element Info
            # print 'Element Num: ' + element_num[0]
            # print 'Chinese Name: ' + pQuery(chinese_name).text()
            # print 'Chemical Name: ' + pQuery(chemical_name).text()
            # print 'CAS: ' + pQuery(cas).text()
            # print 'MF: ' + pQuery(arr('span')).text()

            # Provider Info
            provider_url = get_provider_page_uri(element_num[0], 0)
            provider_content = get_content(provider_url, running_state)
            provider_info = get_provider_info(provider_content, element_num[0])
            # print 'total_provider_num: ' + str(provider_info[0])
            # print 'total_golden_product: ' + str(provider_info[1])
            line_count = row_num
            print 'Line Count: ' + str(line_count)
            ws.write(line_count, 0, pQuery(cas).text())
            ws.write(line_count, 1, pQuery(chinese_name).text())
            ws.write(line_count, 2, pQuery(chemical_name).text())
            ws.write(line_count, 3, pQuery(arr('span')).text())
            ws.write(line_count, 4, int(provider_info[0]))
            ws.write(line_count, 5, int(provider_info[1]))
            line_count += 1            
            

page_num_global = 0
for i_main_page_index in range(141, 200):
    page_num_global = i_main_page_index

    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet1', cell_overwrite_ok=True)
    ws.write(0, 0, u"CAS")
    ws.write(0, 1, u"中文名称")
    ws.write(0, 2, u"英文名称")
    ws.write(0, 3, u"MF")
    ws.write(0, 4, u"供应商数量")
    ws.write(0, 5, u"黄金产品数量")

    print '========= Page: ' + str(i_main_page_index) + " Started ========="
    content_url = get_main_info_uri(i_main_page_index)
    page_content = get_content(content_url, running_state)
    get_main_info(page_content)
    wb.save('output/outcome'+str(page_num_global)+'.xls')
    
