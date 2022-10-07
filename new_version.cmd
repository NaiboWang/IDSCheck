rd /s /q dist
rd /s /q build
rd /s /q idscheck.egg-info
python setup.py sdist bdist_wheel
twine upload dist/*