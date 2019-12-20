import binascii
import struct
from PyQt5 import QtCore

vcn = 0

#난중에 사용할 함수
def masterBootRecord(f):
    test=f.read(512)
   #print("Boot code : {0}".format(test[0:446]))
    for x in range(4):
        print("-"*20)
        if x == 0:
            print("system 예약 파티션")
        print("Partition table entry #{0}_Boot Indicator : {1}".format(x+1,"do not use for booting" if test[446+x*16] == 0 else "system partition"))
        print("Partition table entry #{0}_Starting CHS address : {1}".format(x+1,hex(int.from_bytes(test[446+x*16+1:446+x*16+4],byteorder='little'))))
        print("Partition table entry #{0}_Partition type : {1}".format(x+1,hex(test[446+x*16+4])))
        print("Partition table entry #{0}_Ending CHS address : {1}".format(x+1,hex(int.from_bytes(test[446+x*16+5:446+x*16+8],byteorder='little'))))
        print("Partition table entry #{0}_Starting LBA address : {1}".format(x+1,hex(int.from_bytes(test[446+x*16+8:446+x*16+12],byteorder='little'))))
        print("Partition table entry #{0}_Total sectors : {1}".format(x+1,int.from_bytes(test[446+x*16+12:446+x*16+16],byteorder='little')))
        print("-"*20)
    print("Signature : {0}".format(hex(int.from_bytes(test[510:512],byteorder='little'))))
    #첫번째 파티션 return Starting LBA address
    return int.from_bytes(test[446+16+8:446+16+12],byteorder='little') * 512

#VBR 찾는 함수
def ntfsBootRecode(f):
        while True:
            #최소 섹터가 512이므로 512읽음
            test=f.read(512)
            if not test:
                return -1
            #VBR을 찾기 위한 기능
            if str(test[3:11]).find('NTFS') > 0:
                """print("offset : {0}".format(f.tell()-512))
                print("Jump command to boot code : {0}".format(binascii.b2a_hex(test[0:3])))
                print("OEM ID : {0}".format(str(test[3:11])))
                print("Bytes per sector : {0}".format(int.from_bytes(test[11:13],byteorder='little')))
                print("Sectors per cluster : {0}".format(test[13]))
                print("Reserved : {0}".format(int.from_bytes(test[14:16],byteorder='little')))
                print("Always 0 : {0}".format(binascii.b2a_hex(test[16:19])))
                print("Unused : {0}".format(int.from_bytes(test[19:21], byteorder='little')))
                print("Media descriptor : {0}".format(test[21]))
                print("Always 0 : {0}".format(int.from_bytes(test[22:24], byteorder='little')))
                print("Sector per track : {0}".format(int.from_bytes(test[24:26], byteorder='little')))
                print("Number of heads : {0}".format(int.from_bytes(test[26:28],byteorder='little')))
                print("Hidden sectors : {0}".format(int.from_bytes(test[28:32], byteorder='little')))
                print("Unused : {0}".format(int.from_bytes(test[32:36], byteorder='little')))
                print("Unused : {0}".format(int.from_bytes(test[36:40], byteorder='little')))
                print("Total secotrs : {0}".format(int.from_bytes(test[40:48],byteorder='little')))
                print("Logical cluster Number for the file $MFT : {0}".format(int.from_bytes(test[48:56],byteorder='little')))
                print("Logical cluster Number for the file $MFTMirr : {0}".format(int.from_bytes(test[56:64],byteorder='little')))
                print("Clusters per file record segment : {0}".format(int.from_bytes(test[64:68],byteorder='little')))
                print("Clusters per index block : {0}".format(int.from_bytes(test[68:72],byteorder='little')))
                print("Volume serial number : {0}".format(hex(int.from_bytes(test[72:80], byteorder='little'))))
                print("Checksum : {0}".format(int.from_bytes(test[80:84],byteorder='little')))
                print("Signature : {0}".format(hex(int.from_bytes(test[510:512],byteorder='little'))))
                print("======================================================================")"""
                #512을 읽게 되면 그 만큼 뒤로 가기때문에 계산시 안 맞는 경우가 생기므로 포인터?를 앞으로 가져옴
                f.seek(-512,1)
                global vcn
                vcn = f.tell()
                #bytes per sector * cluster * start of MFT == 파일 입출력 최소 단위
                return int.from_bytes(test[11:13],byteorder='little') * test[13] * int.from_bytes(test[48:56],byteorder='little')

