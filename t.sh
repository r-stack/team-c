
CP=Sound/bin
for i in Sound/libs/*.jar; do CP="$CP:$i"; done


java -classpath $CP sound.Sound $1 $2

