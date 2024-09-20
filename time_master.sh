#!/bin/bash
languages=("python" "r" "javascript" "java" "cpp" "php" "ruby" "perl" "rust" "swift" "objectivec" "c#")
for language in "${languages[@]}"; do
  echo "Doing $language"
  python3 generate_new_time_based_history.py -i data/results/${language}/${language}_${language}_post_stats.json -o data/results/${language}/${language}
  sleep 1
done
