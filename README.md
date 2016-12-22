Automates the conversion between .xcf and jpeg / png file formats by hooking into gimp python-fu-eval interpreter.

### How to use

   * Import one png file to gimp's native format
   ```
   python gimpex.py import holiday.png holiday.xcf
   ```

   * Export an xcf file to jpg
   ```
   python gimpex.py export me.xcf me.jpg
   ```

   * Export all xcf files from the working directory to ~/tmp
   ```
   find . -maxdepth 1 -name '*.xcf' -exec realpath {} \; | while read f; do echo '-i ' $f  ' -o ' ~/tmp/$(basename $f .xcf).png; done | xargs -L 100 python gimpex.py export
   ```
