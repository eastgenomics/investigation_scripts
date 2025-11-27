#!/usr/bin/env python

import pandas as pd

dataset = pd.read_csv("sex_check_output.tsv", sep="\t")

is_female = (dataset["reported_sex"] == "F")
fail_prod_f = (dataset["score"] < 6.44) 
fail_dev_f = (dataset["score"] < 6.26)

prod_f_outliers = (is_female & fail_prod_f)
dev_f_outliers = (is_female & fail_dev_f)

n_total = dataset.shape[0]
n_dev_fail = dataset[dev_f_outliers].shape[0]
n_prod_fail = dataset[prod_f_outliers].shape[0]

dev_fail_rate = round(100*n_dev_fail/n_total, 2)
prod_fail_rate = round(100*n_prod_fail/n_total, 2)

print(f"Prod fail rate: {n_prod_fail}/{n_total} ({prod_fail_rate}%)")
print(f"Dev fail rate: {n_dev_fail}/{n_total} ({dev_fail_rate}%)")
