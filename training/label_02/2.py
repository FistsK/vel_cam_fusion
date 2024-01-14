#读取0000.txt文件的内容，按照第一列的元素进行分类，分别保存到新的txt中
import os
n = 446  # 保存的txt个数
for i in range(n):
    os.remove('./%06d.txt' % i)
    print('第{}个txt文件删除成功'.format(i))