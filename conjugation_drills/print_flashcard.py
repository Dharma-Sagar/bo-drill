import textwrap
import re
from collections import defaultdict
from html import escape
from pathlib import Path

from pdf2image import convert_from_bytes

from .latex import LatexMkBuilder


class PrintFlashcard():
    def gen_latex(self, from_roof=None, draw_square=False, font=None):
        header1 = textwrap.dedent("""
                                    \\documentclass{article}
                                    \\usepackage{polyglossia}
                                    \\usepackage{fontspec} 
                                    \\usepackage{tikz-qtree}
                                    
                                    \\newfontfamily\\monlam[Path = """)

        if font:
            header2 = "/resources/]{" + font
        else:
            header2 = "/resources/]{monlam_uni_ouchan2.ttf"
        header2 += textwrap.dedent("""
                                    }
                                    \\newcommand{\\bo}[1]{\\monlam{#1}}
                                    
                                    \\begin{document}
                                    
                                    \\hoffset=-1in
                                    \\voffset=-1in
                                    \\setbox0\hbox{
                                    \\begin{tikzpicture}
                                    \\tikzset{every tree node/.style={align=center,anchor=north, text height=7}}""")
        footer = textwrap.dedent("""
                                    \\end{tikzpicture}
                                            }
                                    \\pdfpageheight=\\dimexpr\\ht0+\\dp0\\relax
                                    \\pdfpagewidth=\\wd0
                                    \\shipout\\box0
                                    
                                    
                                    \\stop""")
        square = textwrap.dedent("""
                                    \\tikzset{edge from parent/.style=
                                    {draw,
                                    edge from parent path={(\\tikzparentnode.south)
                                    -- +(0,-8pt)
                                    -| (\\tikzchildnode)}}}""")

        if from_roof:
            header2 += (
                "\\tikzset{frontier/.style={distance from root="
                + str(from_roof)
                + "pt}}\n"
            )
        if draw_square:
            header2 += square
        document = header1 + str(Path(__file__).parent) + header2 + qtree + footer
        document = document.replace("\\", "\\")
        return document

    def build_png(self, filename, from_roof=None, draw_square=False, font=None):
        source = self.gen_latex(from_roof=from_roof, draw_square=draw_square, font=font)
        bld_cls = lambda: LatexMkBuilder()
        builder = bld_cls()
        pdf = builder.build_pdf(source, [])
        png = convert_from_bytes(bytes(pdf), fmt="png")[0]
        png.save(filename)
