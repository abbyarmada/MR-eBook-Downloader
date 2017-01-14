# MR-eBook-Downloader

This program/script should download all avaible ebooks from the german MobileRead wiki (http://wiki.mobileread.com/wiki/Free_eBooks-de/de)  
Dieses Programm/ Skript sollte alle verfügbaren eBooks von der deutschen MobileRead Wikiliste (http://wiki.mobileread.com/wiki/Free_eBooks-de/de) herunterladen.

---  

## Information - *English*
### Installation
Install Python 3 or greater, don't forget to use the correct architecture. (https://www.python.org/downloads/)  
Download and unzip the latest release of this program/ script. (https://github.com/IceflowRE/MR-eBook-Downloader/releases/latest)  
Run `InstallMissingModules.sh`. This will install additional required modules for Python.

### Usage
Run `Start.sh` (Linux) or `Start.bat` (Windows) or **better** run `StartDeDownload.py` from the command line!

### Created data
- `ebook` folder where all ebooks will downloaded.
- `temp` stores the temporary data. At the end this folder should be deleted.  
- `udpate.data` saves data over the downloaded ebooks, do not **deleted!** If you want to update or download the ebooks again it will only download the new ones.
- `noEbookFound.txt` stores a list of threads where no ebook was found.
- `failedDownload.txt` stores a list of links where the download was failed. You can try a manual download, if you succeed you should not forget to add an entry to the update.data file.

### Expert settings
Faster download: edit in `MrDeDownloader.py` the line `using_core = 4`, change the number to a higher count. Have in mind that this will strain your PC and the MR server.  
Download only specific formats: edit in `MrDeDownloader.py` the line `format_list = ['epub', 'mobi', 'lrf', 'imp', 'pdf', 'lit', 'azw', 'azw3', 'rar', 'lrx']`, remove not needed formats.

### Notes
There will be some false positive for examples images or ebooks with wrong extensions e.g. `.pdb` which was a `.epub`.  
Have in mind that you can be banned or something similar if you strained the MR server too much.  

## Information - *Deutsch*
### Installation
Installiere Python 3 oder höher, vergess dabei nicht die richtige Architektur zu wählen. (https://www.python.org/downloads/)  
Downloade und entpacke die letzte Veröffentlichung von dem Downloader. (https://github.com/IceflowRE/MR-eBook-Downloader/releases/latest)  
Führe `InstallMissingModules.sh` aus. Dies wird gegebenenfalls fehlende, benötigte Python Module installieren.  

### Benutzung
Starte `Start.sh` (Linux) oder `Start.bat` (Windows) oder **besser**, starte `StartDeDownload.py` von der Kommandozeile aus.

### Erstellte Daten
- `ebook` der Ordner wohin alle eBooks heruntergeladen werden.
- `temp` speichert temporär benötigte Daten. Diese sollten am Ende jedoch wieder gelöscht werden.  
- `udpate.data` speichert Daten über die heruntergeladenen eBooks, nicht **löschen!** Falls der Donwloader nochmals ausgeführt wird, werden nur neue und aktualisierte eBooks heruntergeladen.
- `noEbookFound.txt` enthält eine List von Threads in welchen keine eBooks gefunden wurden.
- `failedDownload.txt` enthält eine List von Links wo der Download fehlgeschlagen ist. Ein manueller Download kann versucht werden. Sollte dies klappen sollte man den entsprechenden Eintrag in der update.data ergänzen.

### Experteneinstellungen
Schnellerer Download: ändere in der `MrDeDownloader.py` Datei die Zeile `using_core = 4`, zu einer höheren Zahl. Beachte dabei jedoch, dass dies den PC und den MR Server stärker belastet.
Nur bestimmte Formate herunterladen: entferne in der `MrDeDownloader.py` Datei, in der Zeile `format_list = ['epub', 'mobi', 'lrf', 'imp', 'pdf', 'lit', 'azw', 'azw3', 'rar', 'lrx']` die entsprechenden Formate.

### Hinweis
Es werden einige "falsche" Dateien heruntergeladen, beispielsweise Bilder oder Dateien mit einer falschen Dateiendung zum Beispiel `.pdb`, welche aber eine `.epub` darstellt.  
Beachte auch, dass der MR Server stärker belastet wird und ein Ban oder ähnliche Maßnahmen erfolgen können.

---  

## Web
https://github.com/IceflowRE/MR-eBook-Downloader

## Credits
- Developer
  - Iceflower S
- IDE
  - JetBrains PyCharm Community Edition 2016.2.3

##License
![Image of GPLv3](http://www.gnu.org/graphics/gplv3-127x51.png)

Copyright  ©  2016 - 2017  Iceflower S

This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.  
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.  
You should have received a copy of the GNU General Public License along with this program; if not, see <http://www.gnu.org/licenses/gpl.html>.
