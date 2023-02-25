setup : 
	python3.6 setup.py build
	python3.6 setup.py install

TODO: test : 
	./ckhealth/tests/runAllTests.sh

clean some:
	python setup.py clean 
    
clean all:
	python setup.py clean --all bdist_egg
