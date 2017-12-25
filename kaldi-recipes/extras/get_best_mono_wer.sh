time=$(date +"%Y-%m-%d %H:%M:%S")
for x in mono*/decode*; do [ -d $x ] && grep WER $x/wer_* | utils/best_wer.sh; \
done | sort -n -r -k2 > RESULTS.mono.$USER.$time
