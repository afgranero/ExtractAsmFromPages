RESULTS="results.txt"

echo "Running tests."| tee $RESULTS
echo | tee $RESULTS
echo "Files containing -j in name will be tested in jsasmplus."| tee $RESULTS
echo "Files containing -z in name will be tested in z80asm."| tee $RESULTS
echo | tee $RESULTS

for FILE in *.asm; do
    echo $FILE
    echo >> $RESULTS
    echo "--------------------------------------------------------------------------" >> $RESULTS
    echo "                              $FILE                               " >> $RESULTS
    echo "--------------------------------------------------------------------------" >> $RESULTS
    echo >> $RESULTS
    cat $FILE >> $RESULTS
    echo >> $RESULTS
    echo >> $RESULTS
    if [[ $FILE == *-j* ]]; then
        echo "---------------------------- Results jasmplus ----------------------------" >> $RESULTS
        echo >> $RESULTS
        sjasmplus --raw=bin/$FILE-jsasmplus.bin $FILE &>> $RESULTS
        echo >> $RESULTS
    fi

    if [[ $FILE == *-z* ]]; then
        echo "---------------------------- Results z80asm -----------------------------" >> $RESULTS
        echo >> $RESULTS
        z80asm --verbose --verbose --output=bin/$FILE-z80asm.bin $FILE &>> $RESULTS
        echo >> $RESULTS
        echo "--------------------------------------------------------------------------" >> $RESULTS
        echo >> $RESULTS
    fi
    echo >> $RESULTS
done

echo 
echo "Results in '$RESULTS'"
echo 
