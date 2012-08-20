# Yet Another Markdown Editor

I hacked this together mostly for personal use, so it is far from perfect!
But feel free to fork and extend :-)

This editor features:

* All features a good editor should have: Keyboard shortcuts, copy, paste, undo, redo, save file,
open file, ...
* GUI with side-to-side edit and preview panel
* Spell checking
* A Tree view which shows the document structure
* Support for MultiMarkdown to get Maths, Tables etc. working
* Export of HTML

A screen shot can be found [here](https://github.com/tmetsch/yame/raw/master/screenshot.png).

## Configuration

Set the absolute path of the Markdown executable in the `default.cfg` file.

## Shortcuts

* Ctrl-C, Ctrl-X and Ctrl-V - the obivous text operations
* Ctrl-N, Ctrl-O and Ctrl-S - New, Open and Save...
* Ctrl+F - Find in text
* Ctrl+T - Toggle Preview
* Ctrl+E - Export HTML file
* Ctrl+Q - Exit

## Requirements

* [PySide](http://www.pyside.org/) (GUI)
* [PyEnchant](http://packages.python.org/pyenchant/) (Spell checking)
* [MultiMarkdown](http://fletcherpenney.net/multimarkdown/) or any other Markdown parser
