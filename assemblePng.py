import zlib
import struct
import os
from PyQt5 import QtCore

cluster_size = 4096
chunk_length_field_size = 4
chunk_type_field_size = 4
chunk_crc_field_size = 4

class Png_fragment:
    def __init__(self):
        self.start_offset = 0               # fragment의 시작 offset
        self.end_offset = 0                 # fragemnt의 끝 offset
        self.up_size = 0                    # fragment의 최상단 IDAT 시그니처 위에 몇 bytes의 IDAT chunk의 data가 존재하는가
        self.down_size = 0                  # fragment의 최하단 IDAT 시그니처 위에 몇 bytes의 IDAT chunk의 data가 존재하는가
        self.bottom_idat_chunk_size = 0     # fragment가 top or middle일 때만 의미가 있는 field
        self.crc = 0                        # fragment가 middle or bottom일 때만 의미가 있는 field
        self.fragment_type = None           # png fragment가 png의 어디 부분인지, 'top' or 'middle' or 'bottom'

    def set_info(self, start_offset, end_offset, up_size, down_size, bottom_idat_chunk_size, crc, fragment_type):
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.up_size = up_size
        self.down_size = down_size
        self.bottom_idat_chunk_size = bottom_idat_chunk_size
        self.crc = crc
        self.fragment_type = fragment_type