def mftEntryHeader(f, mft_offset):
    entry = ['$MFT', '$MFTMirr', '$LogFile', '$Volume', '$AttrDef', '.(Root Directory)', '$Bitmap', '$Boot', '$BadClus', '$Secure', '$Upcase', '$Extend']
    #ntfs를 위해서 read를 더했기 때문에 빼줬음
    #print(mft_offset)
    f.seek(mft_offset,1)
    #entry값은 1024로 대개 고정이므로 1024씩 읽으며 Bitmap으로 바로 가기 위해서 반복문 사용
    for x in range(7):
        test = f.read(1024)
    """print("offset : {0}".format(f.tell() - 1024))
    print("Signature  : {0}".format(str(test[0:4])))
    print("Offset to fixup array : {0}".format(int.from_bytes(test[4:6], byteorder='little')))
    print("Number of entries in fixup array : {0}".format(int.from_bytes(test[6:8], byteorder='little')))
    print("$LogFile Sequence Number (LSN) : {0}".format(int.from_bytes(test[8:16], byteorder='little')))
    print("Sequence Number : {0}".format(int.from_bytes(test[16:18], byteorder='little')))
    print("Link count : {0}".format(int.from_bytes(test[18:20], byteorder='little')))
    print("Offset to first attribute : {0}".format(int.from_bytes(test[20:22], byteorder='little')))
    print("Flags (in-use and directory) : {0}".format(int.from_bytes(test[22:24], byteorder='little')))
    print("Used size of MFT entry : {0}".format(int.from_bytes(test[24:28], byteorder='little')))
    print("Allocated size of MFT Entry : {0}".format(int.from_bytes(test[28:32], byteorder='little')))
    print("File reference to base record : {0}".format(int.from_bytes(test[32:40], byteorder='little')))
    print("Next attribute id : {0}".format(int.from_bytes(test[40:42], byteorder='little')))
    print("Align to 4B boundary : {0}".format(int.from_bytes(test[42:44], byteorder='little')))
    print("Number of this MFT Entry : {0}".format(int.from_bytes(test[44:48], byteorder='little')))
    print("======================================================================")"""
    return test[int.from_bytes(test[20:22], byteorder='little'):]

def attributeHeader(test) :
    """
    attribute = {16 : '$STANDARD_INFORMATION', 32 : '$ATTRIBUTE_LIST', 48 : '$FILE_NAME	', 64 : '$VOLUME_VERSION | $OBJECT_ID', 80 : '$SECURITY_DESCRIPTOR',
                 96 : '$VOLUME_NAME', 112 : '$VOLUME_INFORMATION', 128 : '$DATA', 144 : '$INDEX_ROOT', 160 : '$INDEX_ALLOCATION	',
                 176 : '$BITMAP', 192 : '$SYMBOLIC_LINK | $REPARSE_POINT', 208 : '$EA_INFORMATION', 224 : '$EA', 256 : '$LOGGED_UTILITY_STREAM'}
    print("속성 타입 식별자 : {0}".format(attribute[int.from_bytes(test[0:4], byteorder='little')]))
    print("속성 길이 : {0}".format(int.from_bytes(test[4:8], byteorder='little')))
    print("Non-resident 플래그 : {0}".format(test[8]))
    print("속성 이름 길이 (N) : {0}".format(test[9]))
    print("속성 이름 시작 위치 : {0}".format(int.from_bytes(test[10:12], byteorder='little')))
    print("상태 플래그 : {0}".format(int.from_bytes(test[12:14], byteorder='little')))
    print("속성 식별자 : {0}".format(int.from_bytes(test[14:16], byteorder='little')))
    print('----------------------------------------------------------------------')
    #resident
    if test[8] == 0:
        print("속성 내용 크기 : {0}".format(int.from_bytes(test[16:20], byteorder='little')))
        print("속성 내용 시작 위치 : {0}".format(int.from_bytes(test[20:22], byteorder='little')))
        print("Indexed 플래그 : {0}".format(test[22]))
        print("사용되지 않음: {0}".format(test[23]))
        if test[9] != 0:
            print("속성 이름(유니코드) 단, 이름이 존재할 경우만 사용 : {0}".format(int.from_bytes(test[24:24+(2*test[9]+1)], byteorder='little')))
            print("속성 내용 : {0}".format(int.from_bytes(test[2*test[9]+1:], byteorder='little')))
    #Non-resident
    else :
        print("런리스트 시작 VCN(Virtual Cluster Number) : {0}".format(int.from_bytes(test[16:24], byteorder='little')))
        print("런리스트 끝 VCN : {0}".format(int.from_bytes(test[24:31], byteorder='little')))
        print("런리스트 시작 위치 : {0}".format(int.from_bytes(test[32:34], byteorder='little')))
        print("압축 단위 크기 : {0}".format(int.from_bytes(test[34:36], byteorder='little')))
        print("사용되지 않음 : {0}".format(int.from_bytes(test[36:40], byteorder='little')))
        print("속성 내용 할당 크기(클러스터 크기) : {0}".format(int.from_bytes(test[40:48], byteorder='little')))
        print("속성 내용 실제 크기 : {0}".format(int.from_bytes(test[48:56], byteorder='little')))
        print("속성 내용 초기화된 크기 : {0}".format(int.from_bytes(test[56:64], byteorder='little')))
        if test[9] != 0:
            print("속성 이름(유니코드) 단, 이름이 존재할 경우만 사용 : {0}".format(int.from_bytes(test[64:64+(2*test[9])+1], byteorder='little')))
            print("속성 내용 : {0}".format(int.from_bytes(test[64+(2*test[9])+1:], byteorder='little')))
    print("======================================================================")
    """

    return test[int.from_bytes(test[4:8], byteorder='little'):]

