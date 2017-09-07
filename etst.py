import csv
a = {'a':'1','b':'2','c':'3','d':'4'}
print a.items()
with open(r'c:\test2.csv', 'wb') as f:
    writer1 = csv.writer(f)
    writer1.writerows(a.items())