def assemble_png(filename, png_header_list, idat_list, png_fragment_list, Qcore):
    '''
    :param filename: dd 파일 path
    :param png_header_list: dd 파일에서 png header의 offsets을 담은 list type 데이터
    :param idat_list: dd 파일에서 idat 시그니처의 offsets을 담은 list type 데이터
    :param png_fragment_list: dd 파일에서 시그니처가 없는 png 데이터가 존재하는 cluster의 offsets을 담은 list type 데이터
    :return: None
    '''

    dd_file_fd = open(filename, 'rb')

    fragment_list = []
    recovery_list = []
    idat_list_len = len(idat_list)
    current_index = 0
    start_index = 0

    while(True):    # idat_list와 png_fragment_list를 기반으로 하여, dd파일에 존재하는 png fragment들을 분석한다. 그 후 fragment_list에 fragment들의 정보를 저장한다
        Qcore.processEvents()

        current_idat_offset = idat_list[current_index]
        start_idat_offset = idat_list[start_index]

        dd_file_fd.seek(current_idat_offset)
        chunk_size = cal_chunk_size(dd_file_fd.read(chunk_length_field_size))

        expected_nextchunk_start_offset = current_idat_offset + chunk_size + chunk_length_field_size + chunk_type_field_size + chunk_crc_field_size

        if current_index + 1 == idat_list_len:
            is_continue = False
        else:
            if expected_nextchunk_start_offset == idat_list[current_index + 1]:
                is_continue = True
            else:
                is_continue = False

        if is_continue:    # idat chunk가 계속 이어질 때
            current_index += 1
        elif (start_idat_offset - (start_idat_offset % cluster_size)) in png_header_list:    # idat chunk가 더이상 이어지지 않아(하나의 fragment를 찾아낸 것) fragment_list에 fragment의 정보를 저장한다, fragment가 top 부분 일 때
            bottom_cluster_offset = current_idat_offset + (cluster_size - (current_idat_offset % cluster_size))

            while True:
                if bottom_cluster_offset in png_fragment_list:
                    bottom_cluster_offset += cluster_size
                else:
                    top_fragment = Png_fragment()
                    top_fragment.set_info(start_idat_offset - (start_idat_offset % cluster_size),
                                          bottom_cluster_offset - 1,
                                          0,
                                          bottom_cluster_offset - (current_idat_offset + chunk_length_field_size + chunk_type_field_size),
                                          chunk_size,
                                          0,
                                          'top')

                    fragment_list.append(top_fragment)
                    break

            current_index += 1
            start_index = current_index
        else:    # fragment가 middle 부분이거나 bottom 부분 일 때
            dd_file_fd.seek(expected_nextchunk_start_offset + chunk_length_field_size)
            expected_nextchunk_sig = dd_file_fd.read(chunk_type_field_size)

            dd_file_fd.seek(start_idat_offset - chunk_crc_field_size)
            crc = dd_file_fd.read(chunk_crc_field_size)

            top_cluster_offset = start_idat_offset - (start_idat_offset % cluster_size)

            if expected_nextchunk_sig == b'IEND':    # fragment가 bottom 부분 일 때
                while True:
                    if (top_cluster_offset - cluster_size) in png_fragment_list:
                        top_cluster_offset -= cluster_size
                    else:
                        end_fragment = Png_fragment()
                        end_fragment.set_info(top_cluster_offset,
                                              expected_nextchunk_start_offset + chunk_length_field_size + chunk_type_field_size + chunk_crc_field_size - 1,
                                              start_idat_offset - top_cluster_offset - chunk_crc_field_size,
                                              0,
                                              0,
                                              crc,
                                              'bottom')

                        fragment_list.append(end_fragment)

                        break

                current_index += 1
                start_index = current_index
            else:    # fragment가 middle 부분 일 때
                bottom_cluster_offset = current_idat_offset + (cluster_size - (current_idat_offset % cluster_size))

                while True:
                    if (top_cluster_offset - cluster_size) in png_fragment_list:
                        top_cluster_offset -= cluster_size
                    else:
                        break

                while True:
                    if bottom_cluster_offset in png_fragment_list:
                        bottom_cluster_offset += cluster_size
                    else:
                        break

                middle_fragment = Png_fragment()
                middle_fragment.set_info(top_cluster_offset,
                                         bottom_cluster_offset - 1,
                                         start_idat_offset - top_cluster_offset - chunk_crc_field_size,
                                         bottom_cluster_offset - (current_idat_offset + chunk_length_field_size + chunk_type_field_size),
                                         chunk_size,
                                         crc,
                                         'middle')

                fragment_list.append(middle_fragment)

                current_index += 1
                start_index = current_index

        if current_index == idat_list_len:
            break

    assembled_png_count = 0
    for png_header_offset in png_header_list:    # png fragment들을 조립하여 하나의 png 파일로 만든다.
        assembled_png = b''
        used_fragment_index_list = []

        for fragment_index, fragment in enumerate(fragment_list):
            if png_header_offset == fragment.start_offset:
                is_completed = False
                while True:
                    required_up_size = fragment.bottom_idat_chunk_size - fragment.down_size

                    for next_fragment_index, next_fragment in enumerate(fragment_list):
                        if required_up_size == next_fragment.up_size:
                            dd_file_fd.seek(fragment.end_offset + 1 - fragment.down_size - chunk_type_field_size)
                            crc_check_target = dd_file_fd.read(fragment.down_size + chunk_type_field_size)

                            dd_file_fd.seek(next_fragment.start_offset)
                            crc_check_target += dd_file_fd.read(next_fragment.up_size)

                            if crc_check(crc_check_target, next_fragment.crc):
                                dd_file_fd.seek(fragment.start_offset)
                                assembled_png += dd_file_fd.read(fragment.end_offset - fragment.start_offset + 1)

                                if next_fragment.fragment_type == 'bottom':
                                    dd_file_fd.seek(next_fragment.start_offset)
                                    assembled_png += dd_file_fd.read(next_fragment.end_offset - next_fragment.start_offset + 1)

                                    used_fragment_index_list.append(fragment_index)
                                    used_fragment_index_list.append(next_fragment_index)
                                    recovery_list.append(assembled_png)

                                    assembled_png_count += 1
                                    is_completed = True
                                    break
                                else:
                                    fragment.set_info(next_fragment.start_offset, next_fragment.end_offset, next_fragment.up_size, next_fragment.down_size, next_fragment.bottom_idat_chunk_size, next_fragment.crc, next_fragment.fragment_type)
                                    used_fragment_index_list.append(fragment_index)
                                    fragment_index = next_fragment_index
                                    break
                    if is_completed:
                        break
                break

        removed_count = 0
        for used_fragment_index in used_fragment_index_list:
            del fragment_list[used_fragment_index - removed_count]
            removed_count += 1
    return recovery_list


def crc_check(target_bytes, crc):
    '''
    :param target_bytes: crc 값이 새로 계산되어야 할 bytes type 데이터
    :param crc: target_bytes로 부터 계산된 crc 값과 비교되어야할 crc 값
    :return: "crc(target_bytes) == crc"이면 True, "crc(target_bytes) == crc"이면 False
    '''

    if zlib.crc32(target_bytes).to_bytes(4, 'big') == crc:
        return True
    else:
        return False


def cal_chunk_size(bytes_data):
    '''
    :param bytes_data: png chunk에서 size를 나타내는 4바이트의 bytes type 데이터
    :return: int형의 png chunk size
    '''
    return struct.unpack('>I', bytes_data)[0]