def standardInformation(test):
    """flag = {0x0001:'읽기 전용 (Read Only)',     0x0002 : '숨긴 파일 (Hidden)', 0x0004 : '시스템 (System)', 0x0020 : '아카이브 (Archive)', 0x0040 : '장치 (Device)'
          , 0x0080 : '일반 (Normal)',         0x0100 : '임시 (Temporary)', 0x0200 : 'Sparse 파일', 0x0400 : 'Reparse Point', 0x0800 : '압축됨 (Compressed)'
          , 0x1000 : '오프라인 (Offline)',   0x2000 : '빠른 검색을 위해 인덱스 되지 않은 내용', 0x4000 : '암호화됨 (Encrypted)'}
    print("생성 시간 (Creation time) : {0}".format(int.from_bytes(test[0:8], byteorder='little')))
    print("수정 시간 (Modified time) : {0}".format(int.from_bytes(test[8:16], byteorder='little')))
    print("MFT 수정 시간 (MFT modified time) : {0}".format(int.from_bytes(test[16:24], byteorder='little')))
    print("접근 시간 (Last accessed time) : {0}".format(int.from_bytes(test[24:32], byteorder='little')))
    #수정필요
    print("속성 플래그 (Flags) : {0}".format(int.from_bytes(test[32:36], byteorder='little')))
    print("버전 최대값 (Maximum number of versions) : {0}".format(int.from_bytes(test[36:40], byteorder='little')))
    print("버전 번호 (Version number) : {0}".format(int.from_bytes(test[40:44], byteorder='little')))
    print("클래스 ID (Class ID) : {0}".format(int.from_bytes(test[44:48], byteorder='little')))
    print("소유자 ID (version 3.0+) : {0}".format(int.from_bytes(test[48:52], byteorder='little')))
    print("보안 ID (version 3.0+) : {0}".format(int.from_bytes(test[52:56], byteorder='little')))
    print("Quota Charged (version 3.0+) : {0}".format(int.from_bytes(test[56:64], byteorder='little')))
    print("USN (Update Sequence Number) (version 3.0+) : {0}".format(int.from_bytes(test[64:72], byteorder='little')))
    print("======================================================================")
    """

def fileName(test):
   """
   flag = {0x0001:'읽기 전용 (Read Only)',     0x0002 : '숨긴 파일 (Hidden)', 0x0004 : '시스템 (System)', 0x0020 : '아카이브 (Archive)', 0x0040 : '장치 (Device)'
          , 0x0080 : '일반 (Normal)',         0x0100 : '임시 (Temporary)', 0x0200 : 'Sparse 파일', 0x0400 : 'Reparse Point', 0x0800 : '압축됨 (Compressed)'
          , 0x1000 : '오프라인 (Offline)',   0x2000 : '빠른 검색을 위해 인덱스 되지 않은 내용', 0x4000 : '암호화됨 (Encrypted)', 0x10000000 : '디렉터리'
          , 0x20000000 : '인덱스 뷰'}
    print("부모 디렉터리의 파일 참조 주소 (FileRecordNumber) : {0}".format(int.from_bytes(test[0:6], byteorder='little')))
    print("부모 디렉터리의 파일 참조 주소 (SeqNumber) : {0}".format(int.from_bytes(test[6:8], byteorder='little')))
    print("생성 시간 (Creation time) : {0}".format(int.from_bytes(test[8:16], byteorder='little')))
    print("수정 시간 (Modified time) : {0}".format(int.from_bytes(test[16:24], byteorder='little')))
    print("MFT 수정 시간 (MFT modified time) : {0}".format(int.from_bytes(test[24:32], byteorder='little')))
    print("접근 시간 (Last accessed time) : {0}".format(int.from_bytes(test[32:40], byteorder='little')))
    print("파일 할당 크기 (Allocated size of file) : {0}".format(int.from_bytes(test[40:48], byteorder='little')))
    print("파일 실제 크기 (Real size of file) : {0}".format(int.from_bytes(test[48:56], byteorder='little')))
    print("속성 플래그 (Flags) : {0}".format(int.from_bytes(test[56:60], byteorder='little')))
    print("Reparse 값 (Reparse value) : {0}".format(int.from_bytes(test[60:64], byteorder='little')))
    print("이름 길이 (Length of name) : {0}".format(test[64]))
    print("이름 형식 (Namespace) : {0}".format(test[65]))
    if test[65] == 3:
        print("이름 (Name) : {0}".format(str(test[66:66+(test[64]*2):2])))
    else:
        print("이름 (Name) : {0}".format(str(test[66:66+test[64]])))
    print("======================================================================")
    """

