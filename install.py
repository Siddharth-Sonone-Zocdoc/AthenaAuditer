import pip
import time

def  install(package):
	pip.main(['install', package])


if __name__ == "__main__":
	install('requests')
	import time.sleep(2)
	install('csv')
	print 'Done'