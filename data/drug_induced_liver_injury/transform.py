import pandas as pd
import yaml
from tdc.single_pred import Tox


def get_and_transform_data():
    # get raw data
    splits = Tox(name="DILI").get_split()
    df_train = splits["train"]
    df_valid = splits["valid"]
    df_test = splits["test"]
    df_train["split"] = "train"
    df_valid["split"] = "valid"
    df_test["split"] = "test"
    df = pd.concat([df_train, df_valid, df_test], axis=0)

    fn_data_original = "data_original.csv"
    df.to_csv(fn_data_original, index=False)
    del df

    # create dataframe
    df = pd.read_csv(
        fn_data_original,
        delimiter=",",
    )  # not necessary but ensure we can load the saved data

    # check if fields are the same
    fields_orig = df.columns.tolist()
    assert fields_orig == [
        "Drug_ID",
        "Drug",
        "Y",
        "split",
    ]

    # overwrite column names = fields
    fields_clean = [
        "compound_id",
        "SMILES",
        "liver_injury",
        "split",
    ]
    df.columns = fields_clean

    assert not df.duplicated().sum()

    # save to csv
    fn_data_csv = "data_clean.csv"
    df.to_csv(fn_data_csv, index=False)

    # create meta yaml
    meta = {
        "name": "drug_induced_liver_injury",  # unique identifier, we will also use this for directory names
        "description": """Drug-induced liver injury (DILI) is fatal liver disease caused by drugs
and it has been the single most frequent cause of safety-related drug marketing
withdrawals for the past 50 years (e.g. iproniazid, ticrynafen, benoxaprofen).
This dataset is aggregated from U.S. FDA 2019s National Center for Toxicological
Research.""",
        "targets": [
            {
                "id": "liver_injury",  # name of the column in a tabular dataset
                "description": "whether it can cause liver injury (1) or not (0).",
                "units": None,  # units of the values in this column (leave empty if unitless)
                "type": "boolean",  # can be "categorical", "ordinal", "continuous"
                "names": [  # names for the property (to sample from for building the prompts)
                    {"noun": "liver injury"},
                    {"noun": "drug induced liver injury"},
                    {"noun": "fatal liver disease caused by drugs"},
                    {"noun": "liver toxicity"},
                    {"verb": "injures the liver"},
                    {"verb": "is toxic to the liver"},
                    {"verb": "causes liver injury"},
                ],
                "uris": [
                    "http://purl.bioontology.org/ontology/MEDDRA/10072268",
                    "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C84427",
                ],
            },
        ],
        "benchmarks": [
            {
                "name": "TDC",  # unique benchmark name
                "link": "https://tdcommons.ai/",  # benchmark URL
                "split_column": "split",  # name of the column that contains the split information
            },
        ],
        "identifiers": [
            {
                "id": "SMILES",  # column name
                "type": "SMILES",  # can be "SMILES", "SELFIES", "IUPAC", "Other"
                "description": "SMILES",  # description (optional, except for "Other")
            },
        ],
        "license": "CC BY 4.0",  # license under which the original dataset was published
        "links": [  # list of relevant links (original dataset, other uses, etc.)
            {
                "url": "https://doi.org/10.1021/acs.jcim.5b00238",
                "description": "corresponding publication",
            },
            {
                "url": "https://tdcommons.ai/single_pred_tasks/tox/#dili-drug-induced-liver-injury",
                "description": "Data source",
            },
        ],
        "num_points": len(df),  # number of datapoints in this dataset
        "bibtex": [
            """@article{Xu2015,
doi = {10.1021/acs.jcim.5b00238},
url = {https://doi.org/10.1021/acs.jcim.5b00238},
year = {2015},
month = oct,
publisher = {American Chemical Society (ACS)},
volume = {55},
number = {10},
pages = {2085-2093},
author = {Youjun Xu and Ziwei Dai and Fangjin Chen
and Shuaishi Gao and Jianfeng Pei and Luhua Lai},
title = {Deep Learning for Drug-Induced Liver Injury},
journal = {Journal of Chemical Information and Modeling}""",
        ],
    }

    def str_presenter(dumper, data):
        """configures yaml for dumping multiline strings
        Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data
        """
        if data.count("\n") > 0:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(
        str, str_presenter
    )  # to use with safe_dum
    fn_meta = "meta.yaml"
    with open(fn_meta, "w") as f:
        yaml.dump(meta, f, sort_keys=False)

    print(f"Finished processing {meta['name']} dataset!")


if __name__ == "__main__":
    get_and_transform_data()