def dataFormat(filename, test, realsize):
    run = test[0:]
    unallocate = []
    count = 0
    while True:
        if ((run[0] & 0xf0) >> 4) + (run[0] & 0x0f) == 0:
            break
        """print("Length Field Size : {0}".format(run[0] & 0x0f))
        print("Offset Field Size : {0}".format((run[0] & 0xf0) >> 4))
        print("Run Length : {0}".format(int.from_bytes(run[1:1 + (run[0] & 0x0f)], byteorder='little')))
        print("LCN offset : {0}".format(int.from_bytes(run[1 + (run[0] & 0x0f) : 1 + (run[0] & 0x0f) + ((run[0] & 0xf0) >> 4)],byteorder='little')))"""
        with open(filename, "rb") as f:
            f.seek(vcn +int.from_bytes(run[1 + (run[0] & 0x0f) : 1 + (run[0] & 0x0f) + ((run[0] & 0xf0) >> 4)],byteorder='little') * 4096)
            datacheck = f.read(int.from_bytes(run[1:1 + (run[0] & 0x0f)], byteorder='little')*4096)
            #print("data : {0}".format(binascii.b2a_hex(datacheck)))
            unallocate = checkCluster(datacheck[:realsize])

            run = test[1+((run[0] & 0xf0) >> 4) + (run[0] & 0x0f):]
    #print("======================================================================")
    return unallocate

def atirtbuteList(test):
    print("속성 타입 식별자 : {0}".format(int.from_bytes(test[0:4], byteorder='little')))
    print("해당엔트리 길이 : {0}".format(int.from_bytes(test[4:6], byteorder='little')))
    print("이름길이 : {0}".format(test[6]))
    print("이름오프셋 : {0}".format(test[7]))
    print("속성 시작 VCN : {0}".format(int.from_bytes(test[8:16], byteorder='little')))
    print("속성이 위치하여 했던 엔트리 : {0}".format(int.from_bytes(test[16:24], byteorder='little')))
    print("속성 ID : {0}".format(test[24]))

def objectId(test):
    print("오브젝트 ID : {0}".format(int.from_bytes(test[0:16], byteorder='little')))
    print("파일이 생성된 볼륨ID : {0}".format(int.from_bytes(test[16:32], byteorder='little')))
    print("파일이 생성될 받은 오브젝트 ID : {0}".format(int.from_bytes(test[32:48], byteorder='little')))
    print("파일이 생성될 받은 도메인 ID : {0}".format(int.from_bytes(test[48:64], byteorder='little')))

def reparsePoint(test):
    print("Reparse 타입 플래그 : {0}".format(int.from_bytes(test[0:4], byteorder='little')))
    print("Reparse 데이터 크기 : {0}".format(int.from_bytes(test[4:6], byteorder='little')))
    print("사용 × : {0}".format(int.from_bytes(test[6:8], byteorder='little')))
    print("대상 이름 오프셋 : {0}".format(int.from_bytes(test[8:10], byteorder='little')))
    print("대상 이름 길이 : {0}".format(int.from_bytes(test[10:12], byteorder='little')))
    print("대상의 출력 이름오프셋 : {0}".format(int.from_bytes(test[12:14], byteorder='little')))
    print("출력 이름 길이 : {0}".format(int.from_bytes(test[14:16], byteorder='little')))


