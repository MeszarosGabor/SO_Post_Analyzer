for LANGUAGE in  "python" "java" "javascript" "r" "ruby" "rust"
do
  echo "Running ${LANGUAGE}..."
  python3 generate_extracted_import_metadata.py -x -t ${LANGUAGE} -j data/results/${LANGUAGE}/all_${LANGUAGE}_so_posts.jsonl -o data/results/${LANGUAGE}/${LANGUAGE}
  python3 generate_indiv_and_pair_lib_stats.py -i data/results/${LANGUAGE}/${LANGUAGE}_${LANGUAGE}_post_stats.json -o data/results/${LANGUAGE}/${LANGUAGE}
  python3 generate_post_to_new_libs.py -i data/results/${LANGUAGE}/${LANGUAGE}_${LANGUAGE}_post_stats.json -o data/results/${LANGUAGE}/${LANGUAGE}
  echo "\n"
done
