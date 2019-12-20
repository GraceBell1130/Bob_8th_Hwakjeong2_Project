import os
import sys
from PyQt5 import QtCore

def OrderedSet(list):
    my_set = set()
    res = []
    for e in list:
        if e not in my_set:
            res.append(e)
            my_set.add(e)
    return res

def classifyPng(filename, unallocated, Qcore):
    png_ihdr = b'\x49\x48\x44\x52'  # PNG_IHDR
    png_idat = b'\x49\x44\x41\x54'  # PNG_IDAT
    png_iend = b'\x49\x45\x4E\x44'  # PNG_IEND
    ihdr_list = []
    idat_list = []
    png_frag_list = []
    perfect_png_list = []
    fragment_png_list = []

    with open(filename, "rb") as f:
        for x in unallocated:
            start = x[0]
            end = x[1]
            #클러스터 최소단위를 4096으로 가정하고 진행
            f.seek(start*4096, 0)
            con_count = 0
            for offset in range(end - start):
                Qcore.processEvents()

                #조각화된 파일일 경우 다시 돌아가기 위해서 선언
                len_sum = 0
                #정상적인 파일인 경우 파일 read 포인터가 뒤에 있으므로 로직 패스
                if con_count > 0:
                    con_count -= 1
                    continue
                data = f.read(4096)
                if not data:
                    break
                #ihdr 시그니처 찾기
                check = data.find(png_ihdr)
                if check > -1 and int.from_bytes(data[check-4:check], byteorder='big') < 65535:
                    perfect_png = data
                    #ai로 png 체크 시 불필요한 작업을 줄이기 위해서 사용
                    png_frag_list.append((f.tell() - 4096) // 4096)
                    #idat 시그니처 찾기
                    frag_check = data.find(png_idat)
                    #원래는 4096내에 idat 시그니처가 1개가 아닌 2개가 있다는걸 고려해야 하지만 POC는 무조건 1개가 있다는걸 가정하고 진행하기 때문에 list가 아닌 정수에 저장
                    idat_tmp = f.tell() - 4096 + frag_check - 4
                    while True:
                        if frag_check > -1:
                            length = int.from_bytes(data[frag_check - 4 : frag_check], byteorder='big')

                            if length > 4096 - frag_check and length < 65535:
                                #png는 crc를 포함하기 때문에 4를 더함
                                data = f.read(length + 4)
                                len_sum += length + 4

                                iend = data.find(png_iend)
                                if iend > -1:
                                    if int.from_bytes(data[iend - 4: iend], byteorder='big') == 0:
                                        perfect_png += data[:iend+8]
                                        perfect_png_list.append(perfect_png)
                                        con_count = len_sum//4096
                                        break
                                else:
                                    perfect_png += data
                        else:
                            f.seek(-len_sum,1)
                            #ihdrlist는 클러스터 가장 맨 앞에 있다는걸 가정하였으며 png 시그니처 까지 포함하기 위해서 ihdr시그니처 위치를 저장하지 않았음
                            ihdr_list.append(f.tell() - 4096)
                            fragment_png_list.append(perfect_png)
                            #클러스터단위로 저장을 했으면 필요 없지만 한 클러스내에 ihdr과 idat가 존재하기 때문에 추가 시켜 줌
                            idat_list.append(idat_tmp)
                            break
                        frag_check = data.find(png_idat)
                else:
                    check = data.find(png_idat)
                    if check > -1 and int.from_bytes(data[check - 4:check], byteorder='big') < 65535:
                        # ai로 png 체크 시 불필요한 작업을 줄이기 위해서 사용
                        png_frag_list.append((f.tell() - 4096) // 4096)
                        idat_list.append(f.tell() - 4096 + check - 4)

    return ihdr_list, idat_list, OrderedSet(png_frag_list), perfect_png_list, fragment_png_list
