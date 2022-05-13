fmt:
	black --line-length 150 .
	isort . --treat-comment-as-code "# %%"

notebooks:
	jupytext --update --to notebook plot.py download_threads.py

markdown:
	jupytext --to md plot.py download_threads.py
