#读取0000.txt文件的内容，按照第一列的元素进行分类，分别保存到新的txt中
import os
SaveList = []  # 存档列表
n = 446 # 保存的txt个数
nn = 1
with open('./%04d.txt' % nn, 'r') as f:
    #读取所有行
    lines = f.readlines()
    #循环提取一个元素相同的行
    for k in range(n):
        #提取第一列的元素为k的行
        for i in range(len(lines)):
            if lines[i].split()[0] == str(k):
                SaveList.append(lines[i])
        #将提取的行保存到新的txt中
        with open('./%06d.txt' % k, 'a') as f:
            #删除前两列元素
            for i in range(len(SaveList)):
                SaveList[i] = SaveList[i].split()[2:]
                #TypeError: write() argument must be str, not list
                #将列表转换为字符串并换行
                SaveList[i] = ' '.join(SaveList[i])
                f.write(SaveList[i])
                #最后一行不换行
                if i != len(SaveList) - 1:
                    f.write('\n')
            f.close()
        SaveList = []  # 清空存档列表
        print('第{}个txt文件保存成功'.format(k))

    
