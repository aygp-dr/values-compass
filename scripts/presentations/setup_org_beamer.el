;; Set up org-mode with beamer class for presentations
(require 'org)
(require 'ox-latex)

;; Add beamer to org-latex-classes
(add-to-list 'org-latex-classes
  '("beamer"
     "\\documentclass[presentation]{beamer}
      \\usepackage[utf8]{inputenc}
      \\usepackage[T1]{fontenc}
      \\usepackage{graphicx}
      \\usepackage{hyperref}
      \\usepackage{amsmath}
      \\usepackage{minted}
      \\definecolor{codebg}{rgb}{0.95,0.95,0.95}
      \\setminted{bgcolor=codebg,fontsize=\\footnotesize,frame=single}
      \\usepackage{natbib}
      \\bibliographystyle{plainnat}
      \\setbeamertemplate{bibliography item}[text]
      \\usepackage{wrapfig}
      \\usetheme{Frankfurt}
      \\usecolortheme{seahorse}
      \\usefonttheme{structurebold}
      \\setbeamertemplate{navigation symbols}{}
      \\setbeamertemplate{footline}[frame number]
      \\AtBeginSection[]{\\begin{frame}<beamer>\\frametitle{Outline}\\tableofcontents[currentsection]\\end{frame}}"
     ("\\section{%s}" . "\\section*{%s}")
     ("\\subsection{%s}" . "\\subsection*{%s}")
     ("\\subsubsection{%s}" . "\\subsubsection*{%s}")))

;; Set export options
(setq org-latex-pdf-process
      '("pdflatex -shell-escape -interaction nonstopmode -output-directory %o %f"
        "pdflatex -shell-escape -interaction nonstopmode -output-directory %o %f"
        "pdflatex -shell-escape -interaction nonstopmode -output-directory %o %f"))

(setq org-export-with-smart-quotes t)
(setq org-latex-listings 'minted)
(setq org-latex-minted-options '(("fontsize" "\\footnotesize") 
                                 ("frame" "single")
                                 ("bgcolor" "codebg")))

;; Save the updated org-latex-classes
(message "Org-LaTeX classes successfully configured with beamer support.")