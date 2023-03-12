for file in *; do mv "$file" `echo $file | tr ' ' '_'`; done
for i in `find . -name "*mp4*"`;do mv $i `echo $i | sed -e 's/(//'`; done
for i in `find . -name "*mp4*"`;do mv $i `echo $i | sed -e 's/)//'`; done