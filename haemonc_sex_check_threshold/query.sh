#!/bin/bash

## Get JSON file IDs
readarray -t PROJECTS < <(dx find projects --created-after "2025-08-01 00:00:00" --name "*002*MYE*" --brief)
readarray -t FILES < <(for PROJECT in "${PROJECTS[@]}"; do dx find data --project "$PROJECT" --name "*mqc.json" --brief; done)
for FILE in "${FILES[@]}"
do
    dx describe "$FILE" --json | jq -r '.archivalState'
done | sort | uniq -c
printf "%s\n" "${FILES[@]}" | sort -u > file_ids.txt


## Download JSON files
mkdir sex_check_res
cd sex_check_res || exit
xargs -a file_ids.txt -I{} dx download --no-progress {}
cd ..

## Write samples.tsv
for FILE in sex_check_res/*.json;
do
    SAMPLE_NAME=$(basename "$FILE" _mqc.json);
    RUN_NAME=$(cut -f3 -d"-" <<< "$SAMPLE_NAME");
    echo -e "$SAMPLE_NAME\t$RUN_NAME" >> samples.tsv;
done