def indexRoot(test):
    print("인텍트 속성 타입 : {0}".format(int.from_bytes(test[0:4], byteorder='little')))
    print("수집 정렬 규칙 : {0}".format(int.from_bytes(test[4:8], byteorder='little')))
    print("인덱스 레코드 크기(byte) : {0}".format(int.from_bytes(test[8:12], byteorder='little')))
    print("인덱스 레코드 크기(클러스터) : {0}".format(test[12]))
    print("사용 x : {0}".format(int.from_bytes(test[13:16], byteorder='little')))
    print("노트 헤더 : {0}".format(str(test[16:])))


def indexAllocation (test):
    print("시그니쳐 : {0}".format(str(test[0:4])))
    print("Fixup 배열 오프셋 : {0}".format(int.from_bytes(test[4:6], byteorder='little')))
    print("Fixup 배열 엔트리 수 : {0}".format(int.from_bytes(test[6:8], byteorder='little')))
    print("$LogFile 순서 번호(LSN) : {0}".format(test[8:16]))
    print("전체 인텍스 스트럼에서 해당 레코드 VCN : {0}".format(int.from_bytes(test[16:24], byteorder='little')))
    print("노트 헤더 : {0}".format(str(test[24:])))

def bitmap (test):
    print("속성 타입 식별자 : {0}".format(int.from_bytes(test[0:4], byteorder='little')))
    print("해당엔트리 길이 : {0}".format(int.from_bytes(test[4:6], byteorder='little')))
    print("이름길이 : {0}".format(test[6]))
    print("이름오프셋 : {0}".format(test[7]))
    print("속성 시작 VCN : {0}".format(int.from_bytes(test[8:16], byteorder='little')))
    print("속성이 위치하여 했던 엔트리 : {0}".format(int.from_bytes(test[16:24], byteorder='little')))
    print("속성 ID : {0}".format(test[24]))

def checkCluster(test):
    count = 0
    firstnum = 0
    endnum = 0
    totalsize = 0
    unallocation = []
    for x in test:
        check = 1
        for y in range(8):
            if x & check == 0 :
                if firstnum == 0 :
                    firstnum = count
            else:
                if endnum == 0 and firstnum > endnum:
                   endnum = count

            if firstnum != 0 and endnum != 0 :
                #print("{0} - {1} 미사용".format(firstnum,endnum) , end=" ")
                unallocation.append((firstnum,endnum))
                if firstnum != endnum:
                    #print("size : {0}".format((endnum - firstnum)*4))
                    totalsize += (endnum - firstnum)*4
                else :
                    #print("size : 4")
                    totalsize += 4
                firstnum = 0
                endnum = 0
            count += 1
            check = check << 1
            #마지막까지 비할당 영역일 경우
            if count == len(test) * 8:
                if firstnum != 0 and endnum == 0:
                    endnum = count
                    #print("{0} - {1} 미사용".format(firstnum, endnum), end=" ")
                    #print("size : {0}".format((endnum - firstnum) * 4))
                    unallocation.append((firstnum, endnum))
                    totalsize += (endnum - firstnum) * 4
    #print(totalsize)
    return unallocation

def unallocatedList(filename, Qcore) :

    with open(filename, "rb") as f:
    #with open("\\\\.\\PHYSICALDRIVE0", "rb") as f:
        return_mft_offset = ntfsBootRecode(f)
        if return_mft_offset == -1:
            return -1
        data = mftEntryHeader(f,return_mft_offset)
        #data속성 찾는 반복문
        while True:
            # 속성이 더 없으면 break
            if int.from_bytes(data[0:4], byteorder='little') == 4294967295:
                break
            data = attributeHeader(data)
            if data[8] == 0:
                if int.from_bytes(data[0:4], byteorder='little') == 16:
                    standardInformation(data[int.from_bytes(data[20:22], byteorder='little'): int.from_bytes(data[20:22],
                                                                                                             byteorder='little') + int.from_bytes(
                        data[16:20], byteorder='little')])
                elif int.from_bytes(data[0:4], byteorder='little') == 48:
                    fileName(data[int.from_bytes(data[20:22], byteorder='little'): int.from_bytes(data[20:22],
                                                                                                  byteorder='little') + int.from_bytes(
                        data[16:20], byteorder='little')])
            else:
                if int.from_bytes(data[0:4], byteorder='little') == 128:
                    unallocated = dataFormat(filename, data[int.from_bytes(data[32:34], byteorder='little'):],
                               int.from_bytes(data[48:56], byteorder='little'))
        #masterBootRecord(f)
        return unallocated
