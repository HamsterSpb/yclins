with open('./names.txt', 'r') as f:
	lns = f.readlines()
	for l in lns:
		fio = l.strip()
		sp = fio.split(" ")
		if len(sp) == 1:
			print sp[0]
		else:
			print('{};{}'.format(sp[0], sp[1]))