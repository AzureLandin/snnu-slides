out/slides.pdf: slides.tex beamercolorthemesnnu.sty
	# run twice so the table of contents / progress bar renders correctly
	mkdir -p out || mkdir out
	xelatex -interaction=nonstopmode --output-directory=out slides.tex
	xelatex -interaction=nonstopmode --output-directory=out slides.tex

view-xpdf: out/slides.pdf
	xpdf out/slides.pdf & disown

view-okular: out/slides.pdf
	okular out/slides.pdf & disown

view-acroread: out/slides.pdf
	acroread out/slides.pdf & disown

clean:
	rm -rf out
