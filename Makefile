fmt:
	black --line-length 150 .
	isort . --treat-comment-as-code "# %%"
