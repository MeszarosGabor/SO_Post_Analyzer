#!/bin/bash
languages=("python" "r" "javascript" "java" "cpp" "php" "ruby" "perl" "rust" "swift" "objectivec" "c#")
for language in "${languages[@]}"; do
  echo "Doing $language"
  python3 generate_extracted_import_metadata.py -t $language -x -j data/results/$language/all_${language}_so_posts.jsonl -o data/results/${language}/${language}
  sleep 1
  python3 generate_indiv_and_pair_lib_stats.py -i data/results/${language}/${language}_${language}_post_stats.json -o data/results/${language}/${language}
  sleep 1
done
