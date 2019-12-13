readme:
	jupyter nbconvert README.ipynb --to markdown
	jupyter nbconvert docs/*.ipynb --to markdown
