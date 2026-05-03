.PHONY: test sample clean

test:
	python3 -m py_compile scripts/*.py

sample:
	python3 scripts/build_apkg.py --cards examples/cards.sample.json --out example.apkg --deck-name "Example Deck"
	python3 scripts/validate_apkg.py example.apkg

clean:
	rm -rf __pycache__ scripts/__pycache__ .pytest_cache
	rm -f example.apkg